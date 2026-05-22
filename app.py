"""
app.py — داشبورد اكسير ERP
Streamlit web dashboard — ارفع Excel شهرياً والداشبورد يتحدث تلقائياً
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from parser import parse_excel_file
from db import (init_db, save_data, get_available_months,
                get_sales, get_collections, get_work_orders,
                get_uploads_history, delete_month)

# ════════════════════════════════════════════════════════════
# إعداد الصفحة
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="داشبورد اكسير ERP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

* { font-family: 'Cairo', sans-serif !important; }

.stApp { background: #F0F2F6; }

/* RTL */
.block-container { direction: rtl; }
.stDataFrame     { direction: rtl; }

/* KPI Card */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border-top: 5px solid;
    min-height: 120px;
}
.kpi-title { font-size: 12px; color: #666; margin-bottom: 8px; font-weight: 600; }
.kpi-value { font-size: 24px; font-weight: 900; line-height: 1.1; }
.kpi-sub   { font-size: 11px; color: #888; margin-top: 6px; }

/* Section header */
.sec-hdr {
    background: linear-gradient(90deg, #1565C0, #1976D2);
    color: white;
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    margin: 18px 0 10px;
    letter-spacing: 0.3px;
}

/* Amount badge under gauge */
.amt-badge {
    background: white;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    border: 2px solid;
    margin-top: -5px;
    font-family: 'Cairo', sans-serif;
}
.amt-main { font-size: 15px; font-weight: 700; }
.amt-sub  { font-size: 11px; color: #888; margin-top: 3px; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0D47A1 !important; }
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: #90CAF9 !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# دوال مساعدة
# ════════════════════════════════════════════════════════════

MONTH_AR = {
    '01':'يناير','02':'فبراير','03':'مارس','04':'أبريل',
    '05':'مايو', '06':'يونيو', '07':'يوليو','08':'أغسطس',
    '09':'سبتمبر','10':'أكتوبر','11':'نوفمبر','12':'ديسمبر'
}

def month_label(m):
    if not m or '-' not in m:
        return m or ''
    p = m.split('-')
    return MONTH_AR.get(p[1], p[1]) + ' ' + p[0]

def fmt(n):
    """تنسيق الأرقام مع فاصلة"""
    return f'{round(n):,}'

def make_gauge(value, title, color):
    fig = go.Figure(go.Indicator(
        mode  = "gauge+number",
        value = round(value, 1),
        title = {'text': title, 'font': {'size': 15, 'family': 'Cairo', 'color': '#212121'}},
        number= {'suffix': '%', 'font': {'size': 30, 'family': 'Cairo', 'color': color}},
        gauge = {
            'axis' : {'range': [0, 100], 'tickwidth': 1,
                      'tickfont': {'size': 9}, 'tickcolor': '#555'},
            'bar'  : {'color': color, 'thickness': 0.28},
            'bgcolor'    : 'white',
            'borderwidth': 2,
            'bordercolor': '#DDD',
            'steps': [
                {'range': [0,  40], 'color': '#FFCDD2'},
                {'range': [40, 65], 'color': '#FFF9C4'},
                {'range': [65,100], 'color': '#C8E6C9'}
            ],
            'threshold': {
                'line'     : {'color': color, 'width': 5},
                'thickness': 0.82,
                'value'    : value
            }
        }
    ))
    fig.update_layout(
        height=240,
        margin=dict(l=15, r=15, t=45, b=10),
        paper_bgcolor='white',
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
        marker_color='#1565C0',
        text=m['مبيعات'].apply(lambda x: f'{x/1000:.0f}K'),
        textposition='outside', textfont_size=9
    ))
    fig.add_trace(go.Scatter(
        x=m['label'], y=m['تحصيل'], name='التحصيل',
        mode='lines+markers',
        line=dict(color='#2E7D32', width=3),
        marker=dict(size=8, color='#2E7D32', symbol='circle')
    ))
    fig.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=15, b=10),
        paper_bgcolor='white', plot_bgcolor='white',
        legend=dict(orientation='h', y=-0.18, font_size=12),
        xaxis=dict(showgrid=False, tickfont_size=10),
        yaxis=dict(gridcolor='#EEEEEE', tickformat=',.0f', tickfont_size=10),
        font_family='Cairo',
        barmode='group'
    )
    return fig

def make_reps_chart(reps_df):
    if reps_df.empty:
        return None
    top = reps_df.head(10).sort_values('total_sales')
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top['rep_name'], x=top['total_sales'],
        name='المبيعات', orientation='h',
        marker_color='#1565C0',
        text=top['total_sales'].apply(lambda x: f'{x/1000:.0f}K'),
        textposition='outside', textfont_size=10
    ))
    fig.add_trace(go.Bar(
        y=top['rep_name'], x=top['total_collect'],
        name='التحصيل', orientation='h',
        marker_color='#2E7D32',
        text=top['total_collect'].apply(lambda x: f'{x/1000:.0f}K'),
        textposition='outside', textfont_size=10
    ))
    fig.update_layout(
        height=max(280, len(top)*35),
        barmode='group',
        margin=dict(l=10, r=60, t=15, b=10),
        paper_bgcolor='white', plot_bgcolor='white',
        legend=dict(orientation='h', y=-0.12, font_size=11),
        xaxis=dict(gridcolor='#EEEEEE', tickformat=',.0f', tickfont_size=9),
        yaxis=dict(tickfont_size=11),
        font_family='Cairo'
    )
    return fig

def calc_reps(df_s, df_c, num_months):
    if df_s.empty:
        return pd.DataFrame()

    reps = df_s.groupby('rep_name')['net'].sum().reset_index()
    reps.columns = ['rep_name', 'total_sales']

    off = (df_s[df_s['type'].str.contains('وفست', na=False)]
           .groupby('rep_name')['net'].sum().reset_index()
           .rename(columns={'net': 'off_sales'}))
    reps = pd.merge(reps, off, on='rep_name', how='left').fillna(0)
    reps['dig_sales'] = reps['total_sales'] - reps['off_sales']

    if not df_c.empty:
        col = df_c.groupby('rep_name')['net_amount'].sum().reset_index()
        col.columns = ['rep_name', 'total_collect']
        reps = pd.merge(reps, col, on='rep_name', how='left').fillna(0)
    else:
        reps['total_collect'] = 0

    nm = max(num_months, 1)
    reps = reps[reps['rep_name'] != 'غير محدد']
    reps = reps[reps['total_sales'] > 0]
    reps['collect_rate'] = (reps['total_collect'] / reps['total_sales'] * 100).round(1)
    reps['avg_sales']    = (reps['total_sales']   / nm).round(0)
    reps['avg_collect']  = (reps['total_collect'] / nm).round(0)
    return reps.sort_values('total_sales', ascending=False).reset_index(drop=True)

# ════════════════════════════════════════════════════════════
# تهيئة DB
# ════════════════════════════════════════════════════════════
init_db()

# ════════════════════════════════════════════════════════════
# الشريط الجانبي
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("# 📊 اكسير ERP")
    st.markdown("---")

    # ── رفع الملف ────────────────────────────────────────────
    st.markdown("### 📁 رفع ملف شهري جديد")
    uploaded = st.file_uploader(
        "اختر ملف Excel من اكسير ERP",
        type=['xlsx', 'xls'],
        help="ملف متابعة المبيعات الشهري"
    )

    if uploaded:
        with st.spinner('⏳ جاري معالجة الملف...'):
            try:
                data = parse_excel_file(uploaded)
                uid, months_covered = save_data(data, uploaded.name)
                months_ar = [month_label(m) for m in months_covered]
                st.success(
                    f"✅ **تم الرفع بنجاح!**\n\n"
                    f"• مبيعات: **{len(data['sales']):,}** سجل\n"
                    f"• تحصيلات: **{len(data['collections']):,}** سجل\n"
                    f"• أوامر عمل: **{len(data['work_orders']):,}** أمر\n"
                    f"• الأشهر: **{' | '.join(months_ar)}**"
                )
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ في معالجة الملف:\n{str(e)}")

    st.markdown("---")

    # ── فلتر الفترة ───────────────────────────────────────────
    available = get_available_months()

    if available:
        st.markdown("### 🗓 فلتر الفترة")
        from_m = st.selectbox("من شهر:", available,
                               index=0, format_func=month_label)
        to_m   = st.selectbox("إلى شهر:", available,
                               index=len(available)-1, format_func=month_label)
        period_label = f"من {month_label(from_m)} إلى {month_label(to_m)}"
    else:
        from_m = to_m = None
        period_label  = "لا توجد بيانات"

    st.markdown("---")

    # ── سجل الرفع ────────────────────────────────────────────
    with st.expander("📋 سجل الرفع"):
        hist = get_uploads_history()
        if not hist.empty:
            for _, row in hist.iterrows():
                st.markdown(f"**📄 {row['filename']}**")
                st.caption(
                    f"🕐 {row['uploaded_at'][:16]}\n"
                    f"📊 مبيعات: {row['sales_count']:,} | تحصيلات: {row['collect_count']:,}"
                )
                st.markdown("---")
        else:
            st.info("لا يوجد سجل حتى الآن")

    # ── حذف شهر ──────────────────────────────────────────────
    with st.expander("🗑 حذف بيانات شهر"):
        if available:
            del_m = st.selectbox("اختر الشهر للحذف:", available,
                                  format_func=month_label, key='del')
            if st.button("حذف هذا الشهر", type="secondary"):
                delete_month(del_m)
                st.success(f"✅ تم حذف {month_label(del_m)}")
                st.rerun()

# ════════════════════════════════════════════════════════════
# الصفحة الرئيسية — لو مفيش بيانات
# ════════════════════════════════════════════════════════════
if not available:
    st.markdown("""
    <div style='text-align:center; padding:80px 20px; direction:rtl;'>
        <div style='font-size:64px; margin-bottom:20px;'>📊</div>
        <h1 style='color:#1565C0; font-family:Cairo;'>داشبورد اكسير ERP</h1>
        <p style='font-size:18px; color:#666; font-family:Cairo;'>
            ارفع ملف Excel الشهري من القائمة الجانبية للبدء
        </p>
        <p style='font-size:14px; color:#999; font-family:Cairo;'>
            كل شهر ترفع ملف جديد — الداشبورد بيتراكم ويحفظ التاريخ كله
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ════════════════════════════════════════════════════════════
# تحميل البيانات
# ════════════════════════════════════════════════════════════
df_s = get_sales(from_m, to_m)
df_c = get_collections(from_m, to_m)
df_w = get_work_orders(from_m, to_m)

