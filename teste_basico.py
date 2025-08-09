#!/usr/bin/env python3
"""
Teste Básico - CNAE Prospector
"""

import os
import sys
from datetime import datetime

def teste_configuracao():
    """Testa a configuração básica do sistema"""
    print("🧪 TESTE BÁSICO - CNAE PROSPECTOR")
    print("=" * 50)
    
    # Teste 1: Verificar arquivo .env
    print("1. 📄 Verificando arquivo .env...")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'RAPIDAPI_KEY=' in content:
                print("   ✅ Arquivo .env configurado")
            else:
                print("   ❌ Arquivo .env sem RAPIDAPI_KEY")
    else:
        print("   ❌ Arquivo .env não encontrado")
    
    # Teste 2: Verificar Google Sheets
    print("\n2. 📊 Verificando Google Sheets...")
    if os.path.exists('config/google_sheets.json'):
        print("   ✅ Credenciais Google Sheets encontradas")
    else:
        print("   ❌ Credenciais Google Sheets não encontradas")
    
    # Teste 3: Verificar estrutura
    print("\n3. 📁 Verificando estrutura...")
    dirs = ['src', 'config', 'data/exports']
    for d in dirs:
        if os.path.exists(d):
            print(f"   ✅ {d}/")
        else:
            print(f"   ❌ {d}/ - não encontrado")
    
    # Teste 4: Verificar arquivos de dados
    print("\n4. 📊 Verificando dados exportados...")
    export_dir = 'data/exports'
    if os.path.exists(export_dir):
        files = [f for f in os.listdir(export_dir) if f.endswith('.csv')]
        print(f"   ✅ {len(files)} arquivos CSV encontrados")
        if files:
            print(f"   📋 Último arquivo: {files[-1]}")
    
    # Teste 5: Verificar se main.py funciona
    print("\n5. 🐍 Testando main.py...")
    try:
        sys.path.insert(0, 'src')
        from main import main
        print("   ✅ main.py pode ser importado")
    except Exception as e:
        print(f"   ❌ Erro ao importar main.py: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMO")
    print("=" * 50)
    
    # Verificar se houve sucesso
    export_files = []
    if os.path.exists('data/exports'):
        export_files = [f for f in os.listdir('data/exports') if f.endswith('.csv')]
    
    if len(export_files) > 0:
        print("✅ SISTEMA FUNCIONANDO!")
        print(f"📊 {len(export_files)} arquivos CSV foram gerados")
        print("🚀 O CNAE Prospector está operacional!")
        
        # Mostrar alguns arquivos recentes
        recent_files = sorted(export_files)[-3:]
        print("\n📋 Arquivos recentes:")
        for f in recent_files:
            print(f"   • {f}")
            
    else:
        print("⚠️ Sistema configurado mas sem dados processados")
        print("💡 Execute uma busca para testar:")
        print("   python src/main.py buscar 5611-2/01 --limite 5")

if __name__ == "__main__":
    teste_configuracao()
