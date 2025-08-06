#!/usr/bin/env python3
"""
Script para preparar o projeto para deploy no Railway
"""

import os
import json

def main():
    print("🚀 PREPARANDO PROJETO PARA RAILWAY")
    print("=" * 40)
    
    # 1. Verificar arquivos necessários
    files_needed = [
        'requirements.txt',
        'Procfile', 
        'run_production.py',
        '.env.example'
    ]
    
    print("📋 Verificando arquivos necessários...")
    for file in files_needed:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - FALTANDO!")
    
    # 2. Verificar se git está inicializado
    print("\n📁 Verificando Git...")
    if os.path.exists('.git'):
        print("   ✅ Repositório Git inicializado")
    else:
        print("   ⚠️  Git não inicializado - Execute:")
        print("      git init")
        print("      git add .")
        print("      git commit -m 'Initial commit'")
    
    # 3. Mostrar configurações para Railway
    print("\n⚙️ CONFIGURAÇÕES PARA RAILWAY:")
    print("=" * 40)
    
    env_vars = {
        "NUVEM_FISCAL_CLIENT_ID": "XvvT85IC3PzNNeNrOIR6",
        "NUVEM_FISCAL_CLIENT_SECRET": "lClvhEuEuaJ4bZrCUcPjmgq6P6OZdccSjjp9pbXW", 
        "NUVEM_FISCAL_BASE_URL": "https://api.nuvemfiscal.com.br",
        "GOOGLE_SHEETS_ID": "1ecOvpQfR0venrB4RcFCm6ta5IngygSkeJUN_IEKubQY",
        "PRODUCTION": "true",
        "LOG_LEVEL": "INFO"
    }
    
    print("Copie e cole estas variáveis no Railway:")
    print()
    for key, value in env_vars.items():
        print(f"{key}={value}")
    
    # 4. Instruções de deploy
    print("\n🎯 PASSOS PARA DEPLOY NO RAILWAY:")
    print("=" * 40)
    print("1. Acesse: https://railway.app")
    print("2. Clique em 'New Project'")
    print("3. Selecione 'Deploy from GitHub repo'")
    print("4. Escolha este repositório")
    print("5. Vá em 'Variables' e adicione as variáveis acima")
    print("6. O deploy iniciará automaticamente!")
    
    # 5. Comandos úteis
    print("\n🔧 COMANDOS ÚTEIS:")
    print("=" * 40)
    print("# Se ainda não commitou:")
    print("git add .")
    print("git commit -m 'feat: prepare for railway deployment'")
    print("git push origin main")
    print()
    print("# Para testar localmente:")
    print("python run_production.py --api")
    print("# Acesse: http://localhost:8000")
    
    # 6. URL final
    print("\n🌐 URL FINAL:")
    print("=" * 40)
    print("Após o deploy, sua aplicação estará em:")
    print("https://seu-projeto.up.railway.app")
    print()
    print("Endpoints disponíveis:")
    print("• Interface Web: https://seu-projeto.up.railway.app")  
    print("• API Health: https://seu-projeto.up.railway.app/health")
    print("• API Search: https://seu-projeto.up.railway.app/api/search")
    
    print("\n✅ PROJETO PRONTO PARA RAILWAY!")

if __name__ == "__main__":
    main()