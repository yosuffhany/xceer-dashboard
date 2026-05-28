"""
db.py — إدارة قاعدة البيانات
يدعم SQLite محلياً و PostgreSQL/Supabase على النت تلقائياً
"""
import os
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text

# ══════════════════════════════════════════════════════════════
# اختيار قاعدة البيانات تلقائياً
# ══════════════════════════════════════════════════════════════

def _make_engine():
    """
    أولوية الاتصال:
    1) Streamlit Secrets  → DATABASE_URL   (على Streamlit Cloud)
    2) Environment Var    → DATABASE_URL   (أي سيرفر تاني)
    3) SQLite محلي        → xceer_data.db  (جهازك الشخصي)
    """
    # 1) Streamlit Secrets
    try:
        import streamlit as st
        url = st.secrets.get("DATABASE_URL", "")
        if url:
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return create_engine(url, pool_pre_ping=True)
    except Exception:
        pass

    # 2) Environment variable
    url = os.environ.get("DATABASE_URL", "")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return create_engine(url, pool_pre_ping=True)

    # 3) SQLite محلي
    return create_engine("sqlite:///xceer_data.db")


engine = _make_engine()
IS_PG  = engine.dialect.name == "postgresql"

# ══════════════════════════════════════════════════════════════
# إنشاء الجداول
# ══════════════════════════════════════════════════════════════

def init_db():
    pk = "SERIAL PRIMARY KEY" if IS_PG else "INTEGER PRIMARY KEY AUTOINCREMENT"

    ddl = [
        # ── جدول العروض ──────────────────────────────────────────
        f"""CREATE TABLE IF NOT EXISTS quotes (
            id           {pk},
            uploaded_at  TEXT,
            quote_no     TEXT,
            order_no     TEXT,
            client       TEXT,
            rep          TEXT,
            total        REAL,
            date         TEXT,
            q_type       TEXT,
            is_executed  INTEGER DEFAULT 0
        )""",
        "CREATE INDEX IF NOT EXISTS idx_quotes_type ON quotes(q_type)",
    ] + [
        f"""CREATE TABLE IF NOT EXISTS uploads (
            id            {pk},
            filename      TEXT,
            uploaded_at   TEXT,
            months        TEXT,
            sales_count   INTEGER,
            collect_count INTEGER,
            wo_count      INTEGER
        )""",
        f"""CREATE TABLE IF NOT EXISTS sales (
            id          {pk},
            upload_id   INTEGER,
            date        TEXT,
            month       TEXT,
            client_name TEXT,
            client_no   TEXT,
            rep_name    TEXT,
            net         REAL,
            tax         REAL,
            total       REAL,
            type        TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS collections (
            id               {pk},
            upload_id        INTEGER,
            date             TEXT,
            month            TEXT,
            client_name      TEXT,
            client_no        TEXT,
            rep_name         TEXT,
            amount           REAL,
            net_amount       REAL,
            collection_type  TEXT
        )""",
        f"""CREATE TABLE IF NOT EXISTS work_orders (
            id          {pk},
            upload_id   INTEGER,
            date        TEXT,
            month       TEXT,
            client      TEXT,
            rep_name    TEXT,
            total       REAL,
            order_type  TEXT
        )""",
        "CREATE INDEX IF NOT EXISTS idx_sales_month   ON sales(month)",
        "CREATE INDEX IF NOT EXISTS idx_collect_month ON collections(month)",
        "CREATE INDEX IF NOT EXISTS idx_wo_month      ON work_orders(month)",
    ]

    with engine.connect() as conn:
        for stmt in ddl:
            conn.execute(text(stmt))
        conn.commit()

# ══════════════════════════════════════════════════════════════
# حفظ البيانات
# ══════════════════════════════════════════════════════════════

