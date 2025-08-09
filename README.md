# 🎯 CNAE Prospector - B2B Lead Generation Tool

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-MVP-orange.svg)

## 📋 Sobre o Projeto

O **CNAE Prospector** é uma ferramenta profissional de prospecção B2B que automatiza a busca e organização de leads através de códigos CNAE (Classificação Nacional de Atividades Econômicas). 

### 🚀 Principais Funcionalidades

- **🔍 Busca Inteligente**: Encontre empresas por CNAE, cidade e estado
- **📊 Integração Google Sheets**: Exportação automática para planilhas organizadas
- **🎯 Lead Scoring**: Classificação automática de potencial dos leads
- **📁 Múltiplos Formatos**: Exportação em CSV e Excel
- **🔄 Fonte Principal**: Integração com Nuvem Fiscal (BrasilAPI usada apenas como fallback para completar endereço)
- **📱 Interface CLI**: Linha de comando intuitiva para automação

## 🏗️ Arquitetura

```
cnae-prospector/
├── src/
│   ├── config/          # Configurações e constantes
│   ├── services/        # Lógica de negócio e APIs
│   ├── models/          # Modelos de dados
│   ├── exporters/       # Exportadores (CSV, Excel, Sheets)
│   └── utils/           # Utilitários e helpers
├── data/
│   ├── exports/         # Arquivos exportados
│   ├── processed/       # Dados processados
│   └── raw/            # Dados brutos
├── config/             # Arquivos de configuração
└── docs/              # Documentação
```

## ⚡ Instalação Rápida

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/cnae-prospector.git
cd cnae-prospector
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## 🔧 Configuração

### APIs Suportadas

1. **Nuvem Fiscal** (Recomendado e utilizado)
   - Acesse: [Nuvem Fiscal](https://nuvemfiscal.com.br)
   - Obtenha: `CLIENT_ID` e `CLIENT_SECRET`

2. **BrasilAPI** (fallback gratuito para enriquecimento de endereço)
   - Sem necessidade de configuração (usada automaticamente quando faltar endereço)

### Google Sheets (Opcional)

Para integração com Google Sheets:

1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Crie um projeto e ative a API do Google Sheets
3. Crie uma conta de serviço e baixe o arquivo JSON
4. Salve como `config/google_sheets.json`
5. Compartilhe sua planilha com o email da conta de serviço

## 🎮 Como Usar

### Linha de Comando

```bash
# Busca básica por CNAE
python run_production.py --cnae "5611-2/01" --limite 50

# Busca com filtros geográficos
python run_production.py --cnae "5611-2/01" --uf "SP" --cidade "São Paulo" --limite 100

# Exportar para Google Sheets
python run_production.py --cnae "5611-2/01" --uf "MG" --cidade "Uberlândia" --sheets

# Formato Excel
python run_production.py --cnae "5611-2/01" --formato excel --limite 30
```

### Interface Programática

```python
from src.main import CNAEProspector

# Inicializar
prospector = CNAEProspector()

# Buscar empresas
empresas = prospector.buscar_empresas_por_cnae(
    cnae_codigo="5611-2/01",
    uf="SP",
    cidade="São Paulo",
    limite=100
)

# Exportar resultados
arquivo = prospector.exportar_resultados(
    empresas=empresas,
    formato="csv",
    exportar_sheets=True
)
```

## 📊 Formato dos Dados

O sistema exporta dados estruturados para CRM com os seguintes campos:

| Campo | Descrição |
|-------|-----------|
| CNPJ | Número do CNPJ formatado |
| Razão Social | Nome empresarial oficial |
| Nome Fantasia | Nome comercial |
| Status | Situação cadastral |
| Setor (CNAE) | Código da atividade |
| Atividade Principal | Descrição da atividade |
| Telefone Principal | Contato telefônico |
| Email Contato | Email empresarial |
| Endereço Completo | Endereço formatado |
| Lead Score | Pontuação de potencial |
| Observações | Campo livre para CRM |
| Responsável | Campo livre para CRM |
| Status Contato | Campo livre para CRM |

## 🎯 CNAEs Populares

| Código | Descrição |
|--------|-----------|
| 5611-2/01 | Restaurantes e similares |
| 4712-1/00 | Comércio varejista de mercadorias em geral |
| 7020-4/00 | Atividades de consultoria em gestão empresarial |
| 6201-5/01 | Desenvolvimento de programas de computador |
| 4541-2/05 | Comércio por atacado de produtos farmacêuticos |

## 🔐 Segurança

- ✅ Variáveis de ambiente para credenciais
- ✅ Rate limiting nas APIs
- ✅ Logs detalhados para auditoria
- ✅ Validação de entrada de dados

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📈 Roadmap

### Versão 1.1
- [ ] Interface web com dashboard
- [ ] Integração com CRMs populares (HubSpot, Salesforce)
- [ ] Análise de sentimento dos dados
- [ ] Relatórios avançados

### Versão 1.2
- [ ] API REST completa
- [ ] Webhook para atualizações automáticas
- [ ] Machine Learning para scoring
- [ ] Integração com WhatsApp Business

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Alex Campos** - *Desenvolvimento inicial* - [@alexcampos](https://github.com/alexcampos)

## 📞 Suporte

- 📧 Email: suporte@cnaeprospector.com
- 💬 Issues: [GitHub Issues](https://github.com/seu-usuario/cnae-prospector/issues)
- 📖 Docs: [Documentação Completa](https://docs.cnaeprospector.com)

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!**

[![GitHub stars](https://img.shields.io/github/stars/seu-usuario/cnae-prospector.svg?style=social&label=Star)](https://github.com/seu-usuario/cnae-prospector)