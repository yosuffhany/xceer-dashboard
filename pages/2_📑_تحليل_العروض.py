"""
pages/2_📑_تحليل_العروض.py — تحليل عروض الأسعار (أوفست + ديجيتال)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from db import init_db, save_quotes, get_quotes, get_all_sales_clients, delete_quotes
from quotes_parser import parse_quotes_file

# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="تحليل العروض — اكسير ERP",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# CSS — نفس تصميم الداشبورد الرئيسي
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Round');

*,*::before,*::after { box-sizing: border-box; }
body,p,h1,h2,h3,h4,h5,h6,label,button,input,select,textarea,
.stMarkdown,.stText,[data-testid="stMarkdownContainer"],
[data-baseweb],.kpi-card,.dash-hdr,.block-container,.stTabs {
  font-family:'Cairo',sans-serif !important;
}
.material-icons,.material-icons-round,[class*="material-icon"] {
  font-family:'Material Icons Round','Material Icons' !important;
}
[data-testid="stExpanderToggleIcon"] { display:none !important }

/* ── زر إعادة فتح الشريط الجانبي ── */
[data-testid="collapsedControl"] {
  background: linear-gradient(180deg,#312E81,#4338CA) !important;
  border-radius: 0 10px 10px 0 !important;
  box-shadow: 3px 0 16px rgba(67,56,202,.55) !important;
  opacity: 1 !important; visibility: visible !important;
  min-width: 28px !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] button,
[data-testid="collapsedControl"] span { color:#fff !important; fill:#fff !important }

.stApp {
  background:linear-gradient(135deg,#EEF2FF 0%,#F0F9FF 50%,#F5F3FF 100%) !important;
  min-height:100vh;
}
.block-container {
  direction:rtl; text-align:right;
  padding-top:1.5rem !important; padding-bottom:3rem !important;
  max-width:1400px !important;
}
#MainMenu,footer,header { visibility:hidden }
.stDeployButton { display:none }

/* Sidebar */
section[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#1E1B4B 0%,#312E81 60%,#4338CA 100%) !important;
  box-shadow:4px 0 30px rgba(30,27,75,.25) !important;
}
section[data-testid="stSidebar"] * { color:#E0E7FF !important }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color:#fff !important }
section[data-testid="stSidebar"] .stButton>button {
  background:rgba(255,255,255,.12) !important;
  border:1px solid rgba(255,255,255,.25) !important;
  color:#fff !important; border-radius:10px !important; width:100% !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
  background:rgba(255,255,255,.08) !important;
  border:2px dashed rgba(255,255,255,.35) !important;
  border-radius:14px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
  background:linear-gradient(135deg,#6366F1,#8B5CF6) !important;
  border:none !important; color:#fff !important;
  border-radius:10px !important; font-weight:700 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"]>div {
  background:rgba(255,255,255,.15) !important;
  border:1.5px solid rgba(255,255,255,.4) !important;
  border-radius:10px !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] div { color:#fff !important }

/* KPI cards */
.kpi-card {
  background:rgba(255,255,255,.78);
  backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
  border-radius:18px; border:1px solid rgba(255,255,255,.9);
  box-shadow:0 4px 24px rgba(79,70,229,.07),inset 0 1px 0 rgba(255,255,255,.8);
  padding:20px 18px 16px; min-height:140px;
  transition:all .35s cubic-bezier(.4,0,.2,1);
  position:relative; overflow:hidden; margin-bottom:4px;
  direction:rtl; text-align:right;
  animation:kpiReveal .55s cubic-bezier(.4,0,.2,1) both;
}
.kpi-card::before {
  content:''; position:absolute; top:0; left:0; right:0;
  height:3px; background:var(--c,#4F46E5);
  border-radius:18px 18px 0 0;
}
.kpi-card:hover { transform:translateY(-5px); box-shadow:0 14px 44px rgba(79,70,229,.13) }
.kpi-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:10px }
.kpi-icon-box {
  width:40px; height:40px; background:var(--c,#4F46E5);
  border-radius:12px; display:flex; align-items:center;
  justify-content:center; font-size:17px;
}
.kpi-badge { font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px }
.bg{background:#D1FAE5;color:#065F46}.by{background:#FEF3C7;color:#92400E}
.br{background:#FEE2E2;color:#991B1B}.bb{background:#EDE9FE;color:#5B21B6}
.bc{background:#CFFAFE;color:#164E63}.bv{background:#F3E8FF;color:#6B21A8}
.kpi-lbl { font-size:11px; color:#9CA3AF; font-weight:600; margin-bottom:4px }
.kpi-num { font-size:24px; font-weight:900; color:var(--c,#1E1B4B); line-height:1.1; margin-bottom:5px;
  animation:numPop .6s cubic-bezier(.4,0,.2,1) .2s both; }
.kpi-foot { font-size:11px; color:#9CA3AF }

@keyframes kpiReveal {
  from{opacity:0;transform:translateY(10px) scale(.97)}
  to{opacity:1;transform:translateY(0) scale(1)}
}
@keyframes numPop {
  0%{opacity:0;transform:scale(.7)} 70%{transform:scale(1.08)} 100%{opacity:1;transform:scale(1)}
}

/* Section header */
.s-hdr { display:flex; align-items:center; gap:12px; margin:28px 0 18px; direction:rtl }
.s-dot { width:5px; height:26px; border-radius:3px; flex-shrink:0 }
.s-txt { font-size:15px; font-weight:800; color:#1E1B4B }
.s-line { flex:1; height:1px; background:linear-gradient(90deg,rgba(79,70,229,.15),transparent) }

/* Dash header */
.dash-hdr {
  background:linear-gradient(135deg,#1E1B4B 0%,#4338CA 55%,#7C3AED 100%);
  border-radius:20px; padding:24px 32px; margin-bottom:24px;
  box-shadow:0 10px 40px rgba(67,56,202,.35); direction:rtl;
}
.dash-hdr-title { font-size:22px; font-weight:900; color:#fff; margin:0 0 5px }
.dash-hdr-sub { font-size:13px; color:rgba(255,255,255,.75); margin:0 0 12px }
.dash-pills { display:flex; gap:8px; flex-wrap:wrap }
.dash-pill {
  background:rgba(255,255,255,.15); backdrop-filter:blur(10px);
  border:1px solid rgba(255,255,255,.25); border-radius:20px;
  padding:4px 14px; font-size:11px; color:#fff; font-weight:600;
}

/* Tables */
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="columnheader"] {
  text-align:center !important; justify-content:center !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  background:rgba(255,255,255,.6) !important; backdrop-filter:blur(10px) !important;
  border-radius:12px !important; padding:4px !important; gap:4px !important;
  border:1px solid rgba(255,255,255,.8) !important;
}
.stTabs [data-baseweb="tab"] {
  background:transparent !important; border-radius:9px !important;
  color:#6B7280 !important; font-weight:600 !important; font-size:13px !important;
}
.stTabs [aria-selected="true"] { background:#4F46E5 !important; color:#fff !important }

/* Dropdown */
[data-baseweb="popover"] ul {
  background:#1E1B4B !important; border-radius:12px !important; padding:4px !important;
}
[data-baseweb="popover"] [role="option"] {
  color:#fff !important; font-family:'Cairo',sans-serif !important;
  font-weight:600 !important; border-radius:8px !important;
}
[data-baseweb="popover"] [role="option"]:hover { background:rgba(99,102,241,.5) !important }
[data-baseweb="popover"] [aria-selected="true"] { background:#4F46E5 !important }

@media screen and (max-width:900px) {
  [data-testid="column"] { min-width:calc(50% - .5rem) !important; flex:1 1 calc(50% - .5rem) !important }
}
@media screen and (max-width:640px) {
  [data-testid="column"] { min-width:100% !important; flex:1 1 100% !important }
  .block-container { padding:.75rem .5rem !important }
  .kpi-num { font-size:20px }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════════════════════
def fmt(n):
    try:
        return f'{round(float(n)):,}'
    except Exception:
        return '—'

def pct(a, b):
    return round(a / b * 100, 1) if b else 0.0

def kpi_card(label, value, icon, color, foot, badge=None, btype='bb', is_pct=False):
    if is_pct:
        display = f'{value:.1f}٪'
    elif isinstance(value, float) or isinstance(value, int):
        display = fmt(value)
    else:
        display = str(value)
    bdg = f'<span class="kpi-badge {btype}">{badge}</span>' if badge else ''
    return f"""<div class="kpi-card" style="--c:{color}">
  <div class="kpi-top"><div class="kpi-icon-box">{icon}</div>{bdg}</div>
  <div class="kpi-lbl">{label}</div>
  <div class="kpi-num">{display}</div>
  <div class="kpi-foot">{foot}</div>
