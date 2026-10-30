import streamlit as st
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บแดชบอร์ด
st.set_page_config(
    page_title="Dashboard วิเคราะห์การใช้ไฟฟ้า",
    page_icon="⚡",
    layout="wide"
)

# 2. หัวข้อเว็บไซต์และคำอธิบายวัตถุประสงค์ (ตอบโจทย์ข้อ 2)
st.title("⚡ แดชบอร์ดวิเคราะห์การใช้ไฟฟ้าในสถานศึกษา (2025)")
st.markdown("เว็บไซต์นี้จัดทำขึ้นเพื่อวิเคราะห์ข้อมูลการใช้ไฟฟ้า พฤติกรรมการใช้งาน และปัจจัยด้านสภาพอากาศในสถานศึกษา")

# 3. ฟังก์ชันโหลดข้อมูลพร้อมระบบจัดการข้อผิดพลาด (ตอบโจทย์ข้อ 10)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('electricity_cleaned.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp']) # แปลงวันที่ให้เป็น DateTime
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("❌ ไม่พบไฟล์ 'electricity_cleaned.csv' กรุณานำไฟล์มาวางไว้ในโฟลเดอร์เดียวกับ app.py")
    st.stop()

st.success("✅ โหลดข้อมูลและเชื่อมต่อสำเร็จเรียบร้อย!")

# --- 4. แผงควบคุมตัวกรองข้อมูล (Filters) (ตอบโจทย์ข้อ 4) ---
st.sidebar.header("🔍 ตัวกรองข้อมูล (Filters)")

# ตัวกรองเลือก Meter ID
all_meters = ['ทั้งหมด'] + list(df['meter_id'].unique())
selected_meter = st.sidebar.selectbox("เลือกมิเตอร์ (Meter ID)", all_meters)

# กรองข้อมูลตามที่ผู้ใช้งานเลือกใน Sidebar
if selected_meter != 'ทั้งหมด':
    df_filtered = df[df['meter_id'] == selected_meter]
else:
    df_filtered = df

# --- 5. ตัวเลขสรุปสำคัญ (KPIs) (ตอบโจทย์ข้อ 3) ---
st.subheader("📊 ตัวเลขสรุปสำคัญ (Key Performance Indicators)")
col1, col2, col3 = st.columns(3)

total_energy = df_filtered['energy_kwh'].sum()
avg_occupancy = df_filtered['occupancy_people'].mean()
total_records = len(df_filtered)

col1.metric("⚡ พลังงานไฟฟ้ารวมทั้งหมด", f"{total_energy:,.2f} kWh")
col2.metric("👥 จำนวนคนเฉลี่ยต่อห้อง", f"{avg_occupancy:.2f} คน")
col3.metric("📋 จำนวนรายการทั้งหมด", f"{total_records:,} รายการ")

st.markdown("---")

# --- 6. กราฟแสดงผลแบบโต้ตอบด้วย Plotly (ตอบโจทย์ข้อ 6: มีกราฟ 2 รูปแบบ) ---
st.subheader("📈 การแสดงผลกราฟวิเคราะห์ข้อมูล")

col_g1, col_g2 = st.columns(2)

with col_g1:
    # กราฟแท่ง (Bar Chart): ยอดใช้ไฟฟ้ารายเดือน
    df_filtered['month'] = df_filtered['timestamp'].dt.month
    monthly_trend = df_filtered.groupby('month')['energy_kwh'].sum().reset_index()
    fig_bar = px.bar(
        monthly_trend, 
        x='month', 
        y='energy_kwh', 
        title="ยอดรวมการใช้ไฟฟ้าแยกตามรายเดือน (kWh)",
        labels={'month': 'เดือน', 'energy_kwh': 'พลังงานไฟฟ้า (kWh)'},
        color='energy_kwh',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    # กราฟเส้น (Line Chart): แนวโน้มการใช้ไฟฟ้ารายวัน (ตอบโจทย์ข้อ 6)
    df_filtered['date'] = df_filtered['timestamp'].dt.date
    daily_trend = df_filtered.groupby('date')['energy_kwh'].sum().reset_index()
    fig_line = px.line(
        daily_trend, 
        x='date', 
        y='energy_kwh', 
        title="แนวโน้มการใช้ไฟฟ้ารายวัน (Daily Trend)",
        labels={'date': 'วันที่', 'energy_kwh': 'พลังงานไฟฟ้า (kWh)'}
    )
    st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# --- 7. ข้อความสรุปข้อค้นพบจากข้อมูลจริง (ตอบโจทย์ข้อ 7) ---
st.subheader("💡 สรุปข้อค้นพบและข้อเสนอแนะจากข้อมูล (Insights)")
st.info("""
- **พฤติกรรมการใช้ไฟฟ้าตามฤดูกาล**: ยอดการใช้ไฟฟ้าพุ่งสูงขึ้นในช่วงกลางปี (โดยเฉพาะเดือนพฤษภาคม) ซึ่งสอดคล้องกับช่วงเปิดเทอมและสภาพอากาศที่ร้อนจัด
- **ความสัมพันธ์กับผู้ใช้งาน**: ปริมาณการใช้ไฟฟ้ามีความสัมพันธ์สอดคล้องกับจำนวนคนในพื้นที่ใช้งาน โดยช่วงที่มีคนหนาแน่นจะมีการใช้พลังงานสูงขึ้นอย่างเห็นได้ชัด
- **ข้อเสนอแนะเชิงประหยัดพลังงาน**: ควรพิจารณาตั้งเวลาปิดเครื่องปรับอากาศอัตโนมัติในช่วงเวลาพักเที่ยงหรือหลังเลิกเรียน เพื่อลดการใช้พลังงานส่วนเกิน
""")

# --- 8. ตารางข้อมูลที่เปลี่ยนแปลงตามตัวกรอง (ตอบโจทย์ข้อ 5) ---
st.subheader("📋 ตารางข้อมูล (แสดงผลตามตัวกรองที่เลือก)")
st.write(f"แสดงผลข้อมูลจำนวน {len(df_filtered):,} แถว")
st.dataframe(df_filtered.head(100), use_container_width=True)