def save_data(data, filename):
    months = set()
    for r in data["sales"]:
        if r.get("month"): months.add(r["month"])
    for r in data["collections"]:
        if r.get("month"): months.add(r["month"])

    with engine.connect() as conn:
        # احذف البيانات القديمة لنفس الأشهر
        for month in months:
            conn.execute(text("DELETE FROM sales       WHERE month = :m"), {"m": month})
            conn.execute(text("DELETE FROM collections WHERE month = :m"), {"m": month})
            conn.execute(text("DELETE FROM work_orders WHERE month = :m"), {"m": month})

        # سجّل الرفع واحصل على upload_id
        now    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        params = dict(
            fn=filename,
            at=now,
            mo=json.dumps(sorted(months)),
            sc=len(data["sales"]),
            cc=len(data["collections"]),
            wc=len(data["work_orders"])
        )
        insert_sql = text("""
            INSERT INTO uploads (filename, uploaded_at, months, sales_count, collect_count, wo_count)
            VALUES (:fn, :at, :mo, :sc, :cc, :wc)
        """)

        if IS_PG:
            result    = conn.execute(text(insert_sql.text + " RETURNING id"), params)
            upload_id = result.fetchone()[0]
        else:
            conn.execute(insert_sql, params)
            upload_id = conn.execute(text("SELECT last_insert_rowid()")).fetchone()[0]

        conn.commit()

    # ── إدخال البيانات بالجملة عبر pandas to_sql ──────────────
    if data["sales"]:
        df = pd.DataFrame([{**r, "upload_id": upload_id} for r in data["sales"]])
        df.to_sql("sales", engine, if_exists="append", index=False)

    if data["collections"]:
        df = pd.DataFrame([{**r, "upload_id": upload_id} for r in data["collections"]])
        df.to_sql("collections", engine, if_exists="append", index=False)

    if data["work_orders"]:
        df = pd.DataFrame([{**r, "upload_id": upload_id} for r in data["work_orders"]])
        df.to_sql("work_orders", engine, if_exists="append", index=False)

    return upload_id, sorted(months)

# ══════════════════════════════════════════════════════════════
# جلب البيانات
# ══════════════════════════════════════════════════════════════

def _filter_clause(from_m, to_m):
    parts, params = [], {}
    if from_m:
        parts.append("month >= :fm")
        params["fm"] = from_m
    if to_m:
        parts.append("month <= :tm")
        params["tm"] = to_m
    clause = ("WHERE " + " AND ".join(parts)) if parts else ""
    return clause, params

def get_available_months():
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT DISTINCT month FROM sales WHERE month IS NOT NULL ORDER BY month"
        )).fetchall()
    return [r[0] for r in rows]

def get_sales(from_m=None, to_m=None):
    clause, params = _filter_clause(from_m, to_m)
    with engine.connect() as conn:
        return pd.read_sql_query(
            text(f"SELECT * FROM sales {clause} ORDER BY date"),
            conn, params=params
        )

def get_collections(from_m=None, to_m=None):
    clause, params = _filter_clause(from_m, to_m)
    with engine.connect() as conn:
        return pd.read_sql_query(
            text(f"SELECT * FROM collections {clause} ORDER BY date"),
            conn, params=params
        )

def get_work_orders(from_m=None, to_m=None):
    clause, params = _filter_clause(from_m, to_m)
    with engine.connect() as conn:
        return pd.read_sql_query(
            text(f"SELECT * FROM work_orders {clause} ORDER BY date"),
            conn, params=params
        )

def get_uploads_history():
    with engine.connect() as conn:
        return pd.read_sql_query(
            text("SELECT * FROM uploads ORDER BY uploaded_at DESC LIMIT 20"),
            conn
        )

def delete_month(month):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM sales       WHERE month = :m"), {"m": month})
        conn.execute(text("DELETE FROM collections WHERE month = :m"), {"m": month})
        conn.execute(text("DELETE FROM work_orders WHERE month = :m"), {"m": month})
        conn.commit()

# ══════════════════════════════════════════════════════════════
# العروض
# ══════════════════════════════════════════════════════════════

def save_quotes(records, q_type):
    """حفظ عروض نوع معين — يحذف القديم أولاً"""
    if not records:
        return 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df  = pd.DataFrame(records)
    df['uploaded_at'] = now
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM quotes WHERE q_type = :qt"), {"qt": q_type})
        conn.commit()
    df.to_sql("quotes", engine, if_exists="append", index=False,
              method="multi", chunksize=500)
    return len(df)

def get_quotes(q_type=None):
    with engine.connect() as conn:
        try:
            if q_type:
                return pd.read_sql_query(
                    text("SELECT * FROM quotes WHERE q_type = :qt ORDER BY date"),
                    conn, params={"qt": q_type}
                )
            return pd.read_sql_query(
                text("SELECT * FROM quotes ORDER BY q_type, date"),
                conn
            )
        except Exception:
            return pd.DataFrame()

def get_all_sales_clients():
    """كل أسماء العملاء اللي عندهم مبيعات — لتحديد المفوتر"""
    with engine.connect() as conn:
        try:
            rows = conn.execute(
                text("SELECT DISTINCT client_name FROM sales")
            ).fetchall()
            return {r[0] for r in rows}
        except Exception:
            return set()