</div>"""

def sec_hdr(text, icon, color='#4F46E5'):
    return (f'<div class="s-hdr">'
            f'<div class="s-dot" style="background:{color}"></div>'
            f'<div class="s-txt">{icon} {text}</div>'
            f'<div class="s-line"></div></div>')

def bar_chart(df, x_col, y_cols, names, colors, title, height=340):
    fig = go.Figure()
    for col, name, color in zip(y_cols, names, colors):
        fig.add_trace(go.Bar(
            x=df[x_col], y=df[col], name=name,
            marker_color=color, opacity=0.85,
            text=df[col].apply(fmt), textposition='outside',
            textfont=dict(size=9, family='Cairo')
        ))
    fig.update_layout(
        height=height, barmode='group',
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=-0.18, font=dict(family='Cairo', size=12),
                    bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(tickfont=dict(family='Cairo', size=10, color='#374151'), showgrid=False),
        yaxis=dict(tickformat=',.0f', tickfont=dict(family='Cairo', size=10, color='#9CA3AF'),
                   gridcolor='rgba(79,70,229,0.07)'),
        font=dict(family='Cairo'),
        title=dict(text=title, font=dict(family='Cairo', size=13, color='#374151'),
                   x=0.5, xanchor='center')
    )
    return fig

def hbar_chart(df, y_col, x_cols, names, colors, height=None):
    h = height or max(300, len(df) * 45)
    fig = go.Figure()
    for col, name, color in zip(x_cols, names, colors):
        fig.add_trace(go.Bar(
            y=df[y_col], x=df[col], name=name, orientation='h',
            marker_color=color, opacity=0.85,
            text=df[col].apply(fmt), textposition='outside',
            textfont=dict(size=9, family='Cairo')
        ))
    fig.update_layout(
        height=h, barmode='group',
        margin=dict(l=10, r=80, t=20, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=-0.12, font=dict(family='Cairo', size=11),
                    bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(tickformat=',.0f', tickfont=dict(family='Cairo', size=9, color='#9CA3AF'),
                   gridcolor='rgba(79,70,229,0.07)'),
        yaxis=dict(tickfont=dict(family='Cairo', size=11, color='#374151')),
        font=dict(family='Cairo')
    )
    return fig

# ══════════════════════════════════════════════════════════════
init_db()

# ══════════════════════════════════════════════════════════════
# القائمة الجانبية
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📑 تحليل العروض")
    st.markdown('<hr style="border-color:rgba(255,255,255,.15);margin:8px 0 14px">', unsafe_allow_html=True)

    # ══ الفلاتر أولاً ══════════════════════════════════════════
    st.markdown("### 🔍 الفلاتر")

    # فلتر النوع
    type_filter = st.selectbox('القسم:', ['الكل', 'اوفست فقط', 'ديجيتال فقط'], key='qt_filter')

    # فلتر الحالة
    status_filter = st.selectbox('الحالة:', ['الكل', 'غير منفذة', 'منفذة', 'منفذة - مفوترة', 'منفذة - غير مفوترة'],
                                  key='qs_filter')

    # فلتر الشهر + العميل + المندوب — نجلب الخيارات من DB
    _df_opts = get_quotes()
    if not _df_opts.empty:
        # شهور متاحة (YYYY-MM)
        _df_opts['_m'] = _df_opts['date'].astype(str).str[:7]
        _all_months  = sorted([m for m in _df_opts['_m'].dropna().unique() if len(m) == 7], reverse=True)
        _all_clients = sorted(_df_opts['client'].dropna().unique().tolist())
        _all_reps    = sorted([r for r in _df_opts['rep'].dropna().unique().tolist() if r and r != 'غير محدد'])

        month_ms  = st.multiselect('📅 الشهر:', _all_months,  key='q_month_ms',
                                    placeholder='كل الشهور...')
        client_ms = st.multiselect('🏢 العميل:', _all_clients, key='q_client_ms',
                                    placeholder='كل العملاء...')
        rep_ms    = st.multiselect('👤 المندوب:', _all_reps,   key='q_rep_ms',
                                    placeholder='كل المناديب...')
    else:
        month_ms = client_ms = rep_ms = []

    st.markdown('<hr style="border-color:rgba(255,255,255,.15);margin:14px 0 10px">', unsafe_allow_html=True)

    # حذف العروض
    with st.expander('🗑 إدارة البيانات'):
        del_type = st.selectbox('النوع:', ['الكل', 'اوفست فقط', 'ديجيتال فقط'], key='q_del_type')
        if st.button('🗑 مسح العروض المختارة', type='secondary', key='q_del_btn'):
            qt = None if del_type == 'الكل' else del_type.replace(' فقط', '')
            delete_quotes(qt)
            st.success('✅ تم الحذف بنجاح')
            st.rerun()

    # ══ رفع الملفات (في الأسفل) ════════════════════════════════
    st.markdown('<hr style="border-color:rgba(255,255,255,.15);margin:14px 0 10px">', unsafe_allow_html=True)
    st.markdown("### 📂 رفع الملفات")

    st.markdown("**🖨 عروض أوفست**")
    off_file = st.file_uploader("ملف عروض أوفست", type=['xlsx', 'xls'], key='q_off',
                                 help="ملف العروض الخاص بقسم الأوفست")
    if off_file:
        with st.spinner('⏳ جاري المعالجة...'):
            try:
                recs = parse_quotes_file(off_file, 'اوفست')
                cnt  = save_quotes(recs, 'اوفست')
                st.success(f'✅ تم رفع {cnt:,} عرض أوفست')
                st.rerun()
            except Exception as e:
                st.error(f'❌ خطأ: {e}')

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown("**📱 عروض ديجيتال**")
    dig_file = st.file_uploader("ملف عروض ديجيتال", type=['xlsx', 'xls'], key='q_dig',
                                 help="ملف العروض الخاص بقسم الديجيتال")
    if dig_file:
        with st.spinner('⏳ جاري المعالجة...'):
            try:
                recs = parse_quotes_file(dig_file, 'ديجيتال')
                cnt  = save_quotes(recs, 'ديجيتال')
                st.success(f'✅ تم رفع {cnt:,} عرض ديجيتال')
                st.rerun()
            except Exception as e:
                st.error(f'❌ خطأ: {e}')

# ══════════════════════════════════════════════════════════════
# تحميل البيانات
# ══════════════════════════════════════════════════════════════
df_q = get_quotes()

if df_q.empty:
    st.markdown("""
    <div style='text-align:center;padding:100px 20px;direction:rtl'>
      <div style='font-size:72px;margin-bottom:20px'>📑</div>
      <h1 style='color:#1E1B4B;font-family:Cairo,sans-serif;font-size:28px;margin-bottom:12px'>
        تحليل عروض الأسعار</h1>
      <p style='font-size:17px;color:#6B7280;font-family:Cairo,sans-serif'>
        ارفع ملفات العروض من القائمة الجانبية للبدء</p>
      <p style='font-size:13px;color:#9CA3AF;font-family:Cairo,sans-serif'>
        رفع ملف أوفست + ملف ديجيتال لرؤية التحليل الكامل</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# تحديد العملاء المفوترين (عندهم مبيعات في النظام)
