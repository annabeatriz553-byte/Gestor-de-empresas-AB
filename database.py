import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime
from pathlib import Path
import os

ETAPAS_PADRAO = ["Notas de Entrada", "Notas de Saída", "Notas de Serviço", "Conciliação"]

# Detectar se está em desenvolvimento (SQLite) ou produção (PostgreSQL)
DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = DATABASE_URL is not None

def _get_conn():
    """Retorna conexão com PostgreSQL ou SQLite conforme o ambiente."""
    if USE_POSTGRES:
        # Produção: PostgreSQL no Render
        conn = psycopg2.connect(DATABASE_URL)
    else:
        # Desenvolvimento: SQLite local
        import sqlite3
        DB_PATH = Path(__file__).parent / "empresas.db"
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_database():
    conn = _get_conn()
    c = conn.cursor()

    if USE_POSTGRES:
        # PostgreSQL
        c.execute('''CREATE TABLE IF NOT EXISTS empresas (
            id                SERIAL PRIMARY KEY,
            nome              VARCHAR(255) UNIQUE NOT NULL,
            responsavel       VARCHAR(255),
            email             VARCHAR(255),
            telefone          VARCHAR(20),
            cnpj              VARCHAR(18),
            endereco          TEXT,
            status            VARCHAR(20) DEFAULT 'ativa',
            data_cadastro     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observacoes       TEXT,
            codigo            VARCHAR(50),
            regime_tributario VARCHAR(100),
            informacoes       TEXT
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS etapas_empresa (
            id         SERIAL PRIMARY KEY,
            empresa_id INTEGER NOT NULL,
            nome       VARCHAR(255) NOT NULL,
            ordem      INTEGER DEFAULT 0,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS etapas_status (
            id        SERIAL PRIMARY KEY,
            etapa_id  INTEGER NOT NULL,
            mes       VARCHAR(2) NOT NULL,
            ano       INTEGER NOT NULL,
            concluido INTEGER DEFAULT 0,
            FOREIGN KEY (etapa_id) REFERENCES etapas_empresa(id) ON DELETE CASCADE,
            UNIQUE(etapa_id, mes, ano)
        )''')

        # Índices
        c.execute('CREATE INDEX IF NOT EXISTS idx_etapas_emp ON etapas_empresa(empresa_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_etapas_st  ON etapas_status(etapa_id, mes, ano)')

    else:
        # SQLite
        c.execute('''CREATE TABLE IF NOT EXISTS empresas (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            nome              TEXT UNIQUE NOT NULL,
            responsavel       TEXT,
            email             TEXT,
            telefone          TEXT,
            cnpj              TEXT,
            endereco          TEXT,
            status            TEXT DEFAULT 'ativa',
            data_cadastro     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            observacoes       TEXT,
            codigo            TEXT,
            regime_tributario TEXT,
            informacoes       TEXT
        )''')

        # migrações para bancos SQLite existentes
        for col, tipo in [
            ("codigo",            "TEXT"),
            ("regime_tributario", "TEXT"),
            ("informacoes",       "TEXT"),
        ]:
            try:
                c.execute(f"ALTER TABLE empresas ADD COLUMN {col} {tipo}")
            except:
                pass

        c.execute('''CREATE TABLE IF NOT EXISTS etapas_empresa (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nome       TEXT NOT NULL,
            ordem      INTEGER DEFAULT 0,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id) ON DELETE CASCADE
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS etapas_status (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            etapa_id  INTEGER NOT NULL,
            mes       TEXT NOT NULL,
            ano       INTEGER NOT NULL,
            concluido INTEGER DEFAULT 0,
            FOREIGN KEY (etapa_id) REFERENCES etapas_empresa(id) ON DELETE CASCADE,
            UNIQUE(etapa_id, mes, ano)
        )''')

        c.execute('CREATE INDEX IF NOT EXISTS idx_etapas_emp ON etapas_empresa(empresa_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_etapas_st  ON etapas_status(etapa_id, mes, ano)')

    conn.commit()

    # migração de etapas padrão
    c.execute('''
        SELECT id FROM empresas
        WHERE id NOT IN (SELECT DISTINCT empresa_id FROM etapas_empresa)
    ''')
    ids_sem_etapa = [r[0] for r in c.fetchall()]
    for eid in ids_sem_etapa:
        for i, nome in enumerate(ETAPAS_PADRAO):
            try:
                c.execute('INSERT INTO etapas_empresa (empresa_id, nome, ordem) VALUES (%s,%s,%s)' if USE_POSTGRES else 'INSERT INTO etapas_empresa (empresa_id, nome, ordem) VALUES (?,?,?)',
                          (eid, nome, i))
            except:
                pass
    conn.commit()
    conn.close()


