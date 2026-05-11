# ⚡ Guia Rápido - Gestor de Empresas

## 🚀 Começar em 3 Passos

### Passo 1: Instalar dependências
```bash
pip install -r requirements.txt
```

### Passo 2: Executar o app
```bash
streamlit run app.py
```

### Passo 3: Abrir no navegador
O app abrirá automaticamente em: `http://localhost:8501`

---

## 📚 Primeiro Uso

### 1️⃣ Cadastrar uma empresa
- Menu: **➕ Cadastrar Empresa**
- Preencha os dados básicos
- Clique em **✅ Cadastrar Empresa**

### 2️⃣ Registrar situação do mês
- Menu: **📅 Situação do Mês**
- Selecione a empresa
- Marque as etapas concluídas
- Clique em **💾 Salvar Situação**

### 3️⃣ Acompanhar no dashboard
- Menu: **📊 Dashboard**
- Selecione mês e ano
- Veja as estatísticas em tempo real

---

## 🎯 Menu Rápido

| Menu | O que faz |
|------|-----------|
| 📊 Dashboard | Resumo geral e estatísticas |
| ➕ Cadastrar | Adicionar nova empresa |
| 📝 Gerenciar | Editar/deletar empresas |
| 📅 Situação | Registrar status do mês |
| 📈 Relatórios | Gerar e exportar dados |

---

## 📊 Etapas que você pode rastrear

✅ **Notas de Entrada**  
✅ **Notas de Saída**  
✅ **Notas de Serviço**  
✅ **Conciliação**  
✅ **Documentação Completa**

---

## 💾 Dados

- Banco de dados: **SQLite** (local)
- Arquivo: `empresas.db` (criado automaticamente)
- Sem necessidade de configuração externa

---

## 🌐 Hospedagem

Para publicar na nuvem (Streamlit Cloud):

1. Upload para GitHub
2. Conectar em streamlit.io/cloud
3. Deploy automático ✨

Veja `README.md` para instruções completas.

---

## 🆘 Problemas?

**App não abre?**
```bash
streamlit run app.py --logger.level=debug
```

**Banco de dados travado?**
- Feche outras abas/instâncias do app
- Reinicie o Streamlit

**Precisa resetar dados?**
- Delete o arquivo `empresas.db`
- Execute o app novamente (recriará com dados vazios)

---

Aproveite! 🚀