invoiced_clients = get_all_sales_clients()

# إضافة عمود المفوتر
df_q['is_invoiced'] = df_q.apply(
    lambda r: 1 if (r['is_executed'] == 1 and r['client'] in invoiced_clients) else 0,
    axis=1
)

# تطبيق فلتر النوع
if type_filter == 'اوفست فقط':
    df_q = df_q[df_q['q_type'] == 'اوفست']
elif type_filter == 'ديجيتال فقط':
    df_q = df_q[df_q['q_type'] == 'ديجيتال']

# تطبيق فلتر الحالة
if status_filter == 'غير منفذة':
    df_q = df_q[df_q['is_executed'] == 0]
elif status_filter == 'منفذة':
    df_q = df_q[df_q['is_executed'] == 1]
elif status_filter == 'منفذة - مفوترة':
    df_q = df_q[(df_q['is_executed'] == 1) & (df_q['is_invoiced'] == 1)]
elif status_filter == 'منفذة - غير مفوترة':
    df_q = df_q[(df_q['is_executed'] == 1) & (df_q['is_invoiced'] == 0)]

# تطبيق فلتر الشهر / العميل / المندوب
month_ms  = st.session_state.get('q_month_ms',  [])
client_ms = st.session_state.get('q_client_ms', [])
rep_ms    = st.session_state.get('q_rep_ms',    [])
if month_ms:
    df_q = df_q[df_q['date'].astype(str).str[:7].isin(month_ms)]
