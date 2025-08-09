#!/usr/bin/env python3
"""
Teste simples da Nuvem Fiscal (usando variáveis do .env)
"""

import os
import requests
from dotenv import load_dotenv


def test_nuvem_fiscal():
    """Testa autenticação e consulta de CNPJ na Nuvem Fiscal"""

    # Carrega variáveis do .env
    load_dotenv()

    client_id = os.getenv("NUVEM_FISCAL_CLIENT_ID", "")
    client_secret = os.getenv("NUVEM_FISCAL_CLIENT_SECRET", "")
    base_url = os.getenv("NUVEM_FISCAL_BASE_URL", "https://api.nuvemfiscal.com.br")
    auth_url = "https://auth.nuvemfiscal.com.br/oauth/token"

    print("🧪 TESTANDO NUVEM FISCAL")
    print("=" * 50)

    if not client_id or not client_secret:
        print("❌ NUVEM_FISCAL_CLIENT_ID/SECRET não configurados no .env")
        return

    # 1. Obter token
    print("1️⃣ Obtendo token...")
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "cnpj"
        }

        response = requests.post(
            auth_url,
            headers=headers,
            data=data,
            timeout=30
        )

        print(f"Status: {response.status_code}")
        preview = response.text[:200].replace("\n", " ")
        print(f"Response: {preview}...")

        if response.status_code == 200:
            token = response.json().get("access_token", "")
            if not token:
                print("❌ Token não retornado")
                return
            print(f"✅ Token obtido: {token[:20]}...")

            # 2. Testar consulta de CNPJ
            print("\n2️⃣ Testando consulta de CNPJ...")
            cnpj_teste = "00000000000191"  # Petrobras

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            response = requests.get(
                f"{base_url}/cnpj/{cnpj_teste}",
                headers=headers,
                timeout=30
            )

            print(f"Status: {response.status_code}")
            preview = response.text[:200].replace("\n", " ")
            print(f"Response: {preview}...")

            if response.status_code == 200:
                data = response.json()
                razao = data.get("razao_social") or data.get("razao_social_empresa") or "N/A"
                print(f"✅ CNPJ encontrado: {razao}")
            else:
                print(f"❌ Erro na consulta: {response.status_code}")
        else:
            print(f"❌ Erro ao obter token: {response.status_code}")

    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    test_nuvem_fiscal()