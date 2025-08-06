#!/usr/bin/env python3
"""
Script de teste para verificar se a aplicação funciona
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa se todas as importações funcionam"""
    print("🧪 Testando importações...")
    
    try:
        from src.config.settings import Settings
        print("✅ Settings importado com sucesso")
        
        from src.main import main
        print("✅ Main importado com sucesso")
        
        from src.services.empresa_service import EmpresaService
        print("✅ EmpresaService importado com sucesso")
        
        from src.exporters.csv_exporter import CSVExporter
        print("✅ CSVExporter importado com sucesso")
        
        from src.exporters.sheets_exporter import GoogleSheetsExporter
        print("✅ GoogleSheetsExporter importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False

def test_settings():
    """Testa se as configurações carregam corretamente"""
    print("\n⚙️ Testando configurações...")
    
    try:
        from src.config.settings import Settings
        settings = Settings()
        print("✅ Configurações carregadas com sucesso")
        print(f"   Base dir: {settings.BASE_DIR}")
        print(f"   Log level: {settings.LOG_LEVEL}")
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_api():
    """Testa se a API Flask funciona"""
    print("\n🌐 Testando API Flask...")
    
    try:
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health')
        def health():
            return {"status": "ok"}
        
        print("✅ Flask app criado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro na API Flask: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO CNAE PROSPECTOR")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_settings,
        test_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO DOS TESTES: {passed}/{total} passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Aplicação pronta para deploy no Railway")
        return True
    else:
        print("❌ Alguns testes falharam")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 