if client_ms:
    df_q = df_q[df_q['client'].isin(client_ms)]
if rep_ms:
    df_q = df_q[df_q['rep'].isin(rep_ms)]

# ══════════════════════════════════════════════════════════════
# حسابات الملخص (على الكل بدون فلتر الحالة)
# ══════════════════════════════════════════════════════════════
df_all = get_quotes()
df_all['is_invoiced'] = df_all.apply(
    lambda r: 1 if (r['is_executed'] == 1 and r['client'] in invoiced_clients) else 0,
    axis=1
)
if type_filter == 'اوفست فقط':
    df_all = df_all[df_all['q_type'] == 'اوفست']
elif type_filter == 'ديجيتال فقط':
    df_all = df_all[df_all['q_type'] == 'ديجيتال']
if month_ms:
    df_all = df_all[df_all['date'].astype(str).str[:7].isin(month_ms)]
if client_ms:
    df_all = df_all[df_all['client'].isin(client_ms)]
if rep_ms:
    df_all = df_all[df_all['rep'].isin(rep_ms)]

total_cnt   = len(df_all)
exec_cnt    = int(df_all['is_executed'].sum())
unexec_cnt  = total_cnt - exec_cnt
total_val   = df_all['total'].sum()
exec_val    = df_all[df_all['is_executed'] == 1]['total'].sum()
unexec_val  = df_all[df_all['is_executed'] == 0]['total'].sum()
inv_cnt     = int(df_all['is_invoiced'].sum())
uninv_cnt   = exec_cnt - inv_cnt
inv_val     = df_all[df_all['is_invoiced'] == 1]['total'].sum()
uninv_val   = df_all[(df_all['is_executed'] == 1) & (df_all['is_invoiced'] == 0)]['total'].sum()
exec_rate   = pct(exec_cnt, total_cnt)
inv_rate    = pct(inv_cnt, exec_cnt)

off_cnt     = len(df_all[df_all['q_type'] == 'اوفست'])
dig_cnt     = len(df_all[df_all['q_type'] == 'ديجيتال'])

