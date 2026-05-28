"""
parser.py — قراءة ملف Excel من اكسير ERP وتحويله لبيانات منظمة
"""
import pandas as pd
from datetime import datetime

# ── إعدادات الشيتات والأعمدة ────────────────────────────────────────────
SALES_SHEETS      = [('مبيعات اوفست', 'اوفست'), ('مبيعات الديجيتال', 'ديجيتال')]
COLLECT_SHEETS    = [('تحصيلات شبكة', 'شبكة'), ('تحصيلات بنكيه', 'بنكي'), ('تحصيلات نقدي', 'نقدي')]
WO_SHEET          = 'اوامر العمل'

SALES_HEADER_ROW  = 3   # الهيدر في الصف 4 (index 3)
COL_NET           = 'صافي الفاتورة'
COL_TAX           = 'الضريبة'
COL_TOTAL         = 'الاجمالي'
COL_DATE          = 'تاريخ المستند'
COL_CLIENT        = 'اسم العميل'
COL_CLIENT_NO     = 'رقم العميل'
COL_INVOICE_NO    = 'رقم المستند'   # رقم الفاتورة

COLLECT_HEADER_ROW = 4  # الهيدر في الصف 5 (index 4)
COL_AMOUNT        = 'المبلغ'
COL_C_CLIENT      = 'اسم  الجهة'
COL_C_CLIENT_NO   = 'رقم  الجهة'
COL_RECEIPT_NO    = 'رقم السند'     # رقم سند القبض

WO_HEADER_ROW     = 0
COL_WO_CLIENT     = 'العميل'
COL_WO_REP        = 'مندوب المبيعات'
COL_WO_TOTAL      = 'اجمالى الأمر'
COL_WO_DATE       = 'التاريخ'
COL_WO_TYPE       = 'نوع الأمر'

TAX_RATE = 1.15

MONTH_AR = {
    '01': 'يناير', '02': 'فبراير', '03': 'مارس',  '04': 'أبريل',
    '05': 'مايو',  '06': 'يونيو',  '07': 'يوليو', '08': 'أغسطس',
    '09': 'سبتمبر','10': 'أكتوبر', '11': 'نوفمبر', '12': 'ديسمبر'
}

# ── دوال مساعدة ──────────────────────────────────────────────────────────

