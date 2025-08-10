#!/usr/bin/env python3
"""
Coletor de bares/restaurantes/botecos em Uberlândia via Google Places
e cruzamento com Nuvem Fiscal (CNAE 5611-2/01), priorizando CNPJ ativo
e contatos completos.

Uso (exemplo):
  python scripts/places_crawler.py --city "Uberlândia" --uf MG --radius 12000 --limit 500 \
    --include restaurante bar boteco choperia petiscos \
    --exclude padaria lanchonete sorveteria cafeteria doceria

Requer:
  - GOOGLE_PLACES_API_KEY no .env
  - Credenciais Nuvem Fiscal no .env (CLIENT_ID/SECRET)
Saída:
  - CSV em data/exports/restaurantes_<city>_<YYYYMMDD_HHMMSS>.csv
"""

import os
import time
import math
import csv
import argparse
import difflib
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

import requests

from src.config.settings import Settings
from src.services.empresa_service import EmpresaService


def textsearch_places(session: requests.Session, api_key: str, query: str, paginated_limit: int = 120) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    next_page: Optional[str] = None
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    for _ in range(5):  # até 5 páginas
        params = {"query": query, "key": api_key, "language": "pt-BR"}
        if next_page:
            params["pagetoken"] = next_page
        r = session.get(base_url, params=params, timeout=30)
        if r.status_code != 200:
            break
        js = r.json()
        results.extend(js.get("results", []))
        next_page = js.get("next_page_token")
        if not next_page or len(results) >= paginated_limit:
            break
        time.sleep(2)  # necessário para token de próxima página
    return results[:paginated_limit]


def get_place_details(session: requests.Session, api_key: str, place_id: str) -> Dict[str, Any]:
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_address,formatted_phone_number,international_phone_number,website,geometry,types",
        "key": api_key,
        "language": "pt-BR",
    }
    r = session.get(url, params=params, timeout=30)
    if r.status_code != 200:
        return {}
    return r.json().get("result", {})


def normalize_phone(raw: Optional[str]) -> str:
    if not raw:
        return ""
    digits = ''.join(ch for ch in raw if ch.isdigit())
    if digits.startswith("55"):
        digits = digits[2:]
    if len(digits) > 11:
        digits = digits[-11:]
    return "+55" + digits if digits else ""


def score_place(name: str, types: List[str], include_kw: Set[str], exclude_kw: Set[str]) -> float:
    nm = (name or "").lower()
    sc = 0.0
    if any(k in nm for k in include_kw):
        sc += 0.5
    if any(k in (types or []) for k in ["restaurant", "bar"]):
        sc += 0.3
    if any(k in nm for k in exclude_kw):
        sc -= 0.6
    return max(0.0, min(1.0, sc))


def fuzzy_match(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="Uberlândia")
    parser.add_argument("--uf", default="MG")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--radius", type=int, default=12000)
    parser.add_argument("--include", nargs="*", default=["restaurante", "bar", "boteco", "choperia", "petiscos"])
    parser.add_argument("--exclude", nargs="*", default=["padaria", "lanchonete", "sorveteria", "cafeteria", "doceria"])
    args = parser.parse_args()

    settings = Settings()
    if not settings.GOOGLE_PLACES_API_KEY:
        print("GOOGLE_PLACES_API_KEY ausente no ambiente")
        return

    session = requests.Session()
    include_kw = set(args.include)
    exclude_kw = set(args.exclude)

    # Queries compostas por keyword + cidade
    queries = [f"{kw} em {args.city} {args.uf}" for kw in include_kw]

    seen_ids: Set[str] = set()
    places: List[Dict[str, Any]] = []
    for q in queries:
        batch = textsearch_places(session, settings.GOOGLE_PLACES_API_KEY, q, paginated_limit=math.ceil(args.limit/len(queries))+20)
        for item in batch:
            pid = item.get("place_id")
            if not pid or pid in seen_ids:
                continue
            seen_ids.add(pid)
            details = get_place_details(session, settings.GOOGLE_PLACES_API_KEY, pid)
            if not details:
                continue
            nm = details.get("name") or item.get("name") or ""
            types = details.get("types") or item.get("types") or []
            sc = score_place(nm, types, include_kw, exclude_kw)
            if sc < 0.4:
                continue
            places.append({
                "place_id": pid,
                "name": nm,
                "address": details.get("formatted_address") or item.get("formatted_address") or "",
                "phone": normalize_phone(details.get("international_phone_number") or details.get("formatted_phone_number")),
                "website": details.get("website") or "",
                "types": types,
                "score": sc,
            })
            if len(places) >= args.limit:
                break
        if len(places) >= args.limit:
            break

    # Cruzamento com Nuvem Fiscal (Uberlândia 3170107) CNAE 5611-2/01
    empresa_service = EmpresaService(settings)
    cnaes_empresas = empresa_service._fazer_busca_nuvem_fiscal(  # type: ignore
        token=empresa_service._obter_token_nuvem_fiscal(),
        cnae='5611201',
        municipio='3170107',
        limite=1000
    ) or []

    # Índices simples por nome
    idx_empresas = [
        {
            "razao": e.razao_social,
            "fantasia": e.nome_fantasia or "",
            "endereco": str(e.endereco) if e.endereco else "",
            "obj": e,
        }
        for e in cnaes_empresas
    ]

    enriched: List[Dict[str, Any]] = []
    for p in places:
        best = (None, 0.0)
        for ee in idx_empresas:
            sim = max(fuzzy_match(p["name"], ee["razao"]), fuzzy_match(p["name"], ee["fantasia"]))
            if sim > best[1]:
                best = (ee, sim)
        row: Dict[str, Any] = {
            "Nome": p["name"],
            "Telefone": p["phone"],
            "Website": p["website"],
            "Endereço (Places)": p["address"],
            "Score Places": p["score"],
        }
        if best[0] and best[1] >= 0.72:  # limiar de match
            e = best[0]["obj"]
            row.update({
                "CNPJ": e.cnpj,
                "Razão Social (NF)": e.razao_social,
                "Nome Fantasia (NF)": e.nome_fantasia or "",
                "Situação": e.situacao_cadastral or "",
                "Email (NF)": e.email or "",
                "Telefone (NF)": e.telefone or "",
                "Endereço (NF)": str(e.endereco) if e.endereco else "",
            })
        enriched.append(row)

    # Ordenar priorizando CNPJ e contatos completos
    def rank_key(r: Dict[str, Any]):
        cnpj = 1 if r.get("CNPJ") else 0
        contacts = sum(1 for k in ["Telefone", "Website", "Email (NF)", "Telefone (NF)"] if r.get(k))
        return (cnpj, contacts, r.get("Score Places", 0.0))

    enriched.sort(key=rank_key, reverse=True)

    # Export CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = settings.EXPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"restaurantes_{args.city.replace(' ', '_')}_{ts}.csv"
    fields = [
        "CNPJ", "Razão Social (NF)", "Nome Fantasia (NF)", "Situação", "Email (NF)", "Telefone (NF)", "Endereço (NF)",
        "Nome", "Telefone", "Website", "Endereço (Places)", "Score Places"
    ]
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in enriched:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"Exportado: {out_path}")


if __name__ == "__main__":
    main()