# ══════════════════════════════════════════════════════════════
# رأس الصفحة
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="dash-hdr">
  <div class="dash-hdr-title">📑 تحليل عروض الأسعار</div>
  <div class="dash-hdr-sub">أوفست + ديجيتال — تحليل التنفيذ والفوترة</div>
  <div class="dash-pills">
    <span class="dash-pill">📊 إجمالي: {total_cnt:,} عرض</span>
    <span class="dash-pill">🖨 أوفست: {off_cnt:,}</span>
    <span class="dash-pill">📱 ديجيتال: {dig_cnt:,}</span>
    <span class="dash-pill">✅ تنفيذ: {exec_rate:.1f}٪</span>
    <span class="dash-pill">💰 قيمة: {fmt(total_val)} ر.س</span>
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# مؤشرات الأداء — صف 1: التنفيذ
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('مؤشرات التنفيذ', '🎯', '#4F46E5'), unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card(
        'إجمالي العروض', total_cnt, '📑', '#4F46E5',
        f'قيمة: {fmt(total_val)} ر.س',
        badge=f'{off_cnt} أوفست | {dig_cnt} ديجيتال', btype='bb'
    ), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card(
        'العروض المنفذة', exec_cnt, '✅', '#10B981',
        f'قيمة: {fmt(exec_val)} ر.س',
        badge=f'{exec_rate:.1f}٪ من الإجمالي', btype='bg'
    ), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card(
        'العروض غير المنفذة', unexec_cnt, '⏳', '#EF4444',
        f'قيمة: {fmt(unexec_val)} ر.س',
        badge=f'{pct(unexec_cnt, total_cnt):.1f}٪ من الإجمالي', btype='br'
    ), unsafe_allow_html=True)
with c4:
    clr = '#10B981' if exec_rate >= 65 else '#F59E0B' if exec_rate >= 40 else '#EF4444'
    st.markdown(kpi_card(
        'نسبة التنفيذ', exec_rate, '📊', clr,
        '✅ ممتاز' if exec_rate >= 65 else '⚠️ متوسط' if exec_rate >= 40 else '❌ ضعيف',
        badge=f'{exec_rate:.1f}٪',
        btype='bg' if exec_rate >= 65 else 'by' if exec_rate >= 40 else 'br',
        is_pct=True
    ), unsafe_allow_html=True)

st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# مؤشرات الأداء — صف 2: الفوترة (من المنفذة)
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('مؤشرات الفوترة (من المنفذة)', '💰', '#059669'), unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.markdown(kpi_card(
        'المنفذة المفوترة', inv_cnt, '🧾', '#059669',
        f'قيمة: {fmt(inv_val)} ر.س',
        badge=f'{inv_rate:.1f}٪ من المنفذة', btype='bg'
    ), unsafe_allow_html=True)
with d2:
    st.markdown(kpi_card(
        'المنفذة غير المفوترة', uninv_cnt, '📋', '#F59E0B',
        f'قيمة: {fmt(uninv_val)} ر.س',
        badge=f'{pct(uninv_cnt, exec_cnt):.1f}٪ من المنفذة', btype='by'
    ), unsafe_allow_html=True)
with d3:
    st.markdown(kpi_card(
        'قيمة المنفذة المفوترة', inv_val, '💵', '#059669',
        f'{inv_rate:.1f}٪ من قيمة المنفذة', btype='bg'
    ), unsafe_allow_html=True)
with d4:
    st.markdown(kpi_card(
        'قيمة غير المفوترة', uninv_val, '⚠️', '#F59E0B',
        'فرصة فوترة متاحة', btype='by'
    ), unsafe_allow_html=True)

st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# التحليل بالقسم (أوفست / ديجيتال)
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('التحليل بالقسم', '🏭', '#0EA5E9'), unsafe_allow_html=True)

by_type = (df_all.groupby('q_type').agg(
    إجمالي=('total', 'count'),
    منفذة=('is_executed', 'sum'),
    مفوترة=('is_invoiced', 'sum'),
    قيمة_إجمالية=('total', 'sum'),
).reset_index())
by_type['غير منفذة'] = by_type['إجمالي'] - by_type['منفذة']
by_type['غير مفوترة'] = by_type['منفذة'] - by_type['مفوترة']
by_type['نسبة التنفيذ'] = by_type.apply(lambda r: pct(r['منفذة'], r['إجمالي']), axis=1)
by_type['نسبة الفوترة'] = by_type.apply(lambda r: pct(r['مفوترة'], r['منفذة']), axis=1)

col_t1, col_t2 = st.columns(2)
with col_t1:
    fig_type = bar_chart(
        by_type, 'q_type',
        ['منفذة', 'غير منفذة'],
        ['منفذة', 'غير منفذة'],
        ['#10B981', '#EF4444'],
        'التنفيذ بالقسم (عدد)', height=300
    )
    st.plotly_chart(fig_type, use_container_width=True, key='ch_type_exec')
with col_t2:
    fig_inv = bar_chart(
        by_type, 'q_type',
        ['مفوترة', 'غير مفوترة'],
        ['مفوترة', 'غير مفوترة'],
        ['#059669', '#F59E0B'],
        'الفوترة بالقسم (من المنفذة)', height=300
    )
    st.plotly_chart(fig_inv, use_container_width=True, key='ch_type_inv')

