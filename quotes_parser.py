"""
quotes_parser.py — قراءة ملفات العروض من اكسير ERP
الأعمدة: رقم العرض، امر العمل، العميل، مندوب المبيعات، التاريخ، الاجمالى
"""
import pandas as pd


def parse_quotes_file(file, q_type: str) -> list[dict]:
    """
    يقرأ ملف Excel للعروض ويرجع list من الـ records.
    q_type: 'اوفست' أو 'ديجيتال'
    """
    df = pd.read_excel(file)
    # تنظيف أسماء الأعمدة
    df.columns = [str(c).strip() for c in df.columns]

    records = []
    for _, row in df.iterrows():
        client = str(row.get('العميل', '') or '').strip()
        if not client or client.lower() == 'nan':
            continue

        # رقم أمر العمل
        raw_order = row.get('امر العمل', 0)
        try:
            order_no = str(int(float(str(raw_order or 0))))
        except Exception:
            order_no = '0'

        # إجمالي العرض
        raw_total = row.get('الاجمالى', row.get('الاجمالى ', 0))
        try:
            total = float(str(raw_total or 0).replace(',', ''))
        except Exception:
            total = 0.0

        # المندوب
        rep = str(row.get('مندوب المبيعات', '') or '').strip()
        if not rep or rep.lower() == 'nan':
            rep = 'غير محدد'

        # التاريخ
        date_val = str(row.get('التاريخ', '') or '').strip()
        if date_val.lower() == 'nan':
            date_val = ''

        records.append({
            'quote_no'   : str(row.get('رقم العرض', '') or '').strip(),
            'order_no'   : order_no,
            'client'     : client,
            'rep'        : rep,
            'total'      : total,
            'date'       : date_val,
            'q_type'     : q_type,
            'is_executed': 0 if order_no == '0' else 1,
        })

    return records
