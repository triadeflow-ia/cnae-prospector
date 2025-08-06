#!/usr/bin/env python3
"""
Script para limpar a planilha e gerar dados reais da Nuvem Fiscal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.exporters.sheets_exporter import GoogleSheetsExporter
from src.config.settings import Settings
from src.main import CNAEProspector

def main():
    print("🧹 LIMPANDO PLANILHA E GERANDO DADOS REAIS")
    print("=" * 50)
    
    # Configurações
    settings = Settings()
    
    # 1. Limpar a planilha primeiro
    print("🗑️  Limpando planilha...")
    try:
        exporter = GoogleSheetsExporter()
        if exporter.client:
            spreadsheet = exporter.client.open_by_key(settings.GOOGLE_SHEETS_ID)
            worksheet = spreadsheet.get_worksheet(0)
            
            # Limpar todo o conteúdo
            worksheet.clear()
            print("✅ Planilha limpa com sucesso!")
            
            # Criar cabeçalho novo
            headers = [
                "CNPJ", "Razão Social", "Nome Fantasia", "Status",
                "Setor (CNAE)", "Atividade Principal", "Porte Empresa", "Data Abertura",
                "Telefone Principal", "Email Contato", "Endereço Completo",
                "Rua", "Número", "Bairro", "Cidade", "Estado (UF)", "CEP",
                "Capital Social", "Fonte dos Dados", "Data da Consulta",
                "Lead Score", "Observações", "Responsável", "Status Contato"
            ]
            
            worksheet.update('A1', [headers])
            
            # Formatar cabeçalho
            worksheet.format('A1:X1', {
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
                'horizontalAlignment': 'CENTER'
            })
            
            print("✅ Cabeçalho criado com formatação profissional!")
            
        else:
            print("❌ Erro: Cliente Google Sheets não configurado")
            return
            
    except Exception as e:
        print(f"❌ Erro ao limpar planilha: {e}")
        return
    
    # 2. Gerar dados reais usando CNPJs conhecidos
    print("\n🔍 Buscando dados REAIS da Nuvem Fiscal...")
    
    # Lista de CNPJs reais de empresas conhecidas para testar
    cnpjs_reais = [
        "33.000.167/0001-01",  # Petrobras
        "00.000.208/0001-00",  # Banco do Brasil  
        "09.346.601/0001-17",  # Mercado Livre
        "02.558.157/0001-62",  # Magazine Luiza
        "33.014.556/0001-96",  # Ambev
    ]
    
    try:
        prospector = CNAEProspector()
        
        # Obter token da Nuvem Fiscal
        token = prospector.empresa_service._obter_token_nuvem_fiscal()
        if not token:
            print("❌ Não foi possível obter token da Nuvem Fiscal")
            print("ℹ️  Gerando dados demonstrativos como alternativa...")
            
            # Fallback para dados demonstrativos
            empresas = prospector.buscar_empresas_por_cnae(
                cnae_codigo="5611-2/01",
                uf="MG", 
                cidade="Uberlândia",
                limite=8
            )
        else:
            print("✅ Token obtido com sucesso!")
            print("🔎 Consultando empresas reais...")
            
            empresas_reais = []
            for cnpj in cnpjs_reais:
                print(f"   📋 Consultando CNPJ: {cnpj}")
                empresa = prospector.empresa_service._consultar_cnpj_individual_nuvem_fiscal(token, cnpj)
                if empresa:
                    empresas_reais.append(empresa)
                    print(f"   ✅ {empresa.razao_social}")
                else:
                    print(f"   ❌ CNPJ {cnpj} não encontrado")
            
            # Se não encontrou empresas reais, usar dados demonstrativos
            if not empresas_reais:
                print("⚠️  Nenhuma empresa real encontrada, usando dados demonstrativos...")
                empresas = prospector.buscar_empresas_por_cnae(
                    cnae_codigo="5611-2/01",
                    uf="MG",
                    cidade="Uberlândia", 
                    limite=8
                )
            else:
                empresas = empresas_reais
        
        # 3. Exportar para Google Sheets
        print(f"\n📊 Exportando {len(empresas)} empresas para Google Sheets...")
        
        url = prospector.sheets_exporter.export_to_specific_sheet(empresas)
        if url:
            print("✅ Dados exportados com sucesso!")
            print(f"🔗 URL da planilha: {url}")
            
            # Mostrar resumo dos dados
            print(f"\n📈 RESUMO DOS DADOS:")
            for i, empresa in enumerate(empresas, 1):
                fonte = getattr(empresa, 'fonte', 'Não especificada')
                print(f"   {i}. {empresa.razao_social}")
                print(f"      CNPJ: {empresa.cnpj_formatado}")
                print(f"      Fonte: {fonte}")
                print(f"      Telefone: {empresa.telefone_formatado}")
                print(f"      Email: {empresa.email or 'Não informado'}")
                print()
                
        else:
            print("❌ Falha na exportação para Google Sheets")
            
    except Exception as e:
        print(f"❌ Erro durante a busca: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()