def parse_date(val):
    """تحويل أي قيمة لـ datetime"""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    if isinstance(val, datetime):
        return val
    if hasattr(val, 'to_pydatetime'):  # pandas Timestamp
        return val.to_pydatetime()
    s = str(val).strip()
    for fmt in ['%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(s, fmt)
        except:
            pass
    return None

def get_month(d):
    """تحويل datetime لـ YYYY-MM"""
    if d is None:
        return None
    return d.strftime('%Y-%m')

def safe_float(val, default=0.0):
    try:
        v = float(str(val).replace(',', ''))
        return v if not pd.isna(v) else default
    except:
        return default

def safe_str(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ''
    return str(val).strip()

# ── قراءة شيت المبيعات ────────────────────────────────────────────────────

def parse_sales(xl, sheet_name, sale_type):
    try:
        df = xl.parse(sheet_name, header=SALES_HEADER_ROW)
    except Exception:
        return []

    records = []
    for _, row in df.iterrows():
        client = safe_str(row.get(COL_CLIENT, ''))
        net    = safe_float(row.get(COL_NET, 0))
        d      = parse_date(row.get(COL_DATE))

        if not client or net == 0 or d is None:
            continue

        # رقم الفاتورة — يجرب عدة أسماء محتملة
        inv_no = safe_str(row.get(COL_INVOICE_NO,
                 row.get('رقم الفاتورة',
                 row.get('رقم المستند', ''))))

        records.append({
            'date'      : d.strftime('%Y-%m-%d'),
            'month'     : get_month(d),
            'client_name': client,
            'client_no' : safe_str(row.get(COL_CLIENT_NO, '')),
            'net'       : round(net, 2),
            'tax'       : round(safe_float(row.get(COL_TAX, 0)), 2),
            'total'     : round(safe_float(row.get(COL_TOTAL, 0)), 2),
            'type'      : sale_type,
            'rep_name'  : '',      # يُضاف لاحقاً من rep_map
            'invoice_no': inv_no,
        })
    return records

# ── قراءة شيت التحصيلات ───────────────────────────────────────────────────

def parse_collections(xl, sheet_name, col_type):
    try:
        df = xl.parse(sheet_name, header=COLLECT_HEADER_ROW)
    except Exception:
        return []

    records = []
    for _, row in df.iterrows():
        client = safe_str(row.get(COL_C_CLIENT, ''))
        amount = safe_float(row.get(COL_AMOUNT, 0))
        d      = parse_date(row.get(COL_DATE))

        if not client or amount == 0 or d is None:
            continue

        # رقم السند — يجرب عدة أسماء محتملة
        rcpt_no = safe_str(row.get(COL_RECEIPT_NO,
                  row.get('رقم سند القبض',
                  row.get('رقم الايصال',
                  row.get('رقم القبض', '')))))

        records.append({
            'date'           : d.strftime('%Y-%m-%d'),
            'month'          : get_month(d),
            'client_name'    : client,
            'client_no'      : safe_str(row.get(COL_C_CLIENT_NO, '')),
            'amount'         : round(amount, 2),
            'net_amount'     : round(amount / TAX_RATE, 2),
            'collection_type': col_type,
            'rep_name'       : '',
            'receipt_no'     : rcpt_no,
        })
    return records

# ── قراءة أوامر العمل + بناء rep_map ────────────────────────────────────────

def parse_work_orders(xl):
    try:
        df = xl.parse(WO_SHEET, header=WO_HEADER_ROW)
    except Exception:
        return [], {}

    records = []
    rep_map = {}

    for _, row in df.iterrows():
        client = safe_str(row.get(COL_WO_CLIENT, ''))
        rep    = safe_str(row.get(COL_WO_REP, ''))
        total  = safe_float(row.get(COL_WO_TOTAL, 0))
        d      = parse_date(row.get(COL_WO_DATE))

        if not client:
            continue

        if rep:
            rep_map[client] = rep

        records.append({
            'date'      : d.strftime('%Y-%m-%d') if d else None,
            'month'     : get_month(d) if d else None,
            'client'    : client,
            'rep_name'  : rep or 'غير محدد',
            'total'     : round(total, 2),
            'order_type': safe_str(row.get(COL_WO_TYPE, ''))
        })

    return records, rep_map

# ── الدالة الرئيسية ───────────────────────────────────────────────────────

def parse_excel_file(file):
    """
    يقرأ ملف Excel من اكسير ويرجع dict فيه:
      sales, collections, work_orders, rep_map
    """
    xl = pd.ExcelFile(file)

    # مبيعات
    sales = []
    for sheet_name, sale_type in SALES_SHEETS:
        if sheet_name in xl.sheet_names:
            sales.extend(parse_sales(xl, sheet_name, sale_type))

    # تحصيلات
    collections = []
    for sheet_name, col_type in COLLECT_SHEETS:
        if sheet_name in xl.sheet_names:
            collections.extend(parse_collections(xl, sheet_name, col_type))

    # أوامر عمل + خريطة المناديب
    work_orders, rep_map = [], {}
    if WO_SHEET in xl.sheet_names:
        work_orders, rep_map = parse_work_orders(xl)

    # ربط المندوبين بالمبيعات والتحصيلات
    for r in sales:
        r['rep_name'] = rep_map.get(r['client_name'], 'غير محدد')
    for r in collections:
        r['rep_name'] = rep_map.get(r['client_name'], 'غير محدد')

    return {
        'sales'      : sales,
        'collections': collections,
        'work_orders': work_orders,
        'rep_map'    : rep_map
    }
