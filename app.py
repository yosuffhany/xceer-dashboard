"""
app.py — داشبورد اكسير ERP | Premium Glass Edition
تصميم زجاجي فاخر — متجاوب بالكامل — أرقام متحركة
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from parser import parse_excel_file
from db import (init_db, save_data, get_available_months,
                get_sales, get_collections, get_work_orders,
                get_uploads_history, delete_month)

# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Dashboard 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons|Material+Icons+Round|Material+Icons+Outlined');

/* أساسيات — نطبق Cairo على المحتوى فقط وليس على أيقونات Streamlit */
*,*::before,*::after { box-sizing: border-box; }

body, p, h1,h2,h3,h4,h5,h6,
label, button, input, select, textarea,
.stMarkdown, .stText, .stAlert,
.stSelectbox, .stFileUploader label,
[class*="css-"], [data-testid="stMarkdownContainer"],
[data-testid="stText"], [data-baseweb],
.kpi-card, .dash-hdr, .amt-glass, .s-hdr,
.block-container, .stTabs {
  font-family: 'Cairo', sans-serif !important;
}

/* الحفاظ على خط أيقونات Streamlit */
.material-icons,
.material-icons-round,
.material-icons-outlined,
[class*="material-icon"] {
  font-family: 'Material Icons Round', 'Material Icons' !important;
}

/* إخفاء نصوص الأيقونات التي تظهر كلمات */
[data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child,
[data-testid="stExpanderToggleIcon"],
section[data-testid="stSidebar"] [data-testid="stExpanderToggleIcon"] {
  display: none !important;
}
.stApp {
  background: linear-gradient(135deg,#EEF2FF 0%,#F0F9FF 50%,#F5F3FF 100%) !important;
  min-height: 100vh;
}
.block-container {
  direction: rtl;
  text-align: right;
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1400px !important;
}
#MainMenu, footer, header { visibility: hidden }
.stDeployButton { display: none }

/* منطقة رفع الملف */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
  background: rgba(255,255,255,.08) !important;
  border: 2px dashed rgba(255,255,255,.35) !important;
  border-radius: 14px !important;
  transition: all .3s ease !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]:hover {
  background: rgba(255,255,255,.15) !important;
  border-color: rgba(255,255,255,.6) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
  background: linear-gradient(135deg,#6366F1,#8B5CF6) !important;
  border: none !important;
  color: #fff !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  padding: 8px 20px !important;
  box-shadow: 0 4px 15px rgba(99,102,241,.4) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
  background: linear-gradient(135deg,#4F46E5,#7C3AED) !important;
  box-shadow: 0 6px 20px rgba(99,102,241,.5) !important;
  transform: translateY(-1px) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] {
  color: rgba(255,255,255,.6) !important;
}

/* القائمة الجانبية */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#1E1B4B 0%,#312E81 60%,#4338CA 100%) !important;
  box-shadow: 4px 0 30px rgba(30,27,75,.25) !important;
  border-right: none !important;
}
section[data-testid="stSidebar"] * { color: #E0E7FF !important }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #fff !important }
section[data-testid="stSidebar"] .stButton > button {
  background: rgba(255,255,255,.12) !important;
  border: 1px solid rgba(255,255,255,.25) !important;
  color: #fff !important;
  border-radius: 10px !important;
  width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,.22) !important;
}

/* Selectbox في الـ Sidebar */
section[data-testid="stSidebar"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
  background: rgba(255,255,255,.15) !important;
  border: 1.5px solid rgba(255,255,255,.4) !important;
  border-radius: 10px !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] div {
  color: #ffffff !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] svg {
  fill: rgba(255,255,255,.8) !important;
}
/* Dropdown list */
[data-baseweb="popover"] ul {
  background: #1E1B4B !important;
  border: 1px solid rgba(255,255,255,.25) !important;
  border-radius: 12px !important;
  padding: 4px !important;
}
[data-baseweb="popover"] [role="option"] {
  color: #ffffff !important;
  font-family: 'Cairo', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
  margin: 2px 0 !important;
}
[data-baseweb="popover"] [role="option"]:hover {
  background: rgba(99,102,241,.5) !important;
  color: #fff !important;
}
[data-baseweb="popover"] [aria-selected="true"] {
  background: #4F46E5 !important;
  color: #fff !important;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: rgba(255,255,255,.08) !important;
  border: 1px solid rgba(255,255,255,.15) !important;
  border-radius: 12px !important;
}

/* إصلاح نص arrow_right */
[data-testid="stExpander"] details summary span[data-testid="stExpanderToggleIcon"] { display:none }

/* رأس الداشبورد */
.dash-hdr {
  background: linear-gradient(135deg,#1E1B4B 0%,#4338CA 55%,#7C3AED 100%);
  border-radius: 20px;
  padding: 24px 32px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(67,56,202,.35);
}
.dash-hdr::before {
  content: '';
  position: absolute; top: -60px; right: -40px;
  width: 240px; height: 240px;
  background: rgba(255,255,255,.06);
  border-radius: 50%; pointer-events: none;
}
.dash-hdr::after {
  content: '';
  position: absolute; bottom: -80px; left: 5%;
  width: 200px; height: 200px;
  background: rgba(255,255,255,.04);
  border-radius: 50%; pointer-events: none;
}
.dash-hdr-title {
  font-size: 22px; font-weight: 900; color: #fff;
  margin: 0 0 5px; direction: rtl; text-align: right;
}
.dash-hdr-sub {
  font-size: 13px; color: rgba(255,255,255,.75);
  margin: 0 0 12px; direction: rtl; text-align: right;
}
.dash-pills { display: flex; gap: 8px; flex-wrap: wrap; direction: rtl }
.dash-pill {
  background: rgba(255,255,255,.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,.25);
  border-radius: 20px;
  padding: 4px 14px; font-size: 11px; color: #fff; font-weight: 600;
}

/* بطاقة المؤشر */
.kpi-card {
  background: rgba(255,255,255,.75);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,.9);
  box-shadow: 0 4px 24px rgba(79,70,229,.07), 0 1px 4px rgba(0,0,0,.03),
              inset 0 1px 0 rgba(255,255,255,.8);
  padding: 20px 18px 16px;
  min-height: 140px;
  transition: all .35s cubic-bezier(.4,0,.2,1);
  position: relative; overflow: hidden; margin-bottom: 4px;
  direction: rtl; text-align: right;
}
.kpi-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px; background: var(--c,#4F46E5);
  border-radius: 18px 18px 0 0;
}
.kpi-card::after {
  content: '';
  position: absolute; top: -20px; left: -20px;
  width: 80px; height: 80px; background: var(--c,#4F46E5);
  opacity: .05; border-radius: 50%; pointer-events: none;
}
.kpi-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 14px 44px rgba(79,70,229,.13), 0 4px 14px rgba(0,0,0,.07);
}
.kpi-top {
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 10px;
}
.kpi-icon-box {
  width: 40px; height: 40px; background: var(--c,#4F46E5);
  border-radius: 12px; display: flex; align-items: center;
  justify-content: center; font-size: 17px;
  box-shadow: 0 4px 12px rgba(0,0,0,.15);
}
.kpi-badge {
  font-size: 10px; font-weight: 700;
  padding: 3px 9px; border-radius: 20px;
}
.bg { background: #D1FAE5; color: #065F46 }
.by { background: #FEF3C7; color: #92400E }
.br { background: #FEE2E2; color: #991B1B }
.bb { background: #EDE9FE; color: #5B21B6 }
.bc { background: #CFFAFE; color: #164E63 }
.kpi-lbl {
  font-size: 11px; color: #9CA3AF; font-weight: 600;
  margin-bottom: 4px;
}
.kpi-num {
  font-size: 24px; font-weight: 900;
  color: var(--c,#1E1B4B); line-height: 1.1; margin-bottom: 5px;
}
.kpi-foot { font-size: 11px; color: #9CA3AF }

/* عنوان القسم */
.s-hdr {
  display: flex; align-items: center;
  gap: 12px; margin: 28px 0 18px;
  direction: rtl;
}
.s-dot { width: 5px; height: 26px; border-radius: 3px; flex-shrink: 0 }
.s-txt { font-size: 15px; font-weight: 800; color: #1E1B4B }
.s-line {
  flex: 1; height: 1px;
  background: linear-gradient(90deg,rgba(79,70,229,.15),transparent);
}

/* بطاقة المبلغ */
.amt-glass {
  background: rgba(255,255,255,.8);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-radius: 14px; border: 1.5px solid;
  box-shadow: 0 4px 16px rgba(0,0,0,.06);
  padding: 12px 16px; text-align: center;
  margin-top: 8px; transition: all .3s ease;
  direction: rtl;
}
.amt-glass:hover { transform: translateY(-2px) }
.amt-m { font-size: 15px; font-weight: 800; margin-bottom: 2px }
.amt-s { font-size: 11px; color: #9CA3AF }

/* أنيميشن ظهور البطاقات */
@keyframes kpiReveal {
  from { opacity: 0; transform: translateY(10px) scale(.97); }
  to   { opacity: 1; transform: translateY(0)    scale(1); }
}
.kpi-card { animation: kpiReveal .55s cubic-bezier(.4,0,.2,1) both; }
.kpi-card:nth-child(2) { animation-delay: .07s }
.kpi-card:nth-child(3) { animation-delay: .14s }
.kpi-card:nth-child(4) { animation-delay: .21s }

/* أنيميشن الرقم */
@keyframes numPop {
  0%   { opacity: 0; transform: scale(.7); }
  70%  { transform: scale(1.08); }
  100% { opacity: 1; transform: scale(1); }
}
.kpi-num { animation: numPop .6s cubic-bezier(.4,0,.2,1) .2s both; }

/* إطار العداد */
.g-wrap {
  background: rgba(255,255,255,.7);
  backdrop-filter: blur(16px);
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,.85);
  box-shadow: 0 4px 24px rgba(0,0,0,.05);
  padding: 10px;
}

/* التبويبات */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,.6) !important;
  backdrop-filter: blur(10px) !important;
  border-radius: 12px !important;
  padding: 4px !important; gap: 4px !important;
  border: 1px solid rgba(255,255,255,.8) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: 9px !important;
  color: #6B7280 !important;
  font-weight: 600 !important; font-size: 13px !important;
}
.stTabs [aria-selected="true"] {
  background: #4F46E5 !important; color: #fff !important;
}

/* الجداول — توسيط كامل */
.stDataFrame { direction: rtl }
[data-testid="stDataFrame"] [role="gridcell"],
[data-testid="stDataFrame"] [role="columnheader"] {
  text-align: center !important;
  justify-content: center !important;
}
[data-testid="stDataFrame"] [role="gridcell"] > div,
[data-testid="stDataFrame"] [role="columnheader"] > div,
[data-testid="stDataFrame"] [role="gridcell"] span,
[data-testid="stDataFrame"] [role="columnheader"] span {
  text-align: center !important;
  justify-content: center !important;
  display: flex !important;
  align-items: center !important;
  width: 100% !important;
}

/* متجاوب */
@media screen and (max-width: 900px) {
  [data-testid="column"] {
    min-width: calc(50% - .5rem) !important;
    flex: 1 1 calc(50% - .5rem) !important;
    width: calc(50% - .5rem) !important;
  }
}
@media screen and (max-width: 640px) {
  [data-testid="column"] {
    min-width: 100% !important;
    flex: 1 1 100% !important;
    width: 100% !important;
  }
  .block-container { padding: .75rem .5rem !important }
  .kpi-num { font-size: 20px }
  .dash-hdr { padding: 16px 18px }
  .dash-hdr-title { font-size: 17px }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════════════════════
MONTH_AR = {
    '01':'يناير','02':'فبراير','03':'مارس','04':'أبريل',
    '05':'مايو','06':'يونيو','07':'يوليو','08':'أغسطس',
    '09':'سبتمبر','10':'أكتوبر','11':'نوفمبر','12':'ديسمبر'
}

def month_label(m):
    if not m or '-' not in m: return m or ''
    p = m.split('-')
    return MONTH_AR.get(p[1], p[1]) + ' ' + p[0]

def fmt(n): return f'{round(n):,}'

def fmt_short(n):
    """تنسيق مختصر: ألف / مليون"""
    if n >= 1_000_000:
        return f'{n/1_000_000:.1f} م'
    if n >= 1_000:
        return f'{n/1_000:.0f} ألف'
    return f'{round(n):,}'

def kpi_card(label, value, icon, color, foot, badge=None, btype='bb', is_pct=False):
    """بطاقة KPI مع CSS animation — بدون JS لضمان الظهور الصحيح في Streamlit"""
    if is_pct:
        display_val = f'{value:.1f}٪'
    else:
        display_val = fmt(round(value))
    bdg = f'<span class="kpi-badge {btype}">{badge}</span>' if badge else ''
    return f"""<div class="kpi-card" style="--c:{color}">
  <div class="kpi-top"><div class="kpi-icon-box">{icon}</div>{bdg}</div>
  <div class="kpi-lbl">{label}</div>
  <div class="kpi-num">{display_val}</div>
  <div class="kpi-foot">{foot}</div>
