# Setup PostgreSQL no Render

## 1. Criar Banco de Dados no Render

1. Acesse [render.com](https://render.com)
2. Clique em **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name:** gestor-empresas-db
   - **Database:** empresas_db
   - **User:** postgres_user
   - **Plan:** Free (90 dias grátis)

4. Clique em **"Create Database"** e aguarde ~2 minutos

---

## 2. Conectar o Banco ao App

1. Na página do PostgreSQL, copie a **"Internal Database URL"**
2. Vá para sua **Web Service** (Gestor de Empresas)
3. Acesse **Settings** → **Environment Variables**
4. Adicione:
   - **Key:** `DATABASE_URL`
   - **Value:** Cole a URL do banco

5. Clique em **"Save Changes"** — o app vai reiniciar automaticamente

---

## 3. Verificar Conexão

- Acesse sua aplicação em: `https://gestor-empresas-ab.onrender.com`
- O app vai criar as tabelas automaticamente na primeira execução
- Se houver erro, verifique os logs em **"Logs"** na web service

---

## ⚠️ Importante

- **Free tier expira em 90 dias** — depois disso, escolha entre:
  - Pagar ~$15/mês por PostgreSQL gerenciado
  - Migrar para **Supabase** (PostgreSQL permanente grátis)
  
- **Backups:** Exporte seus dados regularmente usando:
  ```bash
  pg_dump postgresql://user:pass@host:5432/db > backup.sql
  ```

---

## 🔄 Desenvolvimento Local

Se quiser testar localmente sem PostgreSQL:

1. Remova `DATABASE_URL` do seu `.env`
2. O app usa SQLite (`empresas.db`) automaticamente
3. Em produção, o Render detecta `DATABASE_URL` e usa PostgreSQL

