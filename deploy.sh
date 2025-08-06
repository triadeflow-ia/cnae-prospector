#!/bin/bash
# CNAE Prospector - Script de Deploy Automatizado

set -e

echo "🚀 INICIANDO DEPLOY DO CNAE PROSPECTOR"
echo "======================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não encontrado! Instalando..."
    
    # Instalar Docker (Ubuntu/Debian)
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    print_status "Docker instalado com sucesso!"
    print_warning "Você precisa fazer logout/login para usar Docker sem sudo"
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não encontrado! Instalando..."
    
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_status "Docker Compose instalado com sucesso!"
fi

# Verificar se .env existe
if [ ! -f .env ]; then
    print_warning "Arquivo .env não encontrado!"
    
    if [ -f .env.example ]; then
        print_info "Copiando .env.example para .env..."
        cp .env.example .env
        print_warning "ATENÇÃO: Configure suas credenciais reais no arquivo .env antes de continuar!"
        print_info "Abra o arquivo .env e configure:"
        echo "  - NUVEM_FISCAL_CLIENT_ID"
        echo "  - NUVEM_FISCAL_CLIENT_SECRET"
        echo "  - GOOGLE_SHEETS_ID"
        echo ""
        read -p "Pressione Enter após configurar o .env..."
    else
        print_error "Arquivo .env.example não encontrado!"
        exit 1
    fi
fi

# Criar diretórios necessários
print_info "Criando estrutura de diretórios..."
mkdir -p data/exports data/processed data/raw logs ssl

# Verificar se as credenciais estão configuradas
print_info "Verificando configurações..."

if grep -q "your_client_id_here" .env; then
    print_warning "Credenciais ainda não configuradas no .env!"
    print_info "Configure pelo menos as credenciais da Nuvem Fiscal ou Google Sheets"
fi

# Build da aplicação
print_info "Construindo imagem Docker..."
docker-compose build

# Parar containers existentes
print_info "Parando containers existentes..."
docker-compose down 2>/dev/null || true

# Iniciar aplicação
print_info "Iniciando aplicação..."
docker-compose up -d

# Aguardar inicialização
print_info "Aguardando inicialização..."
sleep 10

# Verificar status
print_info "Verificando status dos containers..."
docker-compose ps

# Verificar se a aplicação está respondendo
print_info "Testando aplicação..."
if curl -s http://localhost:8000/health > /dev/null; then
    print_status "Aplicação está rodando com sucesso!"
else
    print_warning "Aplicação pode estar ainda inicializando..."
fi

# Mostrar logs
print_info "Últimas linhas do log:"
docker-compose logs --tail=20 cnae-prospector

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "==================="
print_status "Aplicação disponível em: http://localhost:8000"
print_info "Para ver logs em tempo real: docker-compose logs -f"
print_info "Para parar a aplicação: docker-compose down"
print_info "Para atualizar: git pull && ./deploy.sh"

echo ""
print_warning "PRÓXIMOS PASSOS:"
echo "1. Configurar domínio (se necessário)"
echo "2. Configurar SSL/HTTPS"
echo "3. Configurar backup automático"
echo "4. Configurar monitoramento"

echo ""
print_info "Documentação completa: docs/DEPLOY_GUIDE.md"