</div>"""

def sec_hdr(text, icon, color='#4F46E5'):
    return (f'<div class="s-hdr">'
            f'<div class="s-dot" style="background:{color}"></div>'
            f'<div class="s-txt">{icon} {text}</div>'
            f'<div class="s-line"></div></div>')

def make_gauge(value, title, color):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=round(value, 1),
        title={'text': title, 'font': {'size': 13, 'family': 'Cairo', 'color': '#374151'}},
        number={'suffix': '%', 'font': {'size': 36, 'family': 'Cairo', 'color': color}},
        gauge={
            'axis': {
                'range': [0, 100], 'tickwidth': 1,
                'tickfont': {'size': 9, 'color': '#9CA3AF', 'family': 'Cairo'},
                'tickcolor': '#E5E7EB', 'nticks': 6,
                'tickformat': '.0f'
            },
            'bar': {'color': color, 'thickness': 0.22},
            'bgcolor': 'rgba(0,0,0,0)', 'borderwidth': 0,
            'steps': [
                {'range': [0,  40], 'color': 'rgba(239,68,68,0.08)'},
                {'range': [40, 65], 'color': 'rgba(245,158,11,0.08)'},
                {'range': [65,100], 'color': 'rgba(16,185,129,0.08)'}
            ],
            'threshold': {
                'line': {'color': color, 'width': 4},
                'thickness': 0.9, 'value': value
            }
        }
    ))
    fig.update_layout(
        height=220,
        margin=dict(l=25, r=25, t=45, b=5),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='Cairo'
    )
    return fig

def make_monthly_chart(df_s, df_c):
    ms = (df_s.groupby('month')['net'].sum().reset_index()
          .rename(columns={'net':'مبيعات'}) if not df_s.empty
          else pd.DataFrame(columns=['month','مبيعات']))
    mc = (df_c.groupby('month')['net_amount'].sum().reset_index()
          .rename(columns={'net_amount':'تحصيل'}) if not df_c.empty
          else pd.DataFrame(columns=['month','تحصيل']))
    m = pd.merge(ms, mc, on='month', how='outer').fillna(0).sort_values('month')
    m['label'] = m['month'].apply(month_label)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=m['label'], y=m['مبيعات'], name='المبيعات',
        marker=dict(color='#4F46E5', opacity=0.85),
        text=m['مبيعات'].apply(fmt_short),
        textposition='outside',
        textfont=dict(size=9, color='#4F46E5', family='Cairo')
    ))
    fig.add_trace(go.Scatter(
        x=m['label'], y=m['تحصيل'], name='التحصيل',
        mode='lines+markers',
        line=dict(color='#10B981', width=3, shape='spline', smoothing=0.8),
        marker=dict(size=8, color='#10B981', line=dict(color='white', width=2))
    ))
    fig.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h', y=-0.18, font_size=13,
            bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo')
        ),
        xaxis=dict(
            showgrid=False, tickfont_size=11,
            tickfont_color='#6B7280',
            tickfont=dict(family='Cairo')
        ),
        yaxis=dict(
            gridcolor='rgba(79,70,229,0.07)',
            tickformat=',.0f', tickfont_size=10,
            tickfont_color='#9CA3AF',
            tickfont=dict(family='Cairo')
        ),
        font=dict(family='Cairo'),
        barmode='group'
    )
    return fig

def make_reps_chart(reps_df):
    if reps_df.empty: return None
    top = reps_df.head(10).sort_values('total_sales')
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top['rep_name'], x=top['total_sales'],
        name='المبيعات', orientation='h',
        marker=dict(color='#4F46E5', opacity=0.85),
        text=top['total_sales'].apply(fmt_short),
        textposition='outside',
        textfont=dict(size=10, family='Cairo')
    ))
    fig.add_trace(go.Bar(
        y=top['rep_name'], x=top['total_collect'],
        name='التحصيل', orientation='h',
        marker=dict(color='#10B981', opacity=0.85),
        text=top['total_collect'].apply(fmt_short),
        textposition='outside',
        textfont=dict(size=10, family='Cairo')
    ))
    fig.update_layout(
        height=max(300, len(top)*38),
        barmode='group',
        margin=dict(l=10, r=80, t=15, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h', y=-0.12, font_size=12,
            bgcolor='rgba(0,0,0,0)',
            font=dict(family='Cairo')
        ),
        xaxis=dict(
            gridcolor='rgba(79,70,229,0.07)',
            tickformat=',.0f', tickfont_size=10,
            tickfont_color='#9CA3AF',
            tickfont=dict(family='Cairo')
        ),
        yaxis=dict(
            tickfont_size=12, tickfont_color='#374151',
            tickfont=dict(family='Cairo')
        ),
        font=dict(family='Cairo')
    )
    return fig

def calc_reps(df_s, df_c, nm):
    if df_s.empty: return pd.DataFrame()
    reps = df_s.groupby('rep_name')['net'].sum().reset_index()
    reps.columns = ['rep_name','total_sales']
    off = (df_s[df_s['type'].str.contains('وفست', na=False)]
           .groupby('rep_name')['net'].sum().reset_index()
           .rename(columns={'net':'off_sales'}))
    reps = pd.merge(reps, off, on='rep_name', how='left').fillna(0)
    reps['dig_sales'] = reps['total_sales'] - reps['off_sales']
    if not df_c.empty:
        col = df_c.groupby('rep_name')['net_amount'].sum().reset_index()
        col.columns = ['rep_name','total_collect']
        reps = pd.merge(reps, col, on='rep_name', how='left').fillna(0)
    else:
        reps['total_collect'] = 0
    reps = reps[reps['rep_name'] != 'غير محدد']
    reps = reps[reps['total_sales'] > 0]
    reps['collect_rate'] = (reps['total_collect'] / reps['total_sales'] * 100).round(1)
    reps['avg_sales']    = (reps['total_sales']   / max(nm,1)).round(0)
    reps['avg_collect']  = (reps['total_collect'] / max(nm,1)).round(0)
    return reps.sort_values('total_sales', ascending=False).reset_index(drop=True)

# ══════════════════════════════════════════════════════════════
init_db()

# ══════════════════════════════════════════════════════════════
# القائمة الجانبية
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📊 Dashboard 2026")
    st.markdown(
        '<hr style="border-color:rgba(255,255,255,.15);margin:8px 0 16px">',
        unsafe_allow_html=True
    )
    st.markdown("### 📁 رفع ملف شهري")
    uploaded = st.file_uploader(
        "اختر ملف Excel من اكسير",
        type=['xlsx','xls'],
        help="ملف متابعة المبيعات الشهري"
    )
    if uploaded:
        with st.spinner('⏳ جاري معالجة الملف...'):
            try:
                data = parse_excel_file(uploaded)
                uid2, months_covered = save_data(data, uploaded.name)
                months_ar = [month_label(m) for m in months_covered]
                st.success(
                    f"✅ **تم الرفع بنجاح!**\n\n"
                    f"📊 مبيعات: **{len(data['sales']):,}** سجل\n"
                    f"💰 تحصيلات: **{len(data['collections']):,}** سجل\n"
                    f"📋 أوامر عمل: **{len(data['work_orders']):,}** أمر\n"
                    f"📅 الأشهر: **{' | '.join(months_ar)}**"
                )
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ في معالجة الملف:\n{str(e)}")

    st.markdown(
        '<hr style="border-color:rgba(255,255,255,.15);margin:16px 0">',
        unsafe_allow_html=True
    )
    available = get_available_months()
    if available:
        st.markdown("### 🗓 فلتر الفترة")
        from_m = st.selectbox("من شهر:", available, index=0,
                               format_func=month_label)
        to_m   = st.selectbox("إلى شهر:", available,
                               index=len(available)-1, format_func=month_label)
        period_label = f"من {month_label(from_m)} إلى {month_label(to_m)}"
    else:
        from_m = to_m = None
        period_label  = "لا توجد بيانات"

    st.markdown(
        '<hr style="border-color:rgba(255,255,255,.15);margin:16px 0">',
        unsafe_allow_html=True
    )
    with st.expander("📋 سجل الرفع"):
        hist = get_uploads_history()
        if not hist.empty:
            for _, row in hist.iterrows():
                st.markdown(f"**📄 {row['filename']}**")
                st.caption(f"🕐 {row['uploaded_at'][:16]}")
                st.markdown("---")
        else:
            st.info("لا يوجد سجل حتى الآن")

    with st.expander("🗑 حذف بيانات شهر"):
        if available:
            del_m = st.selectbox("اختر الشهر:", available,
                                  format_func=month_label, key='del')
            if st.button("🗑 حذف هذا الشهر", type="secondary"):
                delete_month(del_m)
                st.success(f"✅ تم حذف {month_label(del_m)}")
                st.rerun()

# ══════════════════════════════════════════════════════════════
# الشاشة الفارغة
# ══════════════════════════════════════════════════════════════
if not available:
    st.markdown("""
    <div style='text-align:center;padding:100px 20px;direction:rtl'>
      <div style='font-size:72px;margin-bottom:20px'>📊</div>
      <h1 style='color:#1E1B4B;font-family:Cairo,sans-serif;
                 font-size:28px;margin-bottom:12px'>داشبورد اكسير ERP</h1>
      <p style='font-size:17px;color:#6B7280;font-family:Cairo,sans-serif'>
        ارفع ملف الإكسل الشهري من القائمة الجانبية للبدء</p>
      <p style='font-size:13px;color:#9CA3AF;font-family:Cairo,sans-serif'>
        الداشبورد يتراكم ويحفظ التاريخ كله — كل شهر ترفع ملف جديد</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
