# 🚀 Guia de Deploy em Produção - CNAE Prospector

## 📋 Opções de Deploy

### 1. 🖥️ VPS/Servidor Dedicado (Recomendado)

#### **Provedores Recomendados:**
- **DigitalOcean**: $5-20/mês
- **Linode**: $5-20/mês  
- **Vultr**: $3.50-15/mês
- **AWS EC2**: $10-30/mês
- **Google Cloud Compute**: $10-25/mês

#### **Especificações Mínimas:**
- **CPU**: 1 vCPU
- **RAM**: 1GB (2GB recomendado)
- **Storage**: 25GB SSD
- **OS**: Ubuntu 20.04/22.04 LTS

---

### 2. ☁️ Plataformas Cloud (Mais Fácil)

#### **Heroku** (Mais Simples)
```bash
# Deploy direto via Git
heroku create cnae-prospector
git push heroku main
```

#### **Railway** (Moderno)
```bash
# Deploy automático via GitHub
railway login
railway link
railway up
```

#### **Render** (Gratuito)
- Deploy automático via GitHub
- SSL gratuito
- Banco PostgreSQL incluído

---

### 3. 🐳 Docker (Mais Profissional)

#### **Docker + VPS**
```bash
# Executar via Docker
docker build -t cnae-prospector .
docker run -d -p 80:8000 cnae-prospector
```

#### **Docker Compose**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "80:8000"
    environment:
      - PRODUCTION=true
    restart: unless-stopped
```

---

## 🛠️ Setup de Produção

### 1. **Preparação do Ambiente**

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.9+
sudo apt install python3 python3-pip python3-venv -y

# Instalar dependências do sistema
sudo apt install nginx supervisor redis-server -y

# Criar usuário para aplicação
sudo useradd -m -s /bin/bash cnae-prospector
sudo su - cnae-prospector
```

### 2. **Deploy da Aplicação**

```bash
# Clone do repositório
git clone https://github.com/seu-usuario/cnae-prospector.git
cd cnae-prospector

# Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Configurar credenciais reais
```

### 3. **Configuração do Nginx**

```nginx
# /etc/nginx/sites-available/cnae-prospector
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/cnae-prospector/cnae-prospector/static/;
    }
}
```

### 4. **Supervisor para Auto-restart**

```ini
# /etc/supervisor/conf.d/cnae-prospector.conf
[program:cnae-prospector]
command=/home/cnae-prospector/cnae-prospector/venv/bin/python run_production.py --api
directory=/home/cnae-prospector/cnae-prospector
user=cnae-prospector
autostart=true
autorestart=true
stderr_logfile=/var/log/cnae-prospector.err.log
stdout_logfile=/var/log/cnae-prospector.out.log
```

---

## 🔒 Segurança em Produção

### 1. **SSL Certificate**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL gratuito
sudo certbot --nginx -d seu-dominio.com
```

### 2. **Firewall**
```bash
# Configurar UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 3. **Backup Automático**
```bash
# Script de backup diário
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backup/cnae-prospector-$DATE.tar.gz /home/cnae-prospector/cnae-prospector
```

---

## 📊 Monitoramento

### 1. **Logs**
```bash
# Visualizar logs em tempo real
tail -f /var/log/cnae-prospector.out.log
tail -f /var/log/cnae-prospector.err.log
```

### 2. **Métricas**
```bash
# Usar htop para monitorar recursos
htop

# Monitorar espaço em disco
df -h

# Monitorar memória
free -h
```

---

## 🚀 Deploy Rápido - Opção 1: Railway

1. **Conectar GitHub ao Railway**
2. **Push do código**
3. **Configurar variáveis de ambiente**
4. **Deploy automático**

## 🚀 Deploy Rápido - Opção 2: DigitalOcean

1. **Criar Droplet Ubuntu**
2. **Executar script de setup**
3. **Configurar domínio**
4. **SSL automático**

---

## 💰 Custos Estimados

| Opção | Custo Mensal | Prós | Contras |
|-------|--------------|------|---------|
| **Heroku** | $7-25 | Muito fácil | Limitações |
| **Railway** | $5-20 | Moderno, Git deploy | Menos features |
| **DigitalOcean** | $5-20 | Controle total | Requer setup |
| **AWS EC2** | $10-30 | Escalável | Complexo |

---

## 🎯 Recomendação

**Para começar**: Use **Railway** ou **Render** (mais fácil)
**Para crescer**: Migre para **DigitalOcean** + **Nginx** (mais controle)
**Para escalar**: Use **AWS** ou **Google Cloud** (mais recursos)