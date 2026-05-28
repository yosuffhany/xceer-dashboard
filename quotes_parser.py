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

    import re

    def _is_valid_date(s):
        """التاريخ لازم يكون YYYY/MM/DD أو YYYY-MM-DD — مش timestamp"""
        return bool(re.match(r'^\d{4}[/-]\d{2}[/-]\d{2}$', s.strip()[:10]))

    def _is_valid_quote_no(s):
        """رقم العرض لازم يكون أرقام فقط"""
        return bool(re.match(r'^\d+$', str(s).strip()))

    records = []
    for _, row in df.iterrows():
        client = str(row.get('العميل', '') or '').strip()
        if not client or client.lower() == 'nan':
            continue

        # تجاهل الصفوف التي يبدو فيها العميل تاريخ أو وقت
        if re.match(r'^\d{4}-\d{2}-\d{2}', client) or re.match(r'^\d{2}:\d{2}', client):
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

        # تجاهل صفوف بدون مبلغ
        if total <= 0:
            continue

        # رقم العرض
        quote_no = str(row.get('رقم العرض', '') or '').strip()

        # المندوب
        rep = str(row.get('مندوب المبيعات', '') or '').strip()
        if not rep or rep.lower() == 'nan':
            rep = 'غير محدد'

        # التاريخ — نأخذ أول 10 حروف فقط (بدون الوقت)
        date_val = str(row.get('التاريخ', '') or '').strip()
        if date_val.lower() == 'nan':
            date_val = ''
        else:
            date_val = date_val[:10]  # YYYY-MM-DD or YYYY/MM/DD فقط

        records.append({
            'quote_no'   : quote_no,
            'order_no'   : order_no,
            'client'     : client,
            'rep'        : rep,
            'total'      : total,
            'date'       : date_val,
            'q_type'     : q_type,
            'is_executed': 0 if order_no == '0' else 1,
        })

    return records