# تحميل البيانات والحسابات
# ══════════════════════════════════════════════════════════════
df_s = get_sales(from_m, to_m)
df_c = get_collections(from_m, to_m)
df_w = get_work_orders(from_m, to_m)

tot_s = df_s['net'].sum()         if not df_s.empty else 0.0
off_s = (df_s[df_s['type'].str.contains('وفست', na=False)]['net'].sum()
         if not df_s.empty else 0.0)
dig_s = tot_s - off_s
tot_c = df_c['net_amount'].sum()  if not df_c.empty else 0.0
tot_w = len(df_w)
rate  = (tot_c / tot_s * 100)    if tot_s > 0 else 0.0
off_p = (off_s / tot_s * 100)    if tot_s > 0 else 0.0
dig_p = (dig_s / tot_s * 100)    if tot_s > 0 else 0.0
nm    = max(df_s['month'].nunique() if not df_s.empty else 1, 1)
avg_s = tot_s / nm
avg_c = tot_c / nm

rc = '#10B981' if rate >= 65 else '#F59E0B' if rate >= 40 else '#EF4444'
rt = '✅ أداء ممتاز' if rate >= 65 else '⚠️ أداء متوسط' if rate >= 40 else '❌ يحتاج متابعة'
rb = 'bg' if rate >= 65 else 'by' if rate >= 40 else 'br'

