#!/usr/bin/env python3
import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import Settings
from services.empresa_service import EmpresaService


def main():
    s = Settings()
    svc = EmpresaService(s)
    empresas = svc.buscar_por_cnae('5611-2/01', uf='SP', cidade='São Paulo', limite=5)
    out = []
    for e in empresas:
        out.append({
            'cnpj': e.cnpj_formatado,
            'razao_social': e.razao_social,
            'endereco': e.endereco.to_dict() if e.endereco else None,
            'email': e.email,
            'telefone': e.telefone,
            'cnae': e.cnae_principal.to_dict() if e.cnae_principal else None,
        })
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()


