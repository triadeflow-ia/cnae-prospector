# 🚀 RAILWAY DEPLOY - PASSO A PASSO COMPLETO

## 📋 ETAPA 1: PREPARAR AMBIENTE LOCAL

### 1.1 Ativar Ambiente Virtual
```bash
# Ativar venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 1.2 Testar Localmente
```bash
# Testar API local
python run_production.py --api --port 8000

# Acessar: http://localhost:8000
```

### 1.3 Verificar Git
```bash
# Verificar status
git status

# Se houver mudanças, commitar
git add .
git commit -m "fix: add missing dependencies"
```

---

## 🌐 ETAPA 2: CRIAR PROJETO NO RAILWAY

### 2.1 Acessar Railway
1. **Acesse:** https://railway.app
2. **Login** com GitHub
3. **Clique:** "New Project"

### 2.2 Conectar Repositório
1. **Selecione:** "Deploy from GitHub repo"
2. **Autorize** o Railway a acessar seus repos
3. **Escolha:** o repositório `cnae-prospector`
4. **Clique:** "Deploy Now"

---

## ⚙️ ETAPA 3: CONFIGURAR VARIÁVEIS

### 3.1 Adicionar Variáveis de Ambiente
No painel Railway, vá em **Variables** e adicione:

```env
NUVEM_FISCAL_CLIENT_ID=XvvT85IC3PzNNeNrOIR6
NUVEM_FISCAL_CLIENT_SECRET=lClvhEuEuaJ4bZrCUcPjmgq6P6OZdccSjjp9pbXW
NUVEM_FISCAL_BASE_URL=https://api.nuvemfiscal.com.br
GOOGLE_SHEETS_ID=1ecOvpQfR0venrB4RcFCm6ta5IngygSkeJUN_IEKubQY
PRODUCTION=true
LOG_LEVEL=INFO
```

### 3.2 Verificar Deploy
1. **Aba "Deployments"** - ver progresso
2. **Aba "Logs"** - verificar erros
3. **Aguardar** conclusão (~3-5 minutos)

---

## 🔗 ETAPA 4: OBTER URL E TESTAR

### 4.1 URL da Aplicação
Railway gerará uma URL como:
```
https://cnae-prospector-production-XXXX.up.railway.app
```

### 4.2 Testar Endpoints
```bash
# Health check
https://sua-app.railway.app/health

# Interface web
https://sua-app.railway.app

# API search
https://sua-app.railway.app/api/search?cnae=5611-2/01&limite=5
```

---

## 🎯 ETAPA 5: USAR EM PRODUÇÃO

### 5.1 Interface Web
1. **Acesse** a URL da aplicação
2. **Preencha** o formulário:
   - CNAE: `5611-2/01`
   - UF: `MG`
   - Cidade: `Uberlândia`
   - Limite: `10`
3. **Marque** "Exportar para Google Sheets"
4. **Clique** "Buscar Empresas"

### 5.2 API Direta
```javascript
// Exemplo JavaScript
fetch('https://sua-app.railway.app/api/search?cnae=5611-2/01&uf=MG&limite=10&sheets=on')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 🔧 TROUBLESHOOTING

### ❌ Deploy Falhou
**Verifique:**
1. **Logs** no Railway
2. **requirements.txt** completo
3. **Procfile** correto

### ❌ Erro 500
**Possíveis causas:**
1. Variáveis de ambiente faltando
2. Google Sheets sem permissão
3. API da Nuvem Fiscal offline

### ❌ Timeout
**Soluções:**
1. Reduzir limite de busca
2. Usar plano Pro do Railway
3. Implementar cache

---

## 💰 CUSTOS RAILWAY

| Plano | Preço | Recursos |
|-------|-------|----------|
| **Hobby** | $5/mês | 512MB RAM, 500GB transfer |
| **Pro** | $20/mês | 8GB RAM, transfer ilimitado |

---

## 🎊 FINALIZAÇÃO

### ✅ Checklist de Sucesso
- [ ] App rodando na URL do Railway
- [ ] Health check respondendo
- [ ] Interface web carregando
- [ ] Busca por CNAE funcionando
- [ ] Export para Google Sheets funcionando
- [ ] API endpoints respondendo

### 🚀 Próximos Passos
1. **Configurar domínio próprio** (opcional)
2. **Implementar cache Redis** para performance
3. **Adicionar autenticação** para uso comercial
4. **Integrar com mais APIs** de dados

---

## 📞 SUPORTE

Se algo não funcionar:
1. **Verifique logs** no Railway
2. **Teste localmente** primeiro
3. **Confira variáveis** de ambiente
4. **Documente o erro** específico

**🎯 SUCESSO = Aplicação rodando + Dados exportando para Sheets!**