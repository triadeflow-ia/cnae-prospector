#!/usr/bin/env python3
"""
Script para gerar planilha com dados reais usando BrasilAPI
"""

import sys
import os
import json
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.exporters.sheets_exporter import GoogleSheetsExporter
from src.config.settings import Settings
from src.models.empresa import Empresa, Endereco, CNAE

def consultar_cnpj_brasil_api(cnpj):
    """Consulta CNPJ na BrasilAPI"""
    try:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def converter_dados_brasil_api_para_empresa(dados_api, cnpj):
    """Converte dados da BrasilAPI para nosso modelo Empresa"""
    try:
        # Endereço
        endereco = Endereco(
            logradouro=dados_api.get('logradouro', ''),
            numero=dados_api.get('numero', ''),
            complemento=dados_api.get('complemento', ''),
            bairro=dados_api.get('bairro', ''),
            cidade=dados_api.get('municipio', ''),
            uf=dados_api.get('uf', ''),
            cep=dados_api.get('cep', '')
        )
        
        # CNAE Principal
        cnae_codigo = dados_api.get('cnae_fiscal', '')
        cnae_descricao = dados_api.get('cnae_fiscal_descricao', '')
        
        cnae_principal = CNAE(
            codigo=cnae_codigo,
            descricao=cnae_descricao,
            principal=True
        )
        
        # Sócios (simplificado)
        socios = []
        qsa = dados_api.get('qsa', [])
        for socio_data in qsa[:2]:  # Máximo 2 sócios
            socio = {
                'nome': socio_data.get('nome_socio', ''),
                'qualificacao': socio_data.get('qualificacao_socio', ''),
                'cpf': 'Não divulgado'
            }
            socios.append(socio)
        
        # Empresa
        empresa = Empresa(
            cnpj=cnpj,
            razao_social=dados_api.get('razao_social', ''),
            nome_fantasia=dados_api.get('nome_fantasia', '') or dados_api.get('razao_social', ''),
            situacao_cadastral=dados_api.get('descricao_situacao_cadastral', 'ATIVA'),
            data_abertura=datetime.strptime(dados_api.get('data_inicio_atividade', '2020-01-01'), '%Y-%m-%d') if dados_api.get('data_inicio_atividade') else datetime(2020, 1, 1),
            porte=dados_api.get('porte', 'Não informado'),
            natureza_juridica=dados_api.get('natureza_juridica', ''),
            cnae_principal=cnae_principal,
            endereco=endereco,
            socios=socios,
            telefone=dados_api.get('ddd_telefone_1', ''),
            email=dados_api.get('email', '')
        )
        
        # Marcar como dados reais
        empresa.fonte = "BrasilAPI - Dados Reais"
        
        return empresa
        
    except Exception as e:
        print(f"❌ Erro ao converter dados: {e}")
        return None

def main():
    print("🚀 GERANDO PLANILHA COM DADOS REAIS")
    print("=" * 50)
    
    # CNPJs reais que sabemos que funcionam
    cnpjs_reais = [
        "11.222.333/0001-81",  # Caixa Escolar
        "07.526.557/0001-00",  # Ambev
        "33.000.167/0001-01",  # Petrobras  
        "00.000.000/0001-91",  # Banco do Brasil
        "34.073.394/0001-84",  # Teste adicional
        "42.291.751/0001-01",  # Teste adicional
    ]
    
    print("🔍 Consultando empresas reais...")
    empresas_reais = []
    
    for cnpj in cnpjs_reais:
        print(f"   📋 Consultando {cnpj}...")
        dados = consultar_cnpj_brasil_api(cnpj)
        
        if dados:
            empresa = converter_dados_brasil_api_para_empresa(dados, cnpj)
            if empresa:
                empresas_reais.append(empresa)
                print(f"   ✅ {empresa.razao_social}")
            else:
                print(f"   ❌ Erro na conversão")
        else:
            print(f"   ❌ Não encontrado")
    
    if not empresas_reais:
        print("❌ Nenhuma empresa real encontrada!")
        return
    
    print(f"\n✅ {len(empresas_reais)} empresas reais encontradas!")
    
    # Limpar e popular planilha
    print("\n🧹 Limpando planilha...")
    try:
        settings = Settings()
        exporter = GoogleSheetsExporter()
        
        if not exporter.client:
            print("❌ Erro: Cliente Google Sheets não configurado")
            return
        
        # Limpar planilha
        spreadsheet = exporter.client.open_by_key(settings.GOOGLE_SHEETS_ID)
        worksheet = spreadsheet.get_worksheet(0)
        worksheet.clear()
        
        print("✅ Planilha limpa!")
        
        # Exportar dados reais
        print("📊 Exportando dados reais...")
        url = exporter.export_to_specific_sheet(empresas_reais, clear_first=False)
        
        if url:
            print("✅ Dados reais exportados com sucesso!")
            print(f"🔗 URL: {url}")
            
            print(f"\n📈 RESUMO DAS EMPRESAS REAIS:")
            for i, empresa in enumerate(empresas_reais, 1):
                print(f"   {i}. {empresa.razao_social}")
                print(f"      CNPJ: {empresa.cnpj_formatado}")
                print(f"      CNAE: {empresa.cnae_principal.codigo} - {empresa.cnae_principal.descricao}")
                print(f"      Cidade: {empresa.endereco.cidade}/{empresa.endereco.uf}")
                print(f"      Fonte: {empresa.fonte}")
                print()
        else:
            print("❌ Erro na exportação")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()