# جدول ملخص القسم
type_disp = by_type.copy()
type_disp.columns = ['القسم', 'الإجمالي', 'منفذة', 'مفوترة', 'القيمة الإجمالية', 'غير منفذة', 'غير مفوترة', 'نسبة التنفيذ', 'نسبة الفوترة']
type_disp['القيمة الإجمالية'] = type_disp['القيمة الإجمالية'].apply(lambda x: f'{x:,.0f}')
type_disp['نسبة التنفيذ'] = type_disp['نسبة التنفيذ'].apply(lambda x: f'{x:.1f}٪')
type_disp['نسبة الفوترة'] = type_disp['نسبة الفوترة'].apply(lambda x: f'{x:.1f}٪')
type_disp = type_disp[['القسم', 'الإجمالي', 'منفذة', 'غير منفذة', 'نسبة التنفيذ', 'مفوترة', 'غير مفوترة', 'نسبة الفوترة', 'القيمة الإجمالية']]
type_disp.index = range(1, len(type_disp)+1)
st.dataframe(type_disp, use_container_width=True, height=130,
    column_config={c: st.column_config.TextColumn(c, width='medium') for c in type_disp.columns})

# ══════════════════════════════════════════════════════════════
# التحليل بالمندوب
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('التحليل بالمندوب', '👥', '#7C3AED'), unsafe_allow_html=True)

by_rep = (df_all.groupby('rep').agg(
    إجمالي=('total', 'count'),
    منفذة=('is_executed', 'sum'),
    مفوترة=('is_invoiced', 'sum'),
    قيمة=('total', 'sum'),
).reset_index())
by_rep['غير منفذة'] = by_rep['إجمالي'] - by_rep['منفذة']
by_rep['غير مفوترة'] = by_rep['منفذة'] - by_rep['مفوترة']
by_rep['نسبة التنفيذ'] = by_rep.apply(lambda r: pct(r['منفذة'], r['إجمالي']), axis=1)
by_rep = by_rep[by_rep['rep'] != 'غير محدد'].sort_values('إجمالي', ascending=False).head(15)

tab_r1, tab_r2 = st.tabs(['📊 شارت التنفيذ', '📋 جدول المناديب'])
with tab_r1:
    fig_rep = hbar_chart(
        by_rep.sort_values('إجمالي'), 'rep',
        ['منفذة', 'غير منفذة', 'مفوترة'],
        ['منفذة', 'غير منفذة', 'مفوترة'],
        ['#10B981', '#EF4444', '#059669'],
        height=max(350, len(by_rep) * 50)
    )
    st.plotly_chart(fig_rep, use_container_width=True, key='ch_rep')

with tab_r2:
    rep_disp = by_rep[['rep', 'إجمالي', 'منفذة', 'غير منفذة', 'نسبة التنفيذ', 'مفوترة', 'غير مفوترة', 'قيمة']].copy()
    rep_disp.columns = ['المندوب', 'الإجمالي', 'منفذة', 'غير منفذة', 'نسبة التنفيذ', 'مفوترة', 'غير مفوترة', 'القيمة (ر.س)']
    rep_disp['القيمة (ر.س)'] = rep_disp['القيمة (ر.س)'].apply(lambda x: f'{x:,.0f}')
    rep_disp['نسبة التنفيذ'] = rep_disp['نسبة التنفيذ'].apply(lambda x: f'{x:.1f}٪')
    rep_disp.index = range(1, len(rep_disp)+1)
    st.dataframe(rep_disp, use_container_width=True, height=420,
        column_config={
            'المندوب'       : st.column_config.TextColumn('المندوب',       width='medium'),
            'الإجمالي'      : st.column_config.TextColumn('الإجمالي',      width='small'),
            'منفذة'         : st.column_config.TextColumn('منفذة',         width='small'),
            'غير منفذة'     : st.column_config.TextColumn('غير منفذة',     width='small'),
            'نسبة التنفيذ'  : st.column_config.TextColumn('نسبة التنفيذ',  width='small'),
            'مفوترة'        : st.column_config.TextColumn('مفوترة',        width='small'),
            'غير مفوترة'    : st.column_config.TextColumn('غير مفوترة',    width='small'),
            'القيمة (ر.س)'  : st.column_config.TextColumn('القيمة (ر.س)',  width='medium'),
        })

# ══════════════════════════════════════════════════════════════
# التحليل بالعميل (Top 20)
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('التحليل بالعميل — أعلى 20', '🏢', '#0D9488'), unsafe_allow_html=True)

by_client = (df_all.groupby('client').agg(
    إجمالي=('total', 'count'),
    منفذة=('is_executed', 'sum'),
    مفوترة=('is_invoiced', 'sum'),
    قيمة=('total', 'sum'),
).reset_index())
by_client['غير منفذة'] = by_client['إجمالي'] - by_client['منفذة']
by_client['نسبة التنفيذ'] = by_client.apply(lambda r: pct(r['منفذة'], r['إجمالي']), axis=1)
by_client = by_client.sort_values('قيمة', ascending=False).head(20)

