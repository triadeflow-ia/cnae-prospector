#!/usr/bin/env python3
"""
Teste simples da Nuvem Fiscal
"""

import requests
import json

def test_nuvem_fiscal():
    """Testa a API da Nuvem Fiscal"""
    
    # Credenciais
    client_id = "zzsrxuTxRs45amfnDXEW"
    client_secret = "H8qjMksiafkY49UTcPruR1ceZKcUJylEOHXkvcDr"
    
    print("🧪 TESTANDO NUVEM FISCAL")
    print("=" * 50)
    
    # 1. Obter token
    print("1️⃣ Obtendo token...")
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'cnpj'
        }
        
        response = requests.post(
            "https://auth.nuvemfiscal.com.br/oauth/token",
            headers=headers,
            data=data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"✅ Token obtido: {token[:20]}...")
            
            # 2. Testar consulta de CNPJ
            print("\n2️⃣ Testando consulta de CNPJ...")
            cnpj_teste = "00000000000191"  # Petrobras
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                f"https://api.nuvemfiscal.com.br/cnpj/{cnpj_teste}",
                headers=headers,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ CNPJ encontrado: {data.get('razao_social', 'N/A')}")
            else:
                print(f"❌ Erro na consulta: {response.status_code}")
                
        else:
            print(f"❌ Erro ao obter token: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_nuvem_fiscal() 