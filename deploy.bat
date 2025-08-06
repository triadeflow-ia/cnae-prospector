@echo off
REM CNAE Prospector - Script de Deploy para Windows

echo 🚀 INICIANDO DEPLOY DO CNAE PROSPECTOR
echo ======================================

REM Verificar se Docker está instalado
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não encontrado!
    echo 📥 Baixe e instale o Docker Desktop: https://docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Verificar se .env existe
if not exist .env (
    echo ⚠️ Arquivo .env não encontrado!
    if exist .env.example (
        echo ℹ️ Copiando .env.example para .env...
        copy .env.example .env
        echo ⚠️ CONFIGURE suas credenciais reais no arquivo .env!
        echo ℹ️ Configure pelo menos:
        echo   - NUVEM_FISCAL_CLIENT_ID
        echo   - NUVEM_FISCAL_CLIENT_SECRET  
        echo   - GOOGLE_SHEETS_ID
        pause
    ) else (
        echo ❌ Arquivo .env.example não encontrado!
        pause
        exit /b 1
    )
)

REM Criar diretórios
echo ℹ️ Criando estrutura de diretórios...
if not exist data\exports mkdir data\exports
if not exist data\processed mkdir data\processed
if not exist data\raw mkdir data\raw
if not exist logs mkdir logs

REM Build da aplicação
echo ℹ️ Construindo aplicação...
docker-compose build

REM Parar containers existentes
echo ℹ️ Parando containers existentes...
docker-compose down 2>nul

REM Iniciar aplicação
echo ℹ️ Iniciando aplicação...
docker-compose up -d

REM Aguardar inicialização
echo ℹ️ Aguardando inicialização...
timeout /t 10 /nobreak >nul

REM Verificar status
echo ℹ️ Verificando status...
docker-compose ps

echo.
echo 🎉 DEPLOY CONCLUÍDO!
echo ===================
echo ✅ Aplicação disponível em: http://localhost:8000
echo ℹ️ Para ver logs: docker-compose logs -f
echo ℹ️ Para parar: docker-compose down
echo.
echo 📖 Documentação: docs\DEPLOY_GUIDE.md
pause