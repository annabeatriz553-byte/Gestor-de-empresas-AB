# 🏢 Gestor de Empresas - Aplicativo Streamlit

Sistema completo de controle interno de empresas com banco de dados SQLite, desenvolvido com Streamlit.

## ✨ Funcionalidades

- 📊 **Dashboard** - Visualização de estatísticas gerais e por mês
- ➕ **Cadastro de Empresas** - Adicionar novas empresas com informações completas
- 📝 **Gerenciamento** - Editar, buscar e deletar empresas
- 📅 **Situação do Mês** - Registrar status das etapas para cada empresa
- 📈 **Relatórios** - Gerar relatórios e exportar dados em Excel/CSV

## 🚀 Como Instalar

### 1. Instalar Python (se não tiver)
Baixe e instale do [python.org](https://www.python.org/)

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Executar o App
```bash
streamlit run app.py
```

O app abrirá automaticamente no seu navegador em `http://localhost:8501`

## 📋 Como Usar

### 📊 Dashboard
- Visualize o resumo geral de empresas
- Veja estatísticas do mês selecionado
- Acompanhe o progresso das etapas

### ➕ Cadastrar Empresa
1. Clique em "Cadastrar Empresa" no menu
2. Preencha os dados da empresa
3. Clique em "Cadastrar Empresa"

**Campos:**
- Nome da empresa * (obrigatório)
- Responsável
- Email
- Telefone
- CNPJ
- Endereço
- Status (Ativa, Inativa, Suspensa)
- Observações

### 📝 Gerenciar Empresas
1. Busque por nome, email, telefone ou CNPJ
2. Filtre por status se necessário
3. Use os botões para editar ou deletar

### 📅 Situação do Mês
1. Selecione a empresa
2. Marque as etapas concluídas:
   - ✅ Notas de Entrada
   - ✅ Notas de Saída
   - ✅ Notas de Serviço
   - ✅ Conciliação
   - ✅ Documentação Completa
3. Adicione observações se necessário
4. Clique em "Salvar Situação"

O histórico de registros da empresa será exibido automaticamente.

### 📈 Relatórios
- **Visão Geral** - Tabela com status de todas as empresas
- **Detalhado** - Histórico completo de uma empresa específica
- **Exportar** - Baixe dados em Excel ou CSV

## 🗄️ Banco de Dados

O app usa SQLite (banco de dados local).

**Arquivo do banco:** `empresas.db` (criado automaticamente)

### Estrutura das Tabelas

#### Empresas
- ID
- Nome (único)
- Responsável
- Email
- Telefone
- CNPJ
- Endereço
- Status (ativa/inativa/suspensa)
- Data de cadastro
- Observações

#### Situação do Mês
- ID
- ID da Empresa
- Mês (MM)
- Ano
- Notas de Entrada (0/1)
- Notas de Saída (0/1)
- Notas de Serviço (0/1)
- Conciliação (0/1)
- Documentação OK (0/1)
- Observações
- Data de atualização

## 🌐 Hospedagem no Streamlit Cloud

### 1. Criar conta
Acesse [streamlit.io](https://streamlit.io) e crie uma conta

### 2. Fazer upload do repositório
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/gestor-empresas
git push -u origin main
```

### 3. Deploy
1. Acesse streamlit.io/cloud
2. Clique em "New app"
3. Selecione seu repositório GitHub
4. Escolha o branch `main`
5. Especifique `app.py` como arquivo principal
6. Clique em "Deploy"

O app estará disponível em: `https://seu-nome-app.streamlit.app`

## 📝 Arquivos do Projeto

```
.
├── app.py              # Aplicativo principal (Streamlit)
├── database.py         # Funções de banco de dados
├── requirements.txt    # Dependências do projeto
├── README.md          # Este arquivo
└── empresas.db        # Banco de dados (criado automaticamente)
```

## 🔧 Personalizações

### Alterar Cores
Edite o CSS em `app.py` (seção de styles)

### Adicionar Novos Campos
1. Modifique a tabela no `database.py`
2. Atualize as funções de inserção/atualização
3. Adicione os campos nos formulários do `app.py`

### Mudar o Banco de Dados
Para usar PostgreSQL ou MySQL, substitua as chamadas SQLite no `database.py`

## ⚠️ Notas Importantes

- O banco de dados é local (SQLite)
- Dados são salvos no servidor onde o app está hospedado
- Faça backup regular do arquivo `empresas.db`
- Primeira coluna com dados é obrigatória em formulários

## 🆘 Solução de Problemas

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### "Database is locked"
Feche outras instâncias do app e tente novamente

### Dados não aparecem
Verifique se o arquivo `empresas.db` existe na pasta do projeto

## 📞 Suporte

Para dúvidas ou sugestões, entre em contato.

---

**Desenvolvido com ❤️ usando Streamlit**