# ── حسابات KPI ───────────────────────────────────────────────
tot_s = df_s['net'].sum()       if not df_s.empty else 0.0
off_s = (df_s[df_s['type'].str.contains('وفست', na=False)]['net'].sum()
         if not df_s.empty else 0.0)
dig_s = tot_s - off_s
tot_c = df_c['net_amount'].sum() if not df_c.empty else 0.0
tot_w = len(df_w)

rate  = (tot_c / tot_s * 100) if tot_s > 0 else 0.0
off_p = (off_s / tot_s * 100) if tot_s > 0 else 0.0
dig_p = (dig_s / tot_s * 100) if tot_s > 0 else 0.0

nm    = max(df_s['month'].nunique() if not df_s.empty else 1, 1)
avg_s = tot_s / nm
avg_c = tot_c / nm

rate_color = ('#1B5E20' if rate >= 65
              else '#E65100' if rate >= 40
              else '#C62828')

# ════════════════════════════════════════════════════════════
# العنوان
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div style='background:linear-gradient(135deg,#0D47A1,#1976D2);
            color:white; padding:18px 28px; border-radius:14px;
            margin-bottom:18px; direction:rtl;
            box-shadow:0 4px 15px rgba(13,71,161,0.3);'>
  <h2 style='margin:0; font-family:Cairo; font-size:22px;'>
      📊 داشبورد اكسير ERP
  </h2>
  <p style='margin:5px 0 0; opacity:0.85; font-size:13px; font-family:Cairo;'>
      {period_label} &nbsp;|&nbsp; {nm} شهر &nbsp;|&nbsp;
      مبيعات: {fmt(tot_s)} ر.س &nbsp;|&nbsp; تحصيل: {fmt(tot_c)} ر.س
  </p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# KPI Cards — صف 1