# ══════════════════════════════════════════════════════════════
# رأس الصفحة
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="dash-hdr">
  <div class="dash-hdr-title">📊 Dashboard 2026</div>
  <div class="dash-hdr-sub">لوحة تحكم المبيعات والتحصيلات</div>
  <div class="dash-pills">
    <span class="dash-pill">📅 {period_label}</span>
    <span class="dash-pill">🗓 {nm} شهر</span>
    <span class="dash-pill">💰 مبيعات: {fmt(tot_s)} ر.س</span>
    <span class="dash-pill">✅ تحصيل: {fmt(tot_c)} ر.س</span>
    <span class="dash-pill">{rt}</span>
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# بطاقات المؤشرات — صف أول
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('المؤشرات المالية الرئيسية', '💰', '#4F46E5'),
            unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(kpi_card(
        'إجمالي المبيعات', tot_s, '💰', '#4F46E5',
        'ريال سعودي', badge=f'{nm} شهر', btype='bb'
    ), unsafe_allow_html=True)
with c2:
    st.markdown(kpi_card(
        'مبيعات الأوفست', off_s, '🖨', '#0EA5E9',
        f'{off_p:.1f}٪ من الإجمالي', badge='أوفست', btype='bc'
    ), unsafe_allow_html=True)
with c3:
    st.markdown(kpi_card(
        'مبيعات الديجيتال', dig_s, '📱', '#7C3AED',
        f'{dig_p:.1f}٪ من الإجمالي', badge='ديجيتال', btype='bb'
    ), unsafe_allow_html=True)