def _migrar_etapas_existentes():
    """Mantido por compatibilidade — lógica migrada para init_database."""
    pass


def _adapt_query(query):
    """Adapta placeholder de SQLite (?) para PostgreSQL (%s) conforme necessário."""
    if USE_POSTGRES:
        return query.replace("?", "%s")
    return query


def importar_empresas_bulk(registros, status_padrao="ativa"):
    """
    Importa uma lista de empresas em UMA ÚNICA transação (muito mais rápido).
    registros: lista de dicts com keys nome, codigo, cnpj, regime_tributario,
               responsavel, telefone, email, observacoes
    Retorna (importadas, duplicadas, erros)
    """
    conn = _get_conn()
    c = conn.cursor()
    imp = dup = err = 0
    novos_ids = []

    insert_query = _adapt_query('''
        INSERT INTO empresas
        (nome, responsavel, email, telefone, cnpj, endereco,
         status, observacoes, codigo, regime_tributario)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    ''')

    for reg in registros:
        try:
            nome = str(reg.get("nome", "")).strip()
            if not nome or nome.lower() == "nan":
                continue
            c.execute(insert_query, (
                nome,
                str(reg.get("responsavel", "") or "").strip(),
                str(reg.get("email",        "") or "").strip(),
                str(reg.get("telefone",     "") or "").strip(),
                str(reg.get("cnpj",         "") or "").strip(),
                "",
                status_padrao,
                str(reg.get("observacoes",  "") or "").strip(),
                str(reg.get("codigo",       "") or "").strip(),
                str(reg.get("regime",       "") or "").strip(),
            ))
            if USE_POSTGRES:
                # PostgreSQL retorna com RETURNING
                novos_ids.append(c.fetchone()[0])
            else:
                novos_ids.append(c.lastrowid)
            imp += 1
        except Exception as e:
            if "unique" in str(e).lower():
                dup += 1
            else:
                err += 1

    # etapas padrão para todas as novas empresas — em lote
    if novos_ids:
        etapas_rows = [
            (eid, nome_et, ordem)
            for eid in novos_ids
            for ordem, nome_et in enumerate(ETAPAS_PADRAO)
        ]
        etapa_query = _adapt_query('INSERT INTO etapas_empresa (empresa_id, nome, ordem) VALUES (?,?,?)')
        for row in etapas_rows:
            try:
                c.execute(etapa_query, row)
            except:
                pass

    conn.commit()
    conn.close()
    return imp, dup, err


# ── Empresas ─────────────────────────────────────────────────

def adicionar_empresa(nome, responsavel="", email="", telefone="",
                      cnpj="", endereco="", status="ativa", observacoes="",
                      codigo="", regime_tributario="", informacoes=""):
    try:
        conn = _get_conn()
        c = conn.cursor()
        params = (nome, responsavel, email, telefone, cnpj, endereco, status, observacoes, codigo, regime_tributario, informacoes)

        if USE_POSTGRES:
            c.execute('''
                INSERT INTO empresas
                (nome, responsavel, email, telefone, cnpj, endereco, status, observacoes, codigo, regime_tributario, informacoes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            ''', params)
            empresa_id = c.fetchone()[0]
        else:
            c.execute('''
                INSERT INTO empresas
                (nome, responsavel, email, telefone, cnpj, endereco, status, observacoes, codigo, regime_tributario, informacoes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ''', params)
            empresa_id = c.lastrowid

        conn.commit()
        conn.close()
        adicionar_etapas_padrao(empresa_id)
        return True, "Empresa adicionada com sucesso!"
    except Exception as e:
        if "unique" in str(e).lower():
            return False, "Empresa com este nome já existe!"
        return False, f"Erro: {e}"


