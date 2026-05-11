# 📁 Estrutura do Projeto - Gestor de Empresas

## 📂 Arquivos do Projeto

```
gestor-empresas/
│
├── 📄 app.py                    # Aplicação principal (Streamlit)
├── 📄 database.py               # Funções do banco de dados
├── 📄 requirements.txt          # Dependências do projeto
├── 📄 README.md                 # Documentação completa
├── 📄 QUICKSTART.md             # Guia rápido
├── 📄 DEPLOYMENT.md             # Guia de hospedagem
├── 📄 ESTRUTURA.md              # Este arquivo
│
├── 🔧 install.bat               # Script de instalação (Windows)
├── 🔧 run.bat                   # Script para executar (Windows)
├── 🔧 seed_data.py              # Script para dados de teste
│
├── 📋 .gitignore                # Arquivos ignorados pelo Git
├── ⚙️ .streamlit/config.toml    # Configuração do Streamlit
│
└── 💾 empresas.db               # Banco de dados (criado automaticamente)
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────┐
│       Interface Streamlit (app.py)      │
├─────────────────────────────────────────┤
│  • Dashboard                            │
│  • Cadastro de Empresas                 │
│  • Gerenciamento                        │
│  • Situação do Mês                      │
│  • Relatórios & Exportação              │
└──────────────────┬──────────────────────┘
                   │
                   │ usa
                   ↓
┌─────────────────────────────────────────┐
│    Camada de Dados (database.py)        │
├─────────────────────────────────────────┤
│  • Funções CRUD                         │
│  • Queries do banco                     │
│  • Validações                           │
│  • Busca e filtros                      │
└──────────────────┬──────────────────────┘
                   │
                   │ conecta
                   ↓
┌─────────────────────────────────────────┐
│    Banco de Dados (SQLite/PostgreSQL)   │
├─────────────────────────────────────────┤
│  • Tabela: empresas                     │
│  • Tabela: situacao_mes                 │
└─────────────────────────────────────────┘
```

## 📊 Modelo de Dados

### Tabela: EMPRESAS
```sql
CREATE TABLE empresas (
    id INTEGER PRIMARY KEY,
    nome TEXT UNIQUE,
    responsavel TEXT,
    email TEXT,
    telefone TEXT,
    cnpj TEXT,
    endereco TEXT,
    status TEXT,              -- ativa|inativa|suspensa
    data_cadastro TIMESTAMP,
    observacoes TEXT
);
```

### Tabela: SITUACAO_MES
```sql
CREATE TABLE situacao_mes (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER,
    mes TEXT,                 -- MM (01-12)
    ano INTEGER,              -- YYYY
    notas_entrada INTEGER,    -- 0|1
    notas_saida INTEGER,      -- 0|1
    notas_servico INTEGER,    -- 0|1
    conciliacao INTEGER,      -- 0|1
    documentacao_ok INTEGER,  -- 0|1
    observacoes TEXT,
    data_atualizacao TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
);
```

## 🔄 Fluxo de Dados

```
1. USUÁRIO ACESSA APP
   ↓
2. STREAMLIT CARREGA app.py
   ↓
3. MENU LATERAL (Escolhe opção)
   ├─→ Dashboard → Carrega estatísticas → database.py
   ├─→ Cadastrar → Salva empresa → database.py → SQLite
   ├─→ Gerenciar → Lista/Edita/Deleta → database.py
   ├─→ Situação → Registra mês → database.py → SQLite
   └─→ Relatórios → Exporta dados → database.py

4. DADOS RETORNAM
   ├─→ Dataframes (Pandas)
   ├─→ Gráficos (Plotly)
   └─→ Tabelas (HTML)

5. PÁGINA ATUALIZADA NO NAVEGADOR
```

## 🔐 Funções Principais

### Em database.py

| Função | Descrição |
|--------|-----------|
| `init_database()` | Cria tabelas |
| `adicionar_empresa()` | INSERT empresa |
| `obter_todas_empresas()` | SELECT * empresas |
| `obter_empresa_por_id()` | SELECT by ID |
| `atualizar_empresa()` | UPDATE empresa |
| `deletar_empresa()` | DELETE empresa |
| `adicionar_situacao_mes()` | INSERT/UPDATE situação |
| `obter_situacao_mes()` | SELECT situação |
| `obter_historico_empresa()` | SELECT histórico |
| `obter_estatisticas_mes()` | SELECT estatísticas |
| `buscar_empresas()` | LIKE search |

### Em app.py

| Menu | Função |
|------|--------|
| 📊 Dashboard | `st.metric()`, Gráficos Plotly |
| ➕ Cadastrar | `st.form()`, Validações |
| 📝 Gerenciar | CRUD completo com confirmação |
| 📅 Situação | Checkboxes, Histórico |
| 📈 Relatórios | Dataframes, Exportação CSV/Excel |

## 📦 Dependências

```
streamlit==1.28.1      # Framework web
pandas==2.1.3          # Manipulação de dados
plotly==5.18.0         # Gráficos interativos
sqlite3                # Banco de dados (built-in)
python-dateutil==2.8.2 # Datas e horas
```

## 🎨 Componentes UI

### Streamlit
- `st.title()` - Título
- `st.markdown()` - Texto formatado
- `st.metric()` - Cartão de métrica
- `st.form()` - Formulário
- `st.text_input()` - Input de texto
- `st.text_area()` - Textarea
- `st.selectbox()` - Dropdown
- `st.checkbox()` - Checkbox
- `st.dataframe()` - Tabela
- `st.plotly_chart()` - Gráfico
- `st.button()` - Botão
- `st.session_state` - Estado da sessão

### Plotly
- `go.Figure()` - Figura base
- `go.Pie()` - Gráfico de pizza
- `go.Bar()` - Gráfico de barras
- `px.line()` - Gráfico de linhas

## 🔄 Ciclo de Vida

1. **Inicialização**
   ```
   init_database() → cria tabelas
   ```

2. **Renderização**
   ```
   app.py → carrega dados → renderiza UI
   ```

3. **Interação**
   ```
   Usuário clica → Streamlit processa → database.py
   ```

4. **Atualização**
   ```
   Dados salvos → rerun() → página atualiza
   ```

## 📱 Responsividade

- ✅ Design adaptável
- ✅ `st.columns()` para layout
- ✅ `st.tabs()` para abas
- ✅ `use_container_width=True` em gráficos

## 🔒 Segurança

- ✅ Validações de input
- ✅ Confirmação antes de deletar
- ✅ Constraints UNIQUE no banco
- ✅ Foreign Keys para integridade

## ⚡ Performance

- 📊 `st.cache_data` para funções caras
- 🗂️ Índices no banco de dados
- 📦 Lazy loading de dados
- 🔄 Reutilização de conexões

## 🚀 Escalabilidade

Para crescimento:
1. Migrar SQLite → PostgreSQL
2. Adicionar autenticação (Streamlit Auth)
3. Implementar paginação
4. Adicionar filtros avançados
5. Criar APIs externas

## 📚 Documentação

- 📖 `README.md` - Documentação completa
- ⚡ `QUICKSTART.md` - Começar rápido
- 🚀 `DEPLOYMENT.md` - Hospedagem
- 📁 `ESTRUTURA.md` - Este arquivo

---

**Desenvolvido com estrutura profissional e pronto para produção!** ✨
