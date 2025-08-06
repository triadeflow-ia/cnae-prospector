# 🚀 Deploy Railway - CNAE Prospector

## 📋 Passo a Passo para Deploy

### 1. 📁 Preparar o Repositório

Primeiro, vamos verificar se tudo está pronto:

```bash
# Verificar se está tudo commitado
git status

# Se há mudanças, commitar
git add .
git commit -m "feat: prepare for railway deployment"
```

### 2. 🔧 Configurar Railway

1. **Acesse railway.app**
2. **Conecte seu GitHub** (se ainda não fez)
3. **Clique em "New Project"**
4. **Selecione "Deploy from GitHub repo"**
5. **Escolha o repositório cnae-prospector**

### 3. ⚙️ Configurar Variáveis de Ambiente

No painel do Railway, vá em **Variables** e adicione:

```env
# Nuvem Fiscal API
NUVEM_FISCAL_CLIENT_ID=XvvT85IC3PzNNeNrOIR6
NUVEM_FISCAL_CLIENT_SECRET=lClvhEuEuaJ4bZrCUcPjmgq6P6OZdccSjjp9pbXW
NUVEM_FISCAL_BASE_URL=https://api.nuvemfiscal.com.br

# Google Sheets
GOOGLE_SHEETS_ID=1ecOvpQfR0venrB4RcFCm6ta5IngygSkeJUN_IEKubQY

# Produção
PRODUCTION=true
LOG_LEVEL=INFO
PORT=8000
```

### 4. 🎯 Comando de Start

O Railway detectará automaticamente o Python, mas você pode definir o comando de start:

```
python run_production.py --api --host 0.0.0.0 --port $PORT
```

### 5. 🔗 URL da Aplicação

Após o deploy, o Railway fornecerá uma URL como:
```
https://cnae-prospector-production.up.railway.app
```

## 🎮 Como Usar Após Deploy

### Interface Web
```
https://seu-app.railway.app
```

### API Endpoints
```
GET https://seu-app.railway.app/health
GET https://seu-app.railway.app/api/search?cnae=5611-2/01&uf=MG&limite=10
```

## 🔧 Configurações Avançadas

### Custom Domain (Opcional)
1. No Railway, vá em **Settings**
2. **Domains** → **Custom Domain**
3. Adicione seu domínio

### Escalabilidade
- Railway escala automaticamente
- Suporta até 8GB RAM
- CPU ilimitado

## 📊 Monitoramento

### Logs em Tempo Real
No painel Railway:
1. **Deployments** tab
2. **View Logs**

### Métricas
- CPU usage
- Memory usage
- Network traffic

## 💰 Custos

- **Hobby Plan**: $5/mês (suficiente para começar)
- **Pro Plan**: $20/mês (para produção séria)
- **Included**: 500GB bandwidth

## 🚨 Troubleshooting

### Erro de Port
Certifique-se que está usando:
```python
port = int(os.environ.get('PORT', 8000))
```

### Timeout
Railway tem timeout de 60s para requests
Para searches longas, implemente async

### Memory Limit
Se ultrapassar 512MB, upgrade para Pro

## ✅ Checklist de Deploy

- [ ] Código commitado e pushed
- [ ] Railway project criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy concluído com sucesso
- [ ] URL funcionando
- [ ] API testada
- [ ] Google Sheets integrado