#!/usr/bin/env python3
"""
Script para testar CNPJs reais usando BrasilAPI
"""

import requests
import json
from datetime import datetime

def consultar_cnpj_brasil_api(cnpj):
    """Consulta CNPJ na BrasilAPI (gratuita)"""
    try:
        # Limpar CNPJ (apenas números)
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ CNPJ {cnpj} não encontrado: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao consultar {cnpj}: {e}")
        return None

def main():
    print("🔍 TESTANDO CNPJs REAIS COM BRASILAPI")
    print("=" * 50)
    
    # Lista de CNPJs conhecidos (menores empresas que devem estar na base)
    cnpjs_teste = [
        "11.222.333/0001-81",  # Fictício para teste
        "34.028.316/0001-96",  # Real - possível empresa
        "07.526.557/0001-00",  # Real - possível empresa
        "33.000.167/0001-01",  # Petrobras
        "00.000.000/0001-91",  # Banco do Brasil
    ]
    
    empresas_encontradas = []
    
    for cnpj in cnpjs_teste:
        print(f"\n📋 Testando CNPJ: {cnpj}")
        
        dados = consultar_cnpj_brasil_api(cnpj)
        
        if dados:
            print(f"✅ Encontrado: {dados.get('razao_social', 'N/A')}")
            print(f"   CNAE Principal: {dados.get('cnae_fiscal', 'N/A')}")
            print(f"   Situação: {dados.get('situacao_cadastral', 'N/A')}")
            print(f"   Cidade: {dados.get('municipio', 'N/A')}/{dados.get('uf', 'N/A')}")
            
            empresas_encontradas.append({
                'cnpj': cnpj,
                'dados': dados
            })
    
    print(f"\n📊 RESUMO: {len(empresas_encontradas)} empresas reais encontradas")
    
    if empresas_encontradas:
        print("\n💾 Salvando dados encontrados...")
        with open('cnpjs_reais_encontrados.json', 'w', encoding='utf-8') as f:
            json.dump(empresas_encontradas, f, ensure_ascii=False, indent=2)
        print("✅ Dados salvos em 'cnpjs_reais_encontrados.json'")
    
    return empresas_encontradas

if __name__ == "__main__":
    main()