def obter_todas_empresas():
    conn = _get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM empresas ORDER BY nome')
    rows = c.fetchall()
    conn.close()
    return rows


def obter_empresa_por_id(eid):
    conn = _get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM empresas WHERE id=?', (eid,))
    row = c.fetchone()
    conn.close()
    return row


def atualizar_empresa(eid, nome, responsavel, email, telefone,
                      cnpj, endereco, status, observacoes,
                      codigo="", regime_tributario="", informacoes=""):
    try:
        conn = _get_conn()
        c = conn.cursor()
        query = _adapt_query('''
            UPDATE empresas SET nome=?, responsavel=?, email=?, telefone=?,
            cnpj=?, endereco=?, status=?, observacoes=?,
            codigo=?, regime_tributario=?, informacoes=?
            WHERE id=?
        ''')
        c.execute(query, (nome, responsavel, email, telefone, cnpj, endereco, status,
              observacoes, codigo, regime_tributario, informacoes, eid))
        conn.commit()
        conn.close()
        return True, "Empresa atualizada com sucesso!"
    except Exception as e:
        return False, f"Erro: {e}"


def deletar_empresa(eid):
    try:
        conn = _get_conn()
        c = conn.cursor()
        c.execute(_adapt_query('DELETE FROM etapas_empresa WHERE empresa_id=?'), (eid,))
        c.execute(_adapt_query('DELETE FROM empresas WHERE id=?'), (eid,))
        conn.commit()
        conn.close()
        return True, "Empresa excluída com sucesso!"
    except Exception as e:
        return False, f"Erro: {e}"


def buscar_empresas(termo):
    conn = _get_conn()
    c = conn.cursor()
    like = f'%{termo}%'
    c.execute(_adapt_query('''SELECT * FROM empresas
                 WHERE nome LIKE ? OR cnpj LIKE ? OR codigo LIKE ? OR email LIKE ? OR telefone LIKE ?
                 ORDER BY nome'''), (like,)*5)
    rows = c.fetchall()
    conn.close()
    return rows


def obter_dataframe_empresas():
    conn = _get_conn()
    df = pd.read_sql_query('SELECT * FROM empresas ORDER BY nome', conn)
    conn.close()
    return df


# ── Etapas ───────────────────────────────────────────────────

def adicionar_etapas_padrao(empresa_id):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('SELECT COUNT(*) FROM etapas_empresa WHERE empresa_id=?'), (empresa_id,))
    if c.fetchone()[0] == 0:
        for i, nome in enumerate(ETAPAS_PADRAO):
            c.execute(_adapt_query('INSERT INTO etapas_empresa (empresa_id, nome, ordem) VALUES (?,?,?)'),
                      (empresa_id, nome, i))
    conn.commit()
    conn.close()


def obter_etapas_empresa(empresa_id):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('SELECT * FROM etapas_empresa WHERE empresa_id=? ORDER BY ordem'), (empresa_id,))
    rows = c.fetchall()
    conn.close()
    return rows   # (id, empresa_id, nome, ordem)


def adicionar_etapa(empresa_id, nome):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('SELECT COALESCE(MAX(ordem),0) FROM etapas_empresa WHERE empresa_id=?'), (empresa_id,))
    ordem = c.fetchone()[0] + 1
    c.execute(_adapt_query('INSERT INTO etapas_empresa (empresa_id, nome, ordem) VALUES (?,?,?)'),
              (empresa_id, nome, ordem))
    conn.commit()
    conn.close()