# ════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr">💰 المؤشرات المالية الرئيسية</div>',
            unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:#1565C0">
        <div class="kpi-title">💰 إجمالي المبيعات</div>
        <div class="kpi-value" style="color:#1565C0">{fmt(tot_s)}</div>
        <div class="kpi-sub">ريال سعودي</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:#01579B">
        <div class="kpi-title">🖨 مبيعات أوفست</div>
        <div class="kpi-value" style="color:#01579B">{fmt(off_s)}</div>
        <div class="kpi-sub">{off_p:.1f}% من الإجمالي</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:#006064">
        <div class="kpi-title">📱 مبيعات ديجيتال</div>
        <div class="kpi-value" style="color:#006064">{fmt(dig_s)}</div>
        <div class="kpi-sub">{dig_p:.1f}% من الإجمالي</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:{rate_color}">
        <div class="kpi-title">✅ صافي التحصيل</div>
        <div class="kpi-value" style="color:{rate_color}">{fmt(tot_c)}</div>
        <div class="kpi-sub">{rate:.1f}% نسبة التحصيل</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# KPI Cards — صف 2
c5, c6, c7, c8 = st.columns(4)
status_text = ('✅ أداء ممتاز' if rate >= 65
               else '⚠️ أداء متوسط' if rate >= 40
               else '❌ يحتاج متابعة')