with c4:
    st.markdown(kpi_card(
        'التحصيل من إجمالي المبيعات', tot_c, '✅', rc,
        f'نسبة التحصيل {rate:.1f}٪', badge=rt, btype=rb
    ), unsafe_allow_html=True)

st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# بطاقات المؤشرات — صف ثاني
# ══════════════════════════════════════════════════════════════
c5, c6, c7, c8 = st.columns(4)
with c5:
    st.markdown(kpi_card(
        'أوامر العمل', tot_w, '📋', '#0D9488',
        'أمر عمل مسجّل', badge='الإجمالي', btype='bc'
    ), unsafe_allow_html=True)
with c6:
    st.markdown(kpi_card(
        'نسبة التحصيل', rate, '📊', rc,
        rt, badge=f'{rate:.1f}٪', btype=rb, is_pct=True
    ), unsafe_allow_html=True)
with c7:
    st.markdown(kpi_card(
        'متوسط المبيعات شهرياً', avg_s, '📈', '#059669',
        'ريال سعودي / شهر', badge='متوسط', btype='bg'
    ), unsafe_allow_html=True)
with c8:
    st.markdown(kpi_card(
        'متوسط التحصيل شهرياً', avg_c, '💵', '#0891B2',
        'ريال سعودي / شهر', badge='متوسط', btype='bc'
    ), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# مؤشرات الأداء (العدادات)
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('مؤشرات الأداء', '🎯', '#7C3AED'), unsafe_allow_html=True)
g1, g2, g3 = st.columns(3)

with g1:
    st.markdown('<div class="g-wrap">', unsafe_allow_html=True)
    st.plotly_chart(make_gauge(rate, 'نسبة التحصيل', rc),
                    use_container_width=True, key='g1')
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="amt-glass" style="border-color:{rc}">
      <div class="amt-m" style="color:{rc}">{fmt(tot_c)} ر.س من {fmt(tot_s)} ر.س</div>
      <div class="amt-s">صافي التحصيل من إجمالي المبيعات</div>
    </div>""", unsafe_allow_html=True)

with g2:
    st.markdown('<div class="g-wrap">', unsafe_allow_html=True)
    st.plotly_chart(make_gauge(off_p, 'نسبة الأوفست', '#0EA5E9'),
                    use_container_width=True, key='g2')
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="amt-glass" style="border-color:#0EA5E9">
      <div class="amt-m" style="color:#0EA5E9">{fmt(off_s)} ر.س من {fmt(tot_s)} ر.س</div>
      <div class="amt-s">مبيعات الأوفست من إجمالي المبيعات</div>
    </div>""", unsafe_allow_html=True)

with g3:
    st.markdown('<div class="g-wrap">', unsafe_allow_html=True)
    st.plotly_chart(make_gauge(dig_p, 'نسبة الديجيتال', '#7C3AED'),
                    use_container_width=True, key='g3')
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="amt-glass" style="border-color:#7C3AED">
      <div class="amt-m" style="color:#7C3AED">{fmt(dig_s)} ر.س من {fmt(tot_s)} ر.س</div>
      <div class="amt-s">مبيعات الديجيتال من إجمالي المبيعات</div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# الشارت الشهري
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('المبيعات والتحصيلات الشهرية', '📈', '#059669'),
            unsafe_allow_html=True)
st.plotly_chart(make_monthly_chart(df_s, df_c),
                use_container_width=True, key='monthly')