def remover_etapa(etapa_id):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('DELETE FROM etapas_status  WHERE etapa_id=?'), (etapa_id,))
    c.execute(_adapt_query('DELETE FROM etapas_empresa WHERE id=?'),       (etapa_id,))
    conn.commit()
    conn.close()


def marcar_etapa(etapa_id, mes, ano, concluido: bool):
    conn = _get_conn()
    c = conn.cursor()
    if USE_POSTGRES:
        c.execute('''INSERT INTO etapas_status (etapa_id, mes, ano, concluido)
                     VALUES (%s,%s,%s,%s)
                     ON CONFLICT (etapa_id, mes, ano) DO UPDATE SET concluido=%s''',
                  (etapa_id, mes, ano, int(concluido), int(concluido)))
    else:
        c.execute('''INSERT OR REPLACE INTO etapas_status (etapa_id, mes, ano, concluido)
                     VALUES (?,?,?,?)''', (etapa_id, mes, ano, int(concluido)))
    conn.commit()
    conn.close()


def obter_status_etapas(empresa_id, mes, ano):
    """Retorna {etapa_id: concluido} para a empresa no mês/ano."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('''
        SELECT e.id, COALESCE(s.concluido, 0)
        FROM etapas_empresa e
        LEFT JOIN etapas_status s ON e.id=s.etapa_id AND s.mes=? AND s.ano=?
        WHERE e.empresa_id=?
        ORDER BY e.ordem
    '''), (mes, ano, empresa_id))
    rows = c.fetchall()
    conn.close()
    return {r[0]: bool(r[1]) for r in rows}


def calcular_progresso(empresa_id, mes, ano):
    """Retorna (pct, concluidas, total)."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('''
        SELECT e.id, COALESCE(s.concluido,0)
        FROM etapas_empresa e
        LEFT JOIN etapas_status s ON e.id=s.etapa_id AND s.mes=? AND s.ano=?
        WHERE e.empresa_id=?
    '''), (mes, ano, empresa_id))
    rows = c.fetchall()
    conn.close()
    if not rows:
        return 0, 0, 0
    total = len(rows)
    done  = sum(1 for r in rows if r[1])
    return round(done / total * 100), done, total


def obter_estatisticas_mes(mes, ano):
    """Retorna (total, completas, em_progresso, nao_iniciadas) — UMA query."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('''
        SELECT
            COUNT(*)                                                                    AS total,
            COALESCE(SUM(CASE WHEN total > 0 AND done = total  THEN 1 ELSE 0 END), 0) AS completas,
            COALESCE(SUM(CASE WHEN done > 0 AND done < total   THEN 1 ELSE 0 END), 0) AS em_prog,
            COALESCE(SUM(CASE WHEN done = 0                    THEN 1 ELSE 0 END), 0) AS nao_inic
        FROM (
            SELECT e.id,
                   COUNT(et.id)                                                        AS total,
                   SUM(CASE WHEN COALESCE(es.concluido,0)=1 THEN 1 ELSE 0 END)        AS done
            FROM empresas e
            LEFT JOIN etapas_empresa et ON et.empresa_id = e.id
            LEFT JOIN etapas_status  es ON es.etapa_id   = et.id
                                       AND es.mes = ? AND es.ano = ?
            GROUP BY e.id
        ) AS sub
    '''), (mes, ano))
    row = c.fetchone()
    conn.close()
    return row or (0, 0, 0, 0)


def obter_empresas_com_progresso(mes, ano):
    """
    Retorna todas as empresas com progresso calculado em UMA query.
    Cada linha: (id, nome, resp, email, tel, cnpj, end, status, data,
                 obs, codigo, regime, info, total_etapas, done)
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('''
        SELECT
            e.id, e.nome, e.responsavel, e.email, e.telefone,
            e.cnpj, e.endereco, e.status, e.data_cadastro,
            e.observacoes, e.codigo, e.regime_tributario, e.informacoes,
            COUNT(et.id)                                                        AS total,
            SUM(CASE WHEN COALESCE(es.concluido,0)=1 THEN 1 ELSE 0 END)        AS done
        FROM empresas e
        LEFT JOIN etapas_empresa et ON et.empresa_id = e.id
        LEFT JOIN etapas_status  es ON es.etapa_id   = et.id
                                   AND es.mes = ? AND es.ano = ?
        GROUP BY e.id, e.nome, e.responsavel, e.email, e.telefone,
                 e.cnpj, e.endereco, e.status, e.data_cadastro,
                 e.observacoes, e.codigo, e.regime_tributario, e.informacoes
        ORDER BY e.nome
    '''), (mes, ano))
    rows = c.fetchall()
    conn.close()
    return rows


def obter_etapas_pendentes_bulk(mes, ano):
    """
    Retorna {empresa_id: [nomes_pendentes]} para TODAS as empresas — UMA query.
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('''
        SELECT et.empresa_id, et.nome
        FROM etapas_empresa et
        LEFT JOIN etapas_status es ON es.etapa_id = et.id
                                  AND es.mes = ? AND es.ano = ?
        WHERE COALESCE(es.concluido, 0) = 0
        ORDER BY et.empresa_id, et.ordem
    '''), (mes, ano))
    rows = c.fetchall()
    conn.close()
    result = {}
    for eid, nome in rows:
        result.setdefault(eid, []).append(nome)
    return result


def buscar_empresas_com_progresso(termo, mes, ano):
    """Busca com progresso em lote."""
    conn = _get_conn()
    c = conn.cursor()
    like = f'%{termo}%'
    c.execute(_adapt_query('''
        SELECT
            e.id, e.nome, e.responsavel, e.email, e.telefone,
            e.cnpj, e.endereco, e.status, e.data_cadastro,
            e.observacoes, e.codigo, e.regime_tributario, e.informacoes,
            COUNT(et.id)                                                        AS total,
            SUM(CASE WHEN COALESCE(es.concluido,0)=1 THEN 1 ELSE 0 END)        AS done
        FROM empresas e
        LEFT JOIN etapas_empresa et ON et.empresa_id = e.id
        LEFT JOIN etapas_status  es ON es.etapa_id   = et.id
                                   AND es.mes = ? AND es.ano = ?
        WHERE e.nome LIKE ? OR e.cnpj LIKE ? OR e.codigo LIKE ?
        GROUP BY e.id, e.nome, e.responsavel, e.email, e.telefone,
                 e.cnpj, e.endereco, e.status, e.data_cadastro,
                 e.observacoes, e.codigo, e.regime_tributario, e.informacoes
        ORDER BY e.nome
    '''), (mes, ano, like, like, like))
    rows = c.fetchall()
    conn.close()
    return rows


def salvar_informacoes(empresa_id, texto):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('UPDATE empresas SET informacoes=? WHERE id=?'), (texto, empresa_id))
    conn.commit()
    conn.close()


def obter_todas_etapas_status_bulk(mes, ano):
    """
    Retorna {empresa_id: {etapa_nome: concluido}} para TODAS as empresas — UMA query.
    Usado nos relatórios para evitar N+1 queries.
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('''
        SELECT et.empresa_id, et.nome, COALESCE(es.concluido, 0)
        FROM etapas_empresa et
        LEFT JOIN etapas_status es ON es.etapa_id = et.id
                                  AND es.mes = ? AND es.ano = ?
        ORDER BY et.empresa_id, et.ordem
    '''), (mes, ano))
    rows = c.fetchall()
    conn.close()
    result = {}
    for eid, nome, done in rows:
        result.setdefault(eid, {})[nome] = bool(done)
    return result


def obter_progresso_anual_bulk(empresa_id, ano):
    """
    Retorna {mes: (pct, done, total)} para todos os 12 meses do ano — UMA query.
    """
    conn = _get_conn()
    c = conn.cursor()
    c.execute(_adapt_query('''
        SELECT s.mes,
               COUNT(e.id)                                                  AS total,
               SUM(CASE WHEN COALESCE(s2.concluido,0)=1 THEN 1 ELSE 0 END) AS done
        FROM etapas_empresa e
        CROSS JOIN (
            SELECT '01' AS mes UNION ALL SELECT '02' UNION ALL SELECT '03' UNION ALL SELECT '04'
            UNION ALL SELECT '05' UNION ALL SELECT '06' UNION ALL SELECT '07' UNION ALL SELECT '08'
            UNION ALL SELECT '09' UNION ALL SELECT '10' UNION ALL SELECT '11' UNION ALL SELECT '12'
        ) AS s
        LEFT JOIN etapas_status s2 ON s2.etapa_id = e.id
                                  AND s2.mes = s.mes AND s2.ano = ?
        WHERE e.empresa_id = ?
        GROUP BY s.mes
        ORDER BY s.mes
    '''), (ano, empresa_id))
    rows = c.fetchall()
    conn.close()
    result = {}
    for mes, total, done in rows:
        pct = round(done / total * 100) if total > 0 else 0
        result[mes] = (pct, done, total)
    return result


def obter_nomes_etapas_distintos():
    """Retorna lista de nomes de etapas únicas ordenadas por frequência de uso."""
    conn = _get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT nome, COUNT(*) AS cnt
        FROM etapas_empresa
        GROUP BY nome
        ORDER BY cnt DESC, nome
    ''')
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def marcar_etapa_bulk(empresa_ids, nome_etapa, mes, ano, concluido: bool):
    """
    Marca a etapa `nome_etapa` como concluído/pendente para todas as empresas
    da lista — em UMA ÚNICA transação.
    Retorna o número de etapas efetivamente marcadas.
    """
    conn = _get_conn()
    c = conn.cursor()
    marcadas = 0
    for eid in empresa_ids:
        c.execute(_adapt_query('SELECT id FROM etapas_empresa WHERE empresa_id=? AND nome=?'), (eid, nome_etapa))
        row = c.fetchone()
        if row:
            if USE_POSTGRES:
                c.execute('''INSERT INTO etapas_status (etapa_id, mes, ano, concluido)
                             VALUES (%s,%s,%s,%s)
                             ON CONFLICT (etapa_id, mes, ano) DO UPDATE SET concluido=%s''',
                          (row[0], mes, ano, int(concluido), int(concluido)))
            else:
                c.execute('''INSERT OR REPLACE INTO etapas_status (etapa_id, mes, ano, concluido)
                             VALUES (?,?,?,?)''', (row[0], mes, ano, int(concluido)))
            marcadas += 1
    conn.commit()
    conn.close()
    return marcadas


def adicionar_etapa_bulk(empresa_ids, nome_etapa):
    """
    Adiciona a etapa `nome_etapa` em todas as empresas da lista.
    Ignora empresas que já possuem uma etapa com esse nome.
    Retorna (adicionadas, ja_existiam).
    """
    conn = _get_conn()
    c = conn.cursor()
    adicionadas = 0
    ja_existiam = 0
    for eid in empresa_ids:
        c.execute(_adapt_query('SELECT COUNT(*) FROM etapas_empresa WHERE empresa_id=? AND nome=?'), (eid, nome_etapa))
        if c.fetchone()[0] > 0:
            ja_existiam += 1
            continue
        c.execute(_adapt_query('SELECT COALESCE(MAX(ordem), -1) + 1 FROM etapas_empresa WHERE empresa_id=?'), (eid,))
        ordem = c.fetchone()[0]
        c.execute(_adapt_query('INSERT INTO etapas_empresa (empresa_id, nome, ordem) VALUES (?,?,?)'),
                  (eid, nome_etapa, ordem))
        adicionadas += 1
    conn.commit()
    conn.close()
    return adicionadas, ja_existiam