with c5:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:#4527A0">
        <div class="kpi-title">📋 أوامر العمل</div>
        <div class="kpi-value" style="color:#4527A0">{tot_w:,}</div>
        <div class="kpi-sub">أمر عمل مسجّل</div>
    </div>""", unsafe_allow_html=True)
with c6:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:{rate_color}">
        <div class="kpi-title">📊 نسبة التحصيل</div>
        <div class="kpi-value" style="color:{rate_color}">{rate:.1f}%</div>
        <div class="kpi-sub">{status_text}</div>
    </div>""", unsafe_allow_html=True)
with c7:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:#33691E">
        <div class="kpi-title">📈 متوسط مبيعات/شهر</div>
        <div class="kpi-value" style="color:#33691E">{fmt(avg_s)}</div>
        <div class="kpi-sub">ريال / شهر</div>
    </div>""", unsafe_allow_html=True)
with c8:
    st.markdown(f"""<div class="kpi-card" style="border-top-color:#006064">
        <div class="kpi-title">💵 متوسط تحصيل/شهر</div>
        <div class="kpi-value" style="color:#006064">{fmt(avg_c)}</div>
        <div class="kpi-sub">ريال / شهر</div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# العدادات (Gauges)
# ════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr">🎯 مؤشرات الأداء</div>',
            unsafe_allow_html=True)

g1, g2, g3 = st.columns(3)

with g1:
    st.plotly_chart(make_gauge(rate, 'نسبة التحصيل', rate_color),
                    use_container_width=True)
    st.markdown(f"""<div class="amt-badge" style="border-color:{rate_color}">
        <div class="amt-main" style="color:{rate_color}">
            {fmt(tot_c)} &nbsp; من &nbsp; {fmt(tot_s)}
        </div>
        <div class="amt-sub">صافي التحصيل من إجمالي المبيعات</div>
    </div>""", unsafe_allow_html=True)