# ══════════════════════════════════════════════════════════════
# أداء المناديب
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('أداء المناديب', '👥', '#0D9488'), unsafe_allow_html=True)
reps = calc_reps(df_s, df_c, nm)
if not reps.empty:
    tab1, tab2 = st.tabs(["📊 شارت المناديب", "📋 جدول المناديب"])
    with tab1:
        fig_r = make_reps_chart(reps)
        if fig_r:
            st.plotly_chart(fig_r, use_container_width=True, key='reps')
    with tab2:
        disp = reps[['rep_name','off_sales','dig_sales','total_sales',
                     'total_collect','collect_rate','avg_sales','avg_collect']].copy()
        disp.index = range(1, len(disp)+1)
        disp.columns = [
            'المندوب', 'أوفست', 'ديجيتال', 'الإجمالي',
            'التحصيل', 'النسبة ٪', 'متوسط مبيعات', 'متوسط تحصيل'
        ]
        # أرقام كاملة مع فاصل الآلاف
        for col in ['أوفست','ديجيتال','الإجمالي','التحصيل','متوسط مبيعات','متوسط تحصيل']:
            disp[col] = disp[col].apply(lambda x: f'{x:,.0f}')
        disp['النسبة ٪'] = disp['النسبة ٪'].apply(lambda x: f'{x:.1f}٪')

        st.caption('👆 انقر على أي صف أو رقم لعرض تفاصيل المندوب تلقائياً أدناه')
        tbl_event = st.dataframe(
            disp,
            use_container_width=True,
            height=420,
            on_select='rerun',
            selection_mode='single-row',
            column_config={
                'المندوب'      : st.column_config.TextColumn('المندوب',      width='medium'),
                'أوفست'        : st.column_config.TextColumn('أوفست (ر.س)', width='medium'),
                'ديجيتال'      : st.column_config.TextColumn('ديجيتال (ر.س)',width='medium'),
                'الإجمالي'     : st.column_config.TextColumn('الإجمالي (ر.س)',width='medium'),
                'التحصيل'      : st.column_config.TextColumn('التحصيل (ر.س)',width='medium'),
                'النسبة ٪'     : st.column_config.TextColumn('النسبة ٪',     width='small'),
                'متوسط مبيعات' : st.column_config.TextColumn('متوسط مبيعات',width='medium'),
                'متوسط تحصيل'  : st.column_config.TextColumn('متوسط تحصيل', width='medium'),
            }
        )
        # لما المستخدم يضغط على صف → اكتب مباشرةً على مفتاح الـ selectbox
        if tbl_event.selection.rows:
            clicked_name = disp.iloc[tbl_event.selection.rows[0]]['المندوب']
            st.session_state['rep_detail'] = clicked_name   # ← نفس key الـ selectbox
            st.info(f'🔍 تم اختيار **{clicked_name}** — انتقل لأسفل لرؤية التفاصيل ↓')
else:
    st.info("لا توجد بيانات مناديب للفترة المختارة")

# ══════════════════════════════════════════════════════════════
# استعراض مندوب — تفصيلي
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('استعراض مندوب بالتفصيل', '🔍', '#7C3AED'), unsafe_allow_html=True)

