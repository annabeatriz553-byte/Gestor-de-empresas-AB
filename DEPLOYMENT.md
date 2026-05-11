# 🚀 Guia de Deployment - Streamlit Cloud

Este guia mostra como hospedar seu app Gestor de Empresas no **Streamlit Cloud** (gratuito e fácil).

## 📋 Pré-requisitos

- ✅ Conta GitHub (gratuita)
- ✅ Conta Streamlit (gratuita)
- ✅ Seu projeto no GitHub

## 🔧 Passo 1: Preparar o Repositório GitHub

### 1.1 Inicializar Git

```bash
cd C:\Users\Anna Beatriz\Desktop\claude
git init
```

### 1.2 Criar arquivo .gitignore (já existe)

Certifique-se de que `empresas.db` está em `.gitignore` (está por padrão)

### 1.3 Fazer commit dos arquivos

```bash
git add .
git commit -m "Initial commit - Gestor de Empresas"
```

### 1.4 Adicionar remoto GitHub

```bash
git remote add origin https://github.com/seu-usuario/gestor-empresas
git branch -M main
git push -u origin main
```

> Substitua `seu-usuario` pelo seu usuário do GitHub

## 🌐 Passo 2: Criar Conta Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Clique em **"Sign up"**
3. Faça login com sua conta GitHub
4. Autorize o Streamlit Cloud

## 🚀 Passo 3: Deploy da Aplicação

### 3.1 Criar novo app

1. Acesse: https://share.streamlit.io
2. Clique em **"Create app"**
3. Selecione seu repositório: `seu-usuario/gestor-empresas`
4. Escolha o branch: **`main`**
5. Especifique o arquivo principal: **`app.py`**
6. Clique em **"Deploy"**

### 3.2 Aguardar o deployment

O Streamlit vai:
- ✅ Fazer clone do repositório
- ✅ Instalar dependências de `requirements.txt`
- ✅ Executar `app.py`

Seu app estará disponível em: `https://seu-nome-app.streamlit.app`

## 💾 Passo 4: Usar o Banco de Dados

### Problema: Banco de Dados Local

O SQLite armazena dados localmente. No Streamlit Cloud, eles são perdidos quando a app reinicia.

### Solução: PostgreSQL Grátis

Para persistência de dados, use **PostgreSQL** (recomendado).

#### 4.1 Criar conta Supabase (PostgreSQL gratuito)

1. Acesse: https://supabase.com
2. Clique em **"Start your project"**
3. Crie uma conta com GitHub
4. Crie um novo projeto
5. Copie a string de conexão

#### 4.2 Modificar database.py

Substitua as funções SQLite por PostgreSQL:

```python
import psycopg2

DB_URL = "postgresql://user:password@db.supabase.co:5432/postgres"

def init_database():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id SERIAL PRIMARY KEY,
            nome TEXT UNIQUE NOT NULL,
            ...
        )
    ''')
    # ... resto do código
```

#### 4.3 Adicionar secrets no Streamlit Cloud

1. Vá para seu app no Streamlit Cloud
2. Clique em **"Settings"** ⚙️
3. Selecione **"Secrets"**
4. Adicione:

```toml
DATABASE_URL = "postgresql://user:password@db.supabase.co:5432/postgres"
```

5. Clique em **"Save"**

#### 4.4 Acessar o secret no código

```python
import streamlit as st

db_url = st.secrets["DATABASE_URL"]
```

## 🔐 Passo 5: Variáveis de Ambiente (Opcionais)

Se precisar de outras configurações:

1. No Streamlit Cloud, vá em **Settings > Secrets**
2. Adicione suas variáveis:

```toml
# Secrets.toml
DATABASE_URL = "postgresql://..."
API_KEY = "seu-chave-aqui"
```

3. Use no código:

```python
import streamlit as st

api_key = st.secrets.get("API_KEY", "default")
```

## ✅ Passo 6: Verificar o Deploy

- Acesse sua URL: `https://seu-nome-app.streamlit.app`
- Teste todas as funcionalidades
- Verifique os logs em **"Manage app" > "Logs"**

## 🔄 Atualizações Futuras

Toda vez que você fizer push para o GitHub:

```bash
git add .
git commit -m "Descrição da mudança"
git push origin main
```

O Streamlit Cloud automaticamente:
- ✅ Detecta as alterações
- ✅ Faz novo deployment
- ✅ Publica a nova versão

## 📊 Alternativas de Banco de Dados

| Serviço | Plano Gratuito | Limite | Custo |
|---------|---|---|---|
| **SQLite** | ✅ | Dados perdidos | Grátis |
| **Supabase (PostgreSQL)** | ✅ | 500MB | Grátis |
| **Firebase** | ✅ | 1GB | Grátis |
| **MongoDB Atlas** | ✅ | 512MB | Grátis |

## 🆘 Troubleshooting

### "Module not found"
Adicione no início de `app.py`:
```python
import sys
sys.path.insert(0, '/mount/src/seu-repo')
```

### "Permission denied"
Verifique que todos os arquivos têm permissão de leitura

### "Database connection failed"
- Verifique a URL no Secrets
- Verifique se o banco está online
- Teste a conexão localmente primeiro

### App muito lento
- Use cache do Streamlit:
```python
@st.cache_data
def carregar_dados():
    return obter_todas_empresas()
```

## 📞 Contatos Úteis

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Community:** https://discuss.streamlit.io
- **Supabase Docs:** https://supabase.com/docs

## 🎉 Pronto!

Seu app está no ar! Compartilhe o link: `https://seu-nome-app.streamlit.app`

---

**Dica:** Crie um `README.md` bem documentado para que outros possam usar seu app!
