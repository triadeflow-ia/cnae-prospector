# 🚀 GUIA DE PRODUÇÃO - CNAE PROSPECTOR

## 📋 CHECKLIST PARA PRODUÇÃO

### 1. 🔑 CONFIGURAR API RAPIDAPI

**Passos:**
1. Acesse: https://rapidapi.com/psfdev/api/empresas-brasil
2. Faça login na sua conta
3. Vá em "Pricing" e escolha um plano pago:
   - **Basic**: $9.99/mês - 1000 requests/mês
   - **Pro**: $29.99/mês - 5000 requests/mês
   - **Ultra**: $99.99/mês - 20000 requests/mês
4. Copie a nova chave da API
5. Edite o arquivo `.env` e substitua:
   ```
   RAPIDAPI_KEY=sua_nova_chave_aqui
   ```

### 2. 📊 CONFIGURAR GOOGLE SHEETS

**Passos:**
1. **Criar projeto no Google Cloud:**
   - Acesse: https://console.cloud.google.com/
   - Clique em "Select a project" > "New Project"
   - Digite um nome (ex: "CNAE-Prospector")
   - Clique em "Create"

2. **Ativar APIs:**
   - Vá em "APIs & Services" > "Library"
   - Procure e ative:
     - Google Sheets API
     - Google Drive API

3. **Criar credenciais:**
   - Vá em "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "Service Account"
   - Digite um nome (ex: "cnae-prospector")
   - Clique em "Create and Continue"
   - Pule as etapas de permissões
   - Clique em "Done"

4. **Baixar credenciais:**
   - Clique no service account criado
   - Vá na aba "Keys"
   - Clique em "Add Key" > "Create new key"
   - Escolha "JSON"
   - Baixe o arquivo

5. **Salvar/Configurar credenciais:**
   - Opção A (dev): renomeie o arquivo para `google_sheets.json` e mova para a pasta `config/`
   - Opção B (produção): use variáveis de ambiente no provedor (ex.: Railway)
     - `GOOGLE_SHEETS_CREDENTIALS_JSON` = conteúdo do JSON completo
     - ou `GOOGLE_SHEETS_CREDENTIALS_B64` = Base64 do JSON
   - Sempre compartilhe a planilha com o `client_email` como Editor

### 3. 📦 INSTALAR DEPENDÊNCIAS

```bash
pip install pandas openpyxl gspread google-auth google-auth-oauthlib
```

### 4. 🧪 TESTAR CONFIGURAÇÃO

```bash
# Teste básico
python src/main.py --help

# Teste de busca
python run_production.py --cnae 5611-2/01 --limite 5

# Teste com filtros
python run_production.py --cnae 5611-2/01 --uf SP --cidade "São Paulo" --limite 10
```

### 5. 📁 ESTRUTURA FINAL

```
cnae-prospector/
├── .env                          # Configurações
├── config/
│   └── google_sheets.json       # Credenciais Google (opcional em prod; usar variáveis)
├── data/
│   ├── exports/                 # Arquivos exportados
│   ├── processed/               # Dados processados
│   └── raw/                     # Dados brutos
├── logs/                        # Logs do sistema
├── src/                         # Código fonte
├── run_production.py            # Script de produção
└── PRODUCAO.md                 # Este arquivo
```

## 🎯 COMANDOS DE PRODUÇÃO

### Busca Simples
```bash
python run_production.py --cnae 5611-2/01 --limite 100
```

### Busca com Filtros
```bash
python run_production.py --cnae 5611-2/01 --uf SP --cidade "São Paulo" --limite 50
```

### Busca para Excel
```bash
python run_production.py --cnae 5611-2/01 --formato excel --limite 200
```

### Busca por Setor (Tecnologia)
```bash
python src/main.py listar --setor "Tecnologia"
```

## ⚠️ IMPORTANTE

1. **Rate Limits**: Respeite os limites da sua API
2. **Backup**: Faça backup dos dados exportados
3. **Logs**: Monitore os logs em `logs/`
4. **Credenciais**: Nunca compartilhe as credenciais
5. **Testes**: Sempre teste com poucos registros primeiro

## 🆘 SOLUÇÃO DE PROBLEMAS

### Erro de API Key
- Verifique se a chave está correta no `.env`
- Confirme se o plano está ativo no RapidAPI

### Erro de Google Sheets
- Verifique se o arquivo `config/google_sheets.json` existe
- Confirme se as APIs estão ativadas no Google Cloud

### Erro de Rate Limit
- Aguarde alguns minutos
- Reduza o limite de resultados
- Considere um plano maior

## 📞 SUPORTE

Para dúvidas ou problemas:
1. Verifique os logs em `logs/`
2. Teste com comandos simples primeiro
3. Confirme as configurações no `.env` 