if not df_s.empty:
    rep_list = sorted([r for r in df_s['rep_name'].unique() if r and r != 'غير محدد'])
    if rep_list:
        sel_rep = st.selectbox(
            '👤 اختر المندوب (أو اضغط على أي صف في الجدول أعلاه):',
            rep_list, key='rep_detail'
        )

        rep_s = df_s[df_s['rep_name'] == sel_rep].copy()
        rep_c = df_c[df_c['rep_name'] == sel_rep].copy() if not df_c.empty else pd.DataFrame()

        r_tot_s   = rep_s['net'].sum()
        r_tot_c   = rep_c['net_amount'].sum() if not rep_c.empty else 0.0
        r_uncoll  = max(r_tot_s - r_tot_c, 0)
        r_rate    = (r_tot_c / r_tot_s * 100) if r_tot_s > 0 else 0.0
        r_color   = '#10B981' if r_rate >= 65 else '#F59E0B' if r_rate >= 40 else '#EF4444'

        # بطاقات ملخص المندوب
        ra, rb, rc2, rd = st.columns(4)
        with ra:
            st.markdown(kpi_card(
                'إجمالي المبيعات', r_tot_s, '💰', '#4F46E5',
                'ريال سعودي', badge=f'{len(rep_s):,} حركة', btype='bb'
            ), unsafe_allow_html=True)
        with rb:
            st.markdown(kpi_card(
                'صافي التحصيل', r_tot_c, '✅', r_color,
                f'نسبة {r_rate:.1f}٪',
                badge='✅ ممتاز' if r_rate >= 65 else '⚠️ متوسط' if r_rate >= 40 else '❌ ضعيف',
                btype='bg' if r_rate >= 65 else 'by' if r_rate >= 40 else 'br'
            ), unsafe_allow_html=True)
        with rc2:
            st.markdown(kpi_card(
                'المتبقي غير محصّل', r_uncoll, '⏳', '#F59E0B',
                'ريال سعودي', badge='متبقي', btype='by'
            ), unsafe_allow_html=True)
        with rd:
            st.markdown(kpi_card(
                'نسبة التحصيل', r_rate, '📊', r_color,
                '', badge=f'{r_rate:.1f}٪', btype='bg' if r_rate >= 65 else 'by' if r_rate >= 40 else 'br',
                is_pct=True
            ), unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        # تبويبات التفاصيل
        t1, t2, t3 = st.tabs(['📋 حركات المبيعات', '💰 التحصيلات', '⏳ غير المحصّل'])

        # ── تبويب 1: حركات المبيعات ──────────────────────────────
        with t1:
            if not rep_s.empty:
                s_cols = ['date','client_name','type','net']
                if 'invoice_no' in rep_s.columns: s_cols.insert(2, 'invoice_no')
                sd = rep_s[s_cols].copy()
                sd.columns = (['التاريخ','العميل','رقم الفاتورة','النوع','المبلغ']
                               if 'invoice_no' in rep_s.columns
                               else ['التاريخ','العميل','النوع','المبلغ'])
                sd['المبلغ'] = sd['المبلغ'].apply(lambda x: f'{x:,.0f}')
                sd = sd.sort_values('التاريخ', ascending=False).reset_index(drop=True)
                sd.index = range(1, len(sd)+1)
                st.caption(f'إجمالي {len(sd):,} حركة — {fmt(r_tot_s)} ر.س')
                st.dataframe(sd, use_container_width=True, height=380,
                    column_config={
                        'التاريخ'       : st.column_config.TextColumn('التاريخ',       width='small'),
                        'العميل'        : st.column_config.TextColumn('العميل',        width='large'),
                        'رقم الفاتورة'  : st.column_config.TextColumn('رقم الفاتورة', width='medium'),
                        'النوع'         : st.column_config.TextColumn('النوع',         width='small'),
                        'المبلغ'        : st.column_config.TextColumn('المبلغ (ر.س)', width='medium'),
                    })
            else:
                st.info('لا توجد حركات مبيعات لهذا المندوب في الفترة المختارة')

        # ── تبويب 2: التحصيلات ───────────────────────────────────
        with t2:
            if not rep_c.empty:
                c_cols = ['date','client_name','collection_type','net_amount']
                if 'receipt_no' in rep_c.columns: c_cols.insert(2, 'receipt_no')
                cd = rep_c[c_cols].copy()
                cd.columns = (['التاريخ','العميل','رقم السند','نوع التحصيل','المبلغ']
                               if 'receipt_no' in rep_c.columns
                               else ['التاريخ','العميل','نوع التحصيل','المبلغ'])
                cd['المبلغ'] = cd['المبلغ'].apply(lambda x: f'{x:,.0f}')
                cd = cd.sort_values('التاريخ', ascending=False).reset_index(drop=True)
                cd.index = range(1, len(cd)+1)
                st.caption(f'إجمالي {len(cd):,} عملية تحصيل — {fmt(r_tot_c)} ر.س')
                st.dataframe(cd, use_container_width=True, height=380,
                    column_config={
                        'التاريخ'       : st.column_config.TextColumn('التاريخ',       width='small'),
                        'العميل'        : st.column_config.TextColumn('العميل',        width='large'),
                        'رقم السند'     : st.column_config.TextColumn('رقم السند',     width='medium'),
                        'نوع التحصيل'   : st.column_config.TextColumn('نوع التحصيل',  width='small'),
                        'المبلغ'        : st.column_config.TextColumn('المبلغ (ر.س)', width='medium'),
                    })
            else:
                st.info('لا توجد تحصيلات لهذا المندوب في الفترة المختارة')

        # ── تبويب 3: غير المحصّل (لكل عميل) ────────────────────
        with t3:
            cl_s = rep_s.groupby('client_name')['net'].sum().reset_index()
            cl_s.columns = ['العميل', 'المبيعات']

            if not rep_c.empty:
                cl_c = rep_c.groupby('client_name')['net_amount'].sum().reset_index()
                cl_c.columns = ['العميل', 'التحصيل']
                outs = pd.merge(cl_s, cl_c, on='العميل', how='left').fillna(0)
            else:
                outs = cl_s.copy()
                outs['التحصيل'] = 0.0

            outs['المتبقي'] = (outs['المبيعات'] - outs['التحصيل']).clip(lower=0)
            outs['النسبة']  = (outs['التحصيل'] / outs['المبيعات'] * 100).round(1)
            outs = outs[outs['المتبقي'] > 0].sort_values('المتبقي', ascending=False).reset_index(drop=True)
            outs.index = range(1, len(outs)+1)

            if not outs.empty:
                tot_uncoll = outs['المتبقي'].sum()
                st.caption(f'⚠️ {len(outs)} عميل لم يُحصَّل منهم — إجمالي متبقي: {fmt(tot_uncoll)} ر.س')
                outs['المبيعات']  = outs['المبيعات'].apply(lambda x: f'{x:,.0f}')
                outs['التحصيل']   = outs['التحصيل'].apply(lambda x: f'{x:,.0f}')
                outs['المتبقي']   = outs['المتبقي'].apply(lambda x: f'{x:,.0f}')
                outs['النسبة']    = outs['النسبة'].apply(lambda x: f'{x:.1f}٪')
                st.dataframe(outs, use_container_width=True, height=400,
                    column_config={
                        'العميل'   : st.column_config.TextColumn('العميل',           width='large'),
                        'المبيعات' : st.column_config.TextColumn('المبيعات (ر.س)',   width='medium'),
                        'التحصيل'  : st.column_config.TextColumn('تم تحصيله (ر.س)', width='medium'),
                        'المتبقي'  : st.column_config.TextColumn('المتبقي (ر.س)',    width='medium'),
                        'النسبة'   : st.column_config.TextColumn('نسبة التحصيل',    width='small'),
                    })
            else:
                st.success(f'✅ ممتاز! تم تحصيل كل مبيعات {sel_rep} بالكامل')
    else:
        st.info('لا توجد بيانات مناديب للفترة المختارة')
else:
    st.info('ارفع ملف بيانات أولاً')

# ══════════════════════════════════════════════════════════════
# تفاصيل العملاء
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('تفاصيل العملاء', '🏢', '#4338CA'), unsafe_allow_html=True)
if not df_s.empty:
    clients = (df_s.groupby('client_name')
               .agg(
                   total_sales=('net','sum'),
                   transactions=('net','count'),
                   rep_name=('rep_name','first')
               )
               .reset_index()
               .sort_values('total_sales', ascending=False))
    clients.index = range(1, len(clients)+1)
    clients.columns = ['اسم العميل', 'المبيعات (ر.س)', 'الحركات', 'المندوب']
    clients['المبيعات (ر.س)'] = clients['المبيعات (ر.س)'].apply(lambda x: f'{x:,.0f}')
    clients['الحركات']         = clients['الحركات'].apply(lambda x: f'{int(x):,}')
    st.caption('👆 انقر على أي صف لعرض تفاصيل العميل أدناه')
    cl_event = st.dataframe(
        clients,
        use_container_width=True,
        height=400,
        on_select='rerun',
        selection_mode='single-row',
        column_config={
            'اسم العميل'     : st.column_config.TextColumn('اسم العميل',     width='large'),
            'المبيعات (ر.س)': st.column_config.TextColumn('المبيعات (ر.س)',width='medium'),
            'الحركات'        : st.column_config.TextColumn('الحركات',        width='small'),
            'المندوب'        : st.column_config.TextColumn('المندوب',        width='medium'),
        }
    )
    if cl_event.selection.rows:
        clicked_client = clients.iloc[cl_event.selection.rows[0]]['اسم العميل']
        st.session_state['client_detail'] = clicked_client
        st.info(f'🔍 تم اختيار **{clicked_client}** — انتقل لأسفل لرؤية التفاصيل ↓')
else:
    st.info("لا توجد بيانات عملاء للفترة المختارة")

# ══════════════════════════════════════════════════════════════
# استعراض عميل — تفصيلي
# ══════════════════════════════════════════════════════════════
st.markdown(sec_hdr('استعراض عميل بالتفصيل', '🏢', '#4338CA'), unsafe_allow_html=True)