tab_c1, tab_c2 = st.tabs(['📊 شارت العملاء', '📋 جدول العملاء'])
with tab_c1:
    top10 = by_client.head(10).sort_values('قيمة')
    fig_cl = go.Figure()
    fig_cl.add_trace(go.Bar(
        y=top10['client'], x=top10['منفذة'], name='منفذة', orientation='h',
        marker_color='#10B981', opacity=0.85,
        text=top10['منفذة'].apply(str), textposition='outside',
        textfont=dict(size=9, family='Cairo')
    ))
    fig_cl.add_trace(go.Bar(
        y=top10['client'], x=top10['غير منفذة'], name='غير منفذة', orientation='h',
        marker_color='#EF4444', opacity=0.85,
        text=top10['غير منفذة'].apply(str), textposition='outside',
        textfont=dict(size=9, family='Cairo')
    ))
    fig_cl.update_layout(
        height=max(320, len(top10)*45), barmode='group',
        margin=dict(l=10, r=80, t=15, b=10),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=-0.12, font=dict(family='Cairo', size=11)),
        xaxis=dict(tickformat=',.0f', gridcolor='rgba(79,70,229,.07)',
                   tickfont=dict(family='Cairo', size=9, color='#9CA3AF')),
        yaxis=dict(tickfont=dict(family='Cairo', size=10, color='#374151')),
        font=dict(family='Cairo')
    )
    st.plotly_chart(fig_cl, use_container_width=True, key='ch_client')

with tab_c2:
    cl_disp = by_client[['client', 'إجمالي', 'منفذة', 'غير منفذة', 'نسبة التنفيذ', 'مفوترة', 'قيمة']].copy()
    cl_disp.columns = ['العميل', 'الإجمالي', 'منفذة', 'غير منفذة', 'نسبة التنفيذ', 'مفوترة', 'القيمة (ر.س)']
    cl_disp['القيمة (ر.س)'] = cl_disp['القيمة (ر.س)'].apply(lambda x: f'{x:,.0f}')
    cl_disp['نسبة التنفيذ'] = cl_disp['نسبة التنفيذ'].apply(lambda x: f'{x:.1f}٪')
    cl_disp.index = range(1, len(cl_disp)+1)

    cl_event = st.dataframe(cl_disp, use_container_width=True, height=460,
        on_select='rerun', selection_mode='single-row',
        column_config={
            'العميل'        : st.column_config.TextColumn('العميل',        width='large'),
            'الإجمالي'      : st.column_config.TextColumn('الإجمالي',      width='small'),
            'منفذة'         : st.column_config.TextColumn('منفذة',         width='small'),
            'غير منفذة'     : st.column_config.TextColumn('غير منفذة',     width='small'),
            'نسبة التنفيذ'  : st.column_config.TextColumn('نسبة التنفيذ',  width='small'),
            'مفوترة'        : st.column_config.TextColumn('مفوترة',        width='small'),
            'القيمة (ر.س)'  : st.column_config.TextColumn('القيمة (ر.س)', width='medium'),
        })
    if cl_event.selection.rows:
        sel_cl = cl_disp.iloc[cl_event.selection.rows[0]]['العميل']
        st.session_state['q_client'] = sel_cl
        st.info(f'🔍 اختيار: **{sel_cl}** — التفاصيل أدناه ↓')

# ══════════════════════════════════════════════════════════════
# استعراض عميل بالتفصيل
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('استعراض عميل بالتفصيل', '🔍', '#4338CA'), unsafe_allow_html=True)