with g2:
    st.plotly_chart(make_gauge(off_p, 'نسبة الأوفست', '#01579B'),
                    use_container_width=True)
    st.markdown(f"""<div class="amt-badge" style="border-color:#01579B">
        <div class="amt-main" style="color:#01579B">
            {fmt(off_s)} &nbsp; من &nbsp; {fmt(tot_s)}
        </div>
        <div class="amt-sub">مبيعات أوفست من إجمالي المبيعات</div>
    </div>""", unsafe_allow_html=True)

with g3:
    st.plotly_chart(make_gauge(dig_p, 'نسبة الديجيتال', '#006064'),
                    use_container_width=True)
    st.markdown(f"""<div class="amt-badge" style="border-color:#006064">
        <div class="amt-main" style="color:#006064">
            {fmt(dig_s)} &nbsp; من &nbsp; {fmt(tot_s)}
        </div>
        <div class="amt-sub">مبيعات ديجيتال من إجمالي المبيعات</div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# الشارت الشهري
# ════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr">📈 المبيعات والتحصيلات الشهرية</div>',
            unsafe_allow_html=True)
st.plotly_chart(make_monthly_chart(df_s, df_c), use_container_width=True)

# ════════════════════════════════════════════════════════════
# المناديب
# ════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr">👥 أداء المناديب</div>',
            unsafe_allow_html=True)

reps = calc_reps(df_s, df_c, nm)

if not reps.empty:
    tab1, tab2 = st.tabs(["📊 شارت المناديب", "📋 جدول المناديب"])

    with tab1:
        fig_r = make_reps_chart(reps)
        if fig_r:
            st.plotly_chart(fig_r, use_container_width=True)

    with tab2:
        disp = reps[['rep_name','off_sales','dig_sales','total_sales',
                     'total_collect','collect_rate','avg_sales','avg_collect']].copy()
        disp.index = range(1, len(disp)+1)
        disp.columns = ['المندوب','مبيعات أوفست','مبيعات ديجيتال',
                         'إجمالي المبيعات','صافي التحصيل','نسبة التحصيل %',
                         'متوسط مبيعات/شهر','متوسط تحصيل/شهر']
        for col in ['مبيعات أوفست','مبيعات ديجيتال','إجمالي المبيعات',
                    'صافي التحصيل','متوسط مبيعات/شهر','متوسط تحصيل/شهر']:
            disp[col] = disp[col].apply(lambda x: f'{x:,.0f}')
        disp['نسبة التحصيل %'] = disp['نسبة التحصيل %'].apply(lambda x: f'{x:.1f}%')
        st.dataframe(disp, use_container_width=True, height=420)
else:
    st.info("لا توجد بيانات مناديب للفترة المختارة")

# ════════════════════════════════════════════════════════════
# تفاصيل العملاء
# ════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr">🏢 تفاصيل العملاء</div>',
            unsafe_allow_html=True)

if not df_s.empty:
    clients = (df_s.groupby('client_name')
               .agg(total_sales=('net','sum'),
                    transactions=('net','count'),
                    rep_name=('rep_name','first'))
               .reset_index()
               .sort_values('total_sales', ascending=False))
    clients.index = range(1, len(clients)+1)
    clients.columns = ['العميل','إجمالي المبيعات','عدد الحركات','المندوب']
    clients['إجمالي المبيعات'] = clients['إجمالي المبيعات'].apply(lambda x: f'{x:,.0f}')
    st.dataframe(clients, use_container_width=True, height=380)
else:
    st.info("لا توجد بيانات عملاء للفترة المختارة")

# ════════════════════════════════════════════════════════════
# Footer
# ════════════════════════════════════════════════════════════
st.markdown("""
<hr style='margin-top:40px; opacity:0.2;'>
<p style='text-align:center; color:#999; font-size:11px; font-family:Cairo;'>
    داشبورد اكسير ERP — ارفع ملف Excel كل شهر والبيانات تتراكم تلقائياً
</p>
""", unsafe_allow_html=True)