if not df_s.empty:
    client_list = (df_s.groupby('client_name')['net'].sum()
                   .sort_values(ascending=False).index.tolist())
    if client_list:
        sel_client = st.selectbox(
            '🏢 اختر العميل (أو اضغط على أي صف في الجدول أعلاه):',
            client_list, key='client_detail'
        )

        cl_s = df_s[df_s['client_name'] == sel_client].copy()
        cl_c = df_c[df_c['client_name'] == sel_client].copy() if not df_c.empty else pd.DataFrame()

        c_tot_s  = cl_s['net'].sum()
        c_tot_c  = cl_c['net_amount'].sum() if not cl_c.empty else 0.0
        c_uncoll = max(c_tot_s - c_tot_c, 0)
        c_rate   = (c_tot_c / c_tot_s * 100) if c_tot_s > 0 else 0.0
        c_color  = '#10B981' if c_rate >= 65 else '#F59E0B' if c_rate >= 40 else '#EF4444'
        c_rep    = cl_s['rep_name'].mode()[0] if not cl_s.empty else '—'

        # بطاقات ملخص العميل
        ca, cb, cc, cd = st.columns(4)
        with ca:
            st.markdown(kpi_card(
                'إجمالي المبيعات', c_tot_s, '💰', '#4338CA',
                f'المندوب: {c_rep}', badge=f'{len(cl_s):,} حركة', btype='bb'
            ), unsafe_allow_html=True)
        with cb:
            st.markdown(kpi_card(
                'صافي التحصيل', c_tot_c, '✅', c_color,
                f'نسبة {c_rate:.1f}٪',
                badge='✅ ممتاز' if c_rate >= 65 else '⚠️ متوسط' if c_rate >= 40 else '❌ ضعيف',
                btype='bg' if c_rate >= 65 else 'by' if c_rate >= 40 else 'br'
            ), unsafe_allow_html=True)
        with cc:
            st.markdown(kpi_card(
                'المتبقي غير محصّل', c_uncoll, '⏳', '#F59E0B',
                'ريال سعودي', badge='متبقي', btype='by'
            ), unsafe_allow_html=True)
        with cd:
            st.markdown(kpi_card(
                'نسبة التحصيل', c_rate, '📊', c_color,
                '', badge=f'{c_rate:.1f}٪',
                btype='bg' if c_rate >= 65 else 'by' if c_rate >= 40 else 'br',
                is_pct=True
            ), unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        ct1, ct2 = st.tabs(['📋 حركات المبيعات', '💰 التحصيلات'])

        # تبويب 1: حركات المبيعات
        with ct1:
            if not cl_s.empty:
                s2_cols = ['date','type','net','rep_name']
                if 'invoice_no' in cl_s.columns: s2_cols.insert(1, 'invoice_no')
                sd2 = cl_s[s2_cols].copy()
                sd2.columns = (['التاريخ','رقم الفاتورة','النوع','المبلغ','المندوب']
                                if 'invoice_no' in cl_s.columns
                                else ['التاريخ','النوع','المبلغ','المندوب'])
                sd2['المبلغ'] = sd2['المبلغ'].apply(lambda x: f'{x:,.0f}')
                sd2 = sd2.sort_values('التاريخ', ascending=False).reset_index(drop=True)
                sd2.index = range(1, len(sd2)+1)
                st.caption(f'إجمالي {len(sd2):,} حركة — {fmt(c_tot_s)} ر.س')
                st.dataframe(sd2, use_container_width=True, height=360,
                    column_config={
                        'التاريخ'      : st.column_config.TextColumn('التاريخ',       width='small'),
                        'رقم الفاتورة' : st.column_config.TextColumn('رقم الفاتورة', width='medium'),
                        'النوع'        : st.column_config.TextColumn('النوع',         width='small'),
                        'المبلغ'       : st.column_config.TextColumn('المبلغ (ر.س)', width='medium'),
                        'المندوب'      : st.column_config.TextColumn('المندوب',       width='medium'),
                    })
            else:
                st.info('لا توجد حركات مبيعات لهذا العميل')

        # تبويب 2: التحصيلات
        with ct2:
            if not cl_c.empty:
                c2_cols = ['date','collection_type','net_amount','rep_name']
                if 'receipt_no' in cl_c.columns: c2_cols.insert(1, 'receipt_no')
                cd2 = cl_c[c2_cols].copy()
                cd2.columns = (['التاريخ','رقم السند','نوع التحصيل','المبلغ','المندوب']
                                if 'receipt_no' in cl_c.columns
                                else ['التاريخ','نوع التحصيل','المبلغ','المندوب'])
                cd2['المبلغ'] = cd2['المبلغ'].apply(lambda x: f'{x:,.0f}')
                cd2 = cd2.sort_values('التاريخ', ascending=False).reset_index(drop=True)
                cd2.index = range(1, len(cd2)+1)
                st.caption(f'إجمالي {len(cd2):,} عملية — {fmt(c_tot_c)} ر.س  |  متبقي: {fmt(c_uncoll)} ر.س')
                st.dataframe(cd2, use_container_width=True, height=360,
                    column_config={
                        'التاريخ'      : st.column_config.TextColumn('التاريخ',       width='small'),
                        'رقم السند'    : st.column_config.TextColumn('رقم السند',     width='medium'),
                        'نوع التحصيل'  : st.column_config.TextColumn('نوع التحصيل',  width='small'),
                        'المبلغ'       : st.column_config.TextColumn('المبلغ (ر.س)', width='medium'),
                        'المندوب'      : st.column_config.TextColumn('المندوب',       width='medium'),
                    })
                if c_uncoll > 0:
                    st.warning(f'⚠️ متبقي غير محصّل: **{fmt(c_uncoll)} ر.س**')
                else:
                    st.success('✅ تم تحصيل كل المبيعات لهذا العميل بالكامل!')
            else:
                st.warning(f'⚠️ لا توجد تحصيلات — كامل المبلغ {fmt(c_tot_s)} ر.س غير محصّل')

# الذيل
st.markdown("""
<hr style='margin-top:40px;border-color:rgba(79,70,229,.1)'>
<p style='text-align:center;color:#9CA3AF;font-size:11px;
          font-family:Cairo,sans-serif;direction:rtl;padding:8px'>
  داشبورد اكسير ERP — ارفع ملف الإكسل كل شهر والبيانات تتراكم تلقائياً
</p>""", unsafe_allow_html=True)