all_clients = sorted(df_all['client'].unique().tolist())
if all_clients:
    sel_detail = st.selectbox('🏢 اختر العميل:', all_clients, key='q_client')
    cl_data = df_all[df_all['client'] == sel_detail]

    c_tot   = len(cl_data)
    c_exec  = int(cl_data['is_executed'].sum())
    c_unex  = c_tot - c_exec
    c_inv   = int(cl_data['is_invoiced'].sum())
    c_uninv = c_exec - c_inv
    c_val   = cl_data['total'].sum()
    c_rate  = pct(c_exec, c_tot)
    c_clr   = '#10B981' if c_rate >= 65 else '#F59E0B' if c_rate >= 40 else '#EF4444'

    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.markdown(kpi_card('إجمالي العروض', c_tot, '📑', '#4338CA',
            f'قيمة: {fmt(c_val)} ر.س', badge=sel_detail[:20], btype='bb'), unsafe_allow_html=True)
    with e2:
        st.markdown(kpi_card('منفذة', c_exec, '✅', '#10B981',
            f'{c_rate:.1f}٪ من الإجمالي', badge=f'{c_rate:.0f}٪', btype='bg'), unsafe_allow_html=True)
    with e3:
        st.markdown(kpi_card('غير منفذة', c_unex, '⏳', '#EF4444',
            f'{pct(c_unex,c_tot):.1f}٪ من الإجمالي', badge='متبقية', btype='br'), unsafe_allow_html=True)
    with e4:
        st.markdown(kpi_card('مفوترة من المنفذة', c_inv, '🧾', '#059669',
            f'غير مفوترة: {c_uninv}', badge=f'{pct(c_inv,c_exec):.0f}٪' if c_exec else '—', btype='bg'), unsafe_allow_html=True)

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    et1, et2, et3 = st.tabs(['✅ المنفذة', '⏳ غير المنفذة', '📋 الكل'])
    for tab_label, mask, tab_key in [
        ('✅ المنفذة',      cl_data['is_executed'] == 1,  'exec'),
        ('⏳ غير المنفذة',  cl_data['is_executed'] == 0,  'unex'),
        ('📋 الكل',         pd.Series([True]*len(cl_data), index=cl_data.index), 'all'),
    ]:
        pass  # placeholder — handled below

    with et1:
        sub = cl_data[cl_data['is_executed'] == 1][['quote_no','order_no','q_type','total','date','rep','is_invoiced']].copy()
        sub['is_invoiced'] = sub['is_invoiced'].map({1: '✅ مفوتر', 0: '⏳ غير مفوتر'})
        sub.columns = ['رقم العرض','امر العمل','القسم','الإجمالي','التاريخ','المندوب','حالة الفوترة']
        sub['الإجمالي'] = sub['الإجمالي'].apply(lambda x: f'{x:,.0f}')
        sub.index = range(1, len(sub)+1)
        st.caption(f'✅ {len(sub):,} عرض منفذ — قيمة: {fmt(cl_data[cl_data["is_executed"]==1]["total"].sum())} ر.س')
        st.dataframe(sub, use_container_width=True, height=300,
            column_config={c: st.column_config.TextColumn(c, width='medium') for c in sub.columns})

    with et2:
        sub = cl_data[cl_data['is_executed'] == 0][['quote_no','q_type','total','date','rep']].copy()
        sub.columns = ['رقم العرض','القسم','الإجمالي','التاريخ','المندوب']
        sub['الإجمالي'] = sub['الإجمالي'].apply(lambda x: f'{x:,.0f}')
        sub.index = range(1, len(sub)+1)
        st.caption(f'⏳ {len(sub):,} عرض غير منفذ — قيمة: {fmt(cl_data[cl_data["is_executed"]==0]["total"].sum())} ر.س')
        st.dataframe(sub, use_container_width=True, height=300,
            column_config={c: st.column_config.TextColumn(c, width='medium') for c in sub.columns})

    with et3:
        sub = cl_data[['quote_no','order_no','q_type','total','date','rep','is_executed','is_invoiced']].copy()
        sub['is_executed'] = sub['is_executed'].map({1: '✅ منفذ', 0: '⏳ غير منفذ'})
        sub['is_invoiced']  = sub['is_invoiced'].map({1: '🧾 مفوتر', 0: '—'})
        sub.columns = ['رقم العرض','امر العمل','القسم','الإجمالي','التاريخ','المندوب','التنفيذ','الفوترة']
        sub['الإجمالي'] = sub['الإجمالي'].apply(lambda x: f'{x:,.0f}')
        sub = sub.sort_values('التاريخ', ascending=False)
        sub.index = range(1, len(sub)+1)
        st.dataframe(sub, use_container_width=True, height=360,
            column_config={c: st.column_config.TextColumn(c, width='medium') for c in sub.columns})

# ══════════════════════════════════════════════════════════════
# جدول البيانات الكامل مع الفلتر
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('جدول البيانات الكاملة', '📋', '#6366F1'), unsafe_allow_html=True)

full = df_q[['quote_no','order_no','q_type','client','rep','total','date','is_executed','is_invoiced']].copy()
full['is_executed'] = full['is_executed'].map({1: '✅ منفذ', 0: '⏳ غير منفذ'})
full['is_invoiced']  = full['is_invoiced'].map({1: '🧾 مفوتر', 0: '—'})
full.columns = ['رقم العرض','امر العمل','القسم','العميل','المندوب','الإجمالي','التاريخ','التنفيذ','الفوترة']
full['الإجمالي'] = full['الإجمالي'].apply(lambda x: f'{x:,.0f}')
full = full.sort_values('التاريخ', ascending=False).reset_index(drop=True)
full.index = range(1, len(full)+1)

st.caption(f'إجمالي {len(full):,} سجل — يعكس الفلتر المختار في الشريط الجانبي')
st.dataframe(full, use_container_width=True, height=480,
    column_config={
        'رقم العرض': st.column_config.TextColumn('رقم العرض', width='medium'),
        'امر العمل' : st.column_config.TextColumn('امر العمل', width='medium'),
        'القسم'     : st.column_config.TextColumn('القسم',     width='small'),
        'العميل'    : st.column_config.TextColumn('العميل',    width='large'),
        'المندوب'   : st.column_config.TextColumn('المندوب',   width='medium'),
        'الإجمالي'  : st.column_config.TextColumn('الإجمالي (ر.س)', width='medium'),
        'التاريخ'   : st.column_config.TextColumn('التاريخ',   width='small'),
        'التنفيذ'   : st.column_config.TextColumn('التنفيذ',   width='small'),
        'الفوترة'   : st.column_config.TextColumn('الفوترة',   width='small'),
    })

# الذيل
st.markdown("""
<hr style='margin-top:40px;border-color:rgba(79,70,229,.1)'>
<p style='text-align:center;color:#9CA3AF;font-size:11px;font-family:Cairo,sans-serif;direction:rtl;padding:8px'>
  تحليل العروض — اكسير ERP | المفوتر = العملاء الموجودين في سجلات المبيعات
</p>""", unsafe_allow_html=True)
