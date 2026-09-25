"""
app.py - Al Muzamil Hospital Management System
Tehsil Ahmad Pur Sial, District Jhang
Phone: 0317-8377873
Email: mazharabbas77873@gmail.com
"""

import os
import sqlite3
import hashlib
import time
from datetime import datetime, date, time as dtime
import pandas as pd
import streamlit as st

# ======================================================
# DATABASE LAYER (SQLite)
# ======================================================
DB_NAME = "hospital.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _h(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'patient',
        email TEXT,
        phone TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_name TEXT,
        age INTEGER,
        phone TEXT,
        dept TEXT,
        doctor TEXT,
        appt_date TEXT,
        appt_time TEXT,
        reason TEXT,
        status TEXT DEFAULT 'Pending',
        payment_status TEXT DEFAULT 'Unpaid',
        amount INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS lab_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_name TEXT,
        test_name TEXT,
        result TEXT,
        normal_range TEXT,
        status TEXT DEFAULT 'Normal',
        report_date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        patient_name TEXT,
        description TEXT,
        amount INTEGER,
        status TEXT DEFAULT 'Unpaid',
        bill_date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        recipient TEXT,
        subject TEXT,
        message TEXT,
        sent_at TEXT
    )
    """)

    conn.commit()

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.executemany(
            "INSERT INTO users (username, password, role, email, phone, created_at) VALUES (?,?,?,?,?,?)",
            [
                ("admin", _h("admin123"), "admin", "admin@almuzamil.pk", "0317-8377873", now),
                ("patient", _h("patient123"), "patient", "patient@example.com", "0300-0000000", now),
                ("doctor", _h("doctor123"), "doctor", "doctor@almuzamil.pk", "0300-1111111", now),
            ]
        )
        conn.commit()
    conn.close()

def create_user(username, password, email="", phone="", role="patient"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, role, email, phone, created_at) VALUES (?,?,?,?,?,?)",
            (username, password, role, email, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username, password):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, role, email, phone, created_at FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_appointment(user_id, patient_name, age, phone, dept, doctor, appt_date, appt_time, reason, amount):
    conn = get_connection()
    conn.execute("""
        INSERT INTO appointments
        (user_id, patient_name, age, phone, dept, doctor, appt_date, appt_time,
         reason, status, payment_status, amount, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (user_id, patient_name, age, phone, dept, doctor, appt_date, appt_time,
          reason, "Pending", "Unpaid", amount,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_appointments_by_user(user_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM appointments WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_appointments():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_appointment_status(appt_id, status=None, payment_status=None):
    conn = get_connection()
    if status:
        conn.execute("UPDATE appointments SET status=? WHERE id=?", (status, appt_id))
    if payment_status:
        conn.execute("UPDATE appointments SET payment_status=? WHERE id=?", (payment_status, appt_id))
    conn.commit()
    conn.close()

def get_doctor_schedule(doctor):
    conn = get_connection()
    rows = conn.execute(
        "SELECT appt_date, appt_time, patient_name, status FROM appointments WHERE doctor=? ORDER BY appt_date, appt_time",
        (doctor,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_lab_report(user_id, patient_name, test_name, result, normal_range, status):
    conn = get_connection()
    conn.execute("""
        INSERT INTO lab_reports (user_id, patient_name, test_name, result, normal_range, status, report_date)
        VALUES (?,?,?,?,?,?,?)
    """, (user_id, patient_name, test_name, result, normal_range, status,
          datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_lab_reports(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute("SELECT * FROM lab_reports WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM lab_reports ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_bill(user_id, patient_name, description, amount):
    conn = get_connection()
    conn.execute("""
        INSERT INTO bills (user_id, patient_name, description, amount, status, bill_date)
        VALUES (?,?,?,?,?,?)
    """, (user_id, patient_name, description, amount, "Unpaid",
          datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def get_bills(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute("SELECT * FROM bills WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM bills ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def pay_bill(bill_id):
    conn = get_connection()
    conn.execute("UPDATE bills SET status='Paid' WHERE id=?", (bill_id,))
    conn.commit()
    conn.close()

def log_notification(user_id, recipient, subject, message):
    conn = get_connection()
    conn.execute("""
        INSERT INTO notifications (user_id, recipient, subject, message, sent_at)
        VALUES (?,?,?,?,?)
    """, (user_id, recipient, subject, message,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_notifications(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute("SELECT * FROM notifications WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ======================================================
# AUTHENTICATION & UTILITIES
# ======================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password, email="", phone="", role="patient"):
    return create_user(username, hash_password(password), email, phone, role)

def login(username, password):
    return get_user(username, hash_password(password))

def show_image(path, caption="", width=None, fallback_emoji="🏥"):
    # Images are loaded directly from the internet; no assets folder is required.
    if path:
        try:
            st.image(path, caption=caption, width=width)
            return
        except Exception:
            pass
    st.markdown(
        f"<div style='text-align:center; font-size:4rem;'>{fallback_emoji}</div>",
        unsafe_allow_html=True
    )

def send_email(user_id, recipient, subject, body):
    log_notification(user_id, recipient, subject, body)
    print(f"[EMAIL] To: {recipient} | Subject: {subject}\n {body}")

def send_sms(user_id, phone, message):
    log_notification(user_id, phone, "SMS", message)
    print(f"[SMS] To: {phone} | {message}")

def process_payment(card_number, expiry, cvv, amount):
    if len(str(card_number)) < 13 or len(str(cvv)) < 3:
        return False, "Invalid card details"
    return True, f"Payment of Rs. {amount} processed successfully (Demo)"

# ======================================================
# APP CONFIG & INITIALIZATION
# ======================================================
st.set_page_config(
    page_title="Al Muzamil Hospital - Kot Bahadur Shah",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

# Custom Styling
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 20% 0%, rgba(255,255,255,0.55) 0%, rgba(255,255,255,0) 55%),
        radial-gradient(ellipse at 80% 10%, rgba(255,255,255,0.35) 0%, rgba(255,255,255,0) 60%),
        linear-gradient(180deg,
            #a8e6ff 0%, #cdeeff 25%, #e6f9d9 55%,
            #b9e88a 70%, #8fd45a 82%, #6fbf3c 92%, #4f9b26 100%);
    background-attachment: fixed;
}
.stApp::before {
    content: ""; position: fixed; top: 0; left: 0; right: 0; height: 55vh;
    pointer-events: none; z-index: 0;
    background:
        radial-gradient(circle at 15% 25%, rgba(255,255,255,0.85) 0 60px, transparent 61px),
        radial-gradient(circle at 22% 30%, rgba(255,255,255,0.75) 0 45px, transparent 46px),
        radial-gradient(circle at 60% 15%, rgba(255,255,255,0.80) 0 70px, transparent 71px),
        radial-gradient(circle at 68% 20%, rgba(255,255,255,0.70) 0 50px, transparent 51px),
        radial-gradient(circle at 85% 30%, rgba(255,255,255,0.75) 0 55px, transparent 56px);
    opacity: 0.9;
}
.stApp::after {
    content: ""; position: fixed; left: 0; right: 0; bottom: 0; height: 90px;
    pointer-events: none; z-index: 0;
    background:
        repeating-linear-gradient(90deg, rgba(50,140,20,0.35) 0 2px, transparent 2px 10px),
        linear-gradient(180deg, transparent 0%, rgba(60,160,30,0.35) 100%);
    mask-image: linear-gradient(180deg, transparent 0%, black 60%);
    -webkit-mask-image: linear-gradient(180deg, transparent 0%, black 60%);
}
.main .block-container, [data-testid="stSidebar"] { position: relative; z-index: 1; }

.main-header {
    background: linear-gradient(135deg, rgba(0,105,92,0.95), rgba(0,137,123,0.95), rgba(38,166,154,0.95));
    padding: 28px; border-radius: 18px; color: white; text-align: center;
    box-shadow: 0 10px 28px rgba(0,0,0,0.25); margin-bottom: 22px;
    border: 2px solid rgba(255,255,255,0.35);
}
.main-header h1 { color: #fff; font-size: 2.6rem; margin: 0 0 6px; text-shadow: 0 3px 12px rgba(0,0,0,0.35); }
.main-header p { font-size: 1.15rem; opacity: 0.97; margin: 0; }

.card, .doctor-card, .dept-card, .metric-card {
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    border-radius: 16px; box-shadow: 0 6px 20px rgba(0,60,30,0.12);
    border: 1px solid rgba(255,255,255,0.7);
}
.card { padding: 20px; border-left: 6px solid #00897b; margin-bottom: 16px; }
.dept-card {
    padding: 22px 18px; text-align: center; margin-bottom: 8px;
    border-top: 5px solid #26a69a; transition: all 0.3s ease;
}
.dept-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 14px 30px rgba(0,137,123,0.35);
    border-top-color: #00695c;
}
.dept-card h3 { color: #00695c; margin: 6px 0; }
.dept-card p { color: #444; margin: 4px 0; }
.doctor-card {
    padding: 18px; margin-bottom: 14px; border-top: 4px solid #00897b;
    transition: transform 0.3s, box-shadow 0.3s;
}
.doctor-card:hover { transform: translateY(-5px); box-shadow: 0 12px 26px rgba(0,137,123,0.35); }
.metric-card { padding: 20px 12px; text-align: center; border-top: 5px solid #00897b; }
.metric-card h2 { margin: 6px 0; color: #00695c; font-size: 2rem; }
.metric-card p { margin: 0; color: #555; }
.emergency-box {
    background: linear-gradient(135deg, #b71c1c, #e53935);
    color: white; padding: 26px; border-radius: 18px; text-align: center;
    box-shadow: 0 10px 24px rgba(229,57,53,0.45);
    border: 2px solid rgba(255,255,255,0.35);
}
.emergency-box h2 { color: #fff; font-size: 2rem; margin: 6px 0; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #004d40 0%, #00695c 60%, #00897b 100%);
    border-right: 3px solid rgba(255,255,255,0.15);
}
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.35);
}
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.28); }

.stButton > button {
    background: linear-gradient(90deg, #00897b, #26a69a);
    color: #fff; border: none; border-radius: 10px;
    padding: 10px 20px; font-weight: 600; transition: all 0.25s ease;
    box-shadow: 0 4px 12px rgba(0,137,123,0.35);
}
.stButton > button:hover {
    background: linear-gradient(90deg, #00695c, #00897b);
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 8px 18px rgba(0,137,123,0.5);
}
.footer {
    background: linear-gradient(90deg, #004d40, #00695c);
    color: #fff; padding: 22px; border-radius: 16px;
    text-align: center; margin-top: 34px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
h1, h2, h3 { color: #004d40; }
hr { border: none; height: 2px; background: linear-gradient(90deg, transparent, #26a69a, transparent); }

@media (max-width: 768px) {
    .main-header h1 { font-size: 1.9rem; }
    .main-header { padding: 18px; }
    .dept-card, .doctor-card, .metric-card { padding: 14px; }
    .metric-card h2 { font-size: 1.5rem; }
}
</style>
""", unsafe_allow_html=True)

# Session State Initializations
for key, val in {
    "logged_in": False,
    "username": "",
    "user_id": None,
    "role": "patient",
    "selected_department": None,
    "prefill_doctor": None,
    "prefill_dept": None,
    "nav_to": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Static Datasets
HOSPITAL = {
    "name": "Al Muzamil Hospital",
    "location": "Kot Bahadur Shah",
    "tehsil": "Ahmad Pur Sial",
    "district": "Jhang",
    "phone": "0317-8377873",
    "email": "mazharabbas77873@gmail.com",
    "rescue": "1122",
}

DEPARTMENTS = {
    "Cardiology": {"icon": "❤️", "desc": "Heart & cardiovascular care, ECG, Angiography", "head": "Dr. Ahmed Khan"},
    "Neurology": {"icon": "🧠", "desc": "Brain, spine & nervous system treatments", "head": "Dr. Sana Malik"},
    "Orthopedics": {"icon": "🦴", "desc": "Bones, joints & sports injuries", "head": "Dr. Bilal Raza"},
    "Pediatrics": {"icon": "👶", "desc": "Child healthcare, vaccination & growth", "head": "Dr. Hina Shah"},
    "Gynecology": {"icon": "👩‍⚕️", "desc": "Women's health, maternity & prenatal care", "head": "Dr. Ayesha Siddiqui"},
    "Emergency": {"icon": "🚑", "desc": "24/7 emergency & trauma care", "head": "Dr. Usman Tariq"},
    "Dermatology": {"icon": "🧴", "desc": "Skin, hair & cosmetic treatments", "head": "Dr. Fatima Noor"},
    "ENT": {"icon": "👂", "desc": "Ear, nose & throat specialists", "head": "Dr. Kamran Ali"},
    "Oncology": {"icon": "🎗️", "desc": "Cancer diagnosis & treatment", "head": "Dr. Zara Sheikh"},
    "Radiology": {"icon": "🩻", "desc": "X-Ray, MRI, CT Scan & Ultrasound", "head": "Dr. Imran Qureshi"},
}

DOCTORS = [
    {"name": "Dr. Ahmed Khan", "dept": "Cardiology", "days": "Mon, Wed, Fri", "time": "9:00 AM - 2:00 PM", "fee": 2000, "exp": "18 years", "img": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Sana Malik", "dept": "Neurology", "days": "Tue, Thu, Sat", "time": "10:00 AM - 4:00 PM", "fee": 2500, "exp": "14 years", "img": "https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Bilal Raza", "dept": "Orthopedics", "days": "Mon, Tue, Thu", "time": "8:00 AM - 1:00 PM", "fee": 1800, "exp": "12 years", "img": "https://images.unsplash.com/photo-1537368910025-700350fe46c7?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Hina Shah", "dept": "Pediatrics", "days": "Mon - Fri", "time": "9:00 AM - 3:00 PM", "fee": 1500, "exp": "10 years", "img": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Ayesha Siddiqui","dept": "Gynecology", "days": "Wed, Fri, Sat", "time": "11:00 AM - 5:00 PM", "fee": 2200, "exp": "16 years", "img": "https://images.unsplash.com/photo-1651008376811-b90baee60c1f?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Usman Tariq", "dept": "Emergency", "days": "All Days (24/7)", "time": "Round the Clock", "fee": 1000, "exp": "15 years", "img": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Fatima Noor", "dept": "Dermatology", "days": "Tue, Wed, Sat", "time": "10:00 AM - 3:00 PM", "fee": 1700, "exp": "9 years", "img": "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Kamran Ali", "dept": "ENT", "days": "Mon, Thu, Fri", "time": "9:30 AM - 2:30 PM", "fee": 1600, "exp": "11 years", "img": "https://images.unsplash.com/photo-1618498082410-b4aa22193b38?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Zara Sheikh", "dept": "Oncology", "days": "Tue, Fri", "time": "12:00 PM - 5:00 PM", "fee": 3000, "exp": "20 years", "img": "https://images.unsplash.com/photo-1527613426441-4da17471b66d?auto=format&fit=crop&w=500&q=80"},
    {"name": "Dr. Imran Qureshi", "dept": "Radiology", "days": "Mon - Sat", "time": "8:00 AM - 8:00 PM", "fee": 1200, "exp": "13 years", "img": "https://images.unsplash.com/photo-1584982751601-97dcc096659c?auto=format&fit=crop&w=500&q=80"},
]

SERVICES = {
    "Cardiology": ["ECG", "Echocardiography", "Angiography", "Angioplasty", "Pacemaker Implant", "Holter Monitoring"],
    "Neurology": ["EEG", "MRI Brain", "Nerve Conduction Study", "Stroke Care", "Epilepsy Treatment"],
    "Orthopedics": ["Fracture Care", "Joint Replacement", "Arthroscopy", "Spine Surgery", "Sports Injury"],
    "Pediatrics": ["Vaccination", "Growth Monitoring", "Neonatal Care", "Child Nutrition", "Development Screening"],
    "Gynecology": ["Prenatal Care", "Delivery Services", "Infertility Treatment", "Laparoscopy", "Menopause Care"],
    "Emergency": ["Trauma Care", "Resuscitation", "Ambulance Service", "ICU Support", "Poison Control"],
    "Dermatology": ["Skin Allergy", "Acne Treatment", "Laser Therapy", "Hair Loss", "Cosmetic Procedures"],
    "ENT": ["Hearing Tests", "Sinus Surgery", "Tonsillectomy", "Endoscopy", "Vertigo Treatment"],
    "Oncology": ["Chemotherapy", "Radiation Therapy", "Cancer Screening", "Palliative Care", "Tumor Biopsy"],
    "Radiology": ["X-Ray", "CT Scan", "MRI", "Ultrasound", "Mammography", "PET Scan"],
}

GRASS_DIVIDER = """
<div style="height: 26px; margin: 18px 0; border-radius: 13px;
    background: repeating-linear-gradient(90deg, #4f9b26 0 4px, #6fbf3c 4px 8px, #8fd45a 8px 12px);
    box-shadow: inset 0 -3px 6px rgba(0,60,0,0.25);"></div>
"""

# ======================================================
# PAGE VIEWS
# ======================================================
def login_page():
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 {HOSPITAL['name']}</h1>
        <p>{HOSPITAL['location']} • Tehsil {HOSPITAL['tehsil']} • District {HOSPITAL['district']}</p>
        <p style="font-size:1rem; opacity:0.9;">📞 {HOSPITAL['phone']} | ✉️ {HOSPITAL['email']}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tabs = st.tabs(["🔐 Login", "📝 Register"])
        with tabs[0]:
            with st.form("login_form"):
                username = st.text_input("👤 Username")
                password = st.text_input("🔑 Password", type="password")
                submit = st.form_submit_button("Login")
                if submit:
                    user = login(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user["username"]
                        st.session_state.user_id = user["id"]
                        st.session_state.role = user["role"]
                        st.success("Login successful!")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            st.info("**Demo:** admin/admin123 | patient/patient123 | doctor/doctor123")
        with tabs[1]:
            with st.form("register_form"):
                new_user = st.text_input("Choose Username")
                new_pass = st.text_input("Choose Password", type="password")
                new_email = st.text_input("Email")
                new_phone = st.text_input("Phone")
                reg = st.form_submit_button("Register")
                if reg:
                    if not new_user or not new_pass:
                        st.error("Username and password required.")
                    else:
                        ok = register(new_user, new_pass, new_email, new_phone, "patient")
                        if ok:
                            st.success("✅ Registered! Please login.")
                        else:
                            st.warning("Username already exists.")

def home_page():
    show_image("https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1600&q=85", fallback_emoji="🏥")
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 {HOSPITAL['name']}</h1>
        <p>{HOSPITAL['location']} • Tehsil {HOSPITAL['tehsil']} • District {HOSPITAL['district']}</p>
        <p style="font-size:1rem; opacity:0.9;">📞 {HOSPITAL['phone']} | ✉️ {HOSPITAL['email']}</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, num, lbl in zip([c1, c2, c3, c4],
                             ["100+", "25+", "15+", "20,000+"],
                             ["🛏️ Beds", "👨‍⚕️ Doctors", "🏢 Departments", "😊 Patients/Year"]):
        col.markdown(f'<div class="metric-card"><h2>{num}</h2><p>{lbl}</p></div>', unsafe_allow_html=True)

    st.markdown(GRASS_DIVIDER, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #a8e063, #56ab2f); color: white;
        padding: 26px; border-radius: 18px; text-align: center; margin: 20px 0;
        box-shadow: 0 10px 26px rgba(86,171,47,0.45); border: 2px solid rgba(255,255,255,0.4);">
        <h2 style="color:white; margin:0;">🌿 {HOSPITAL['name']} — Healing with Care</h2>
        <p style="margin:8px 0 0;">Modern medicine • Trusted care • 24/7 Emergency • Expert Doctors</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"### 🌟 Welcome to {HOSPITAL['name']}")
    st.write(f"""
    **{HOSPITAL['name']}** is a trusted healthcare facility located in 
    **{HOSPITAL['location']}, Tehsil {HOSPITAL['tehsil']}, District {HOSPITAL['district']}**.

    📍 **Address:** {HOSPITAL['location']}, Tehsil {HOSPITAL['tehsil']}, District {HOSPITAL['district']}, Punjab, Pakistan  
    📞 **Phone:** {HOSPITAL['phone']}  
    ✉️ **Email:** {HOSPITAL['email']}
    """)

    st.markdown(f"""
    <div class="emergency-box">
        <h2>🚨 24/7 Emergency Services</h2>
        <p style="font-size:1.2rem;">Rescue: <b>{HOSPITAL['rescue']}</b> | Hospital: <b>{HOSPITAL['phone']}</b></p>
    </div>
    """, unsafe_allow_html=True)

def facilities_page():
    st.markdown("## 🏥 Hospital Facilities & Medical Activities")
    st.caption("Hospital, laboratory, experiments, operation theatre, emergency ward, ambulance and doctors.")

    facilities = [
        ("🏥 Hospital", "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1600&q=85", "Hospital building & healthcare environment"),
        ("🧪 Laboratory", "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=1200&q=85", "Hospital laboratory"),
        ("🔬 Lab Experiment", "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=85", "Medical laboratory experiment in progress"),
        ("🩺 Operation Theatre", "https://images.unsplash.com/photo-1551076805-e1869033e561?auto=format&fit=crop&w=1200&q=85", "Operation theatre"),
        ("🚨 Emergency Ward", "https://images.unsplash.com/photo-1516841273335-e39b37888115?auto=format&fit=crop&w=1200&q=85", "Emergency ward"),
        ("🚑 Ambulance", "https://images.unsplash.com/photo-1587745416684-47953f16f02f?auto=format&fit=crop&w=1200&q=85", "Emergency ambulance service"),
    ]

    for i in range(0, len(facilities), 2):
        c1, c2 = st.columns(2)
        for col, item in zip([c1, c2], facilities[i:i+2]):
            title, url, caption = item
            with col:
                st.markdown(f"### {title}")
                st.image(url, caption=caption, use_container_width=True)

    st.markdown("### 👨‍⚕️ Doctors")
    st.image("https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=500&q=80", caption="Medical Doctor", use_container_width=True)


def departments_page():
    if st.session_state.selected_department:
        dept = st.session_state.selected_department
        info = DEPARTMENTS[dept]

        if st.button("⬅️ Back to All Departments"):
            st.session_state.selected_department = None
            st.rerun()

        st.markdown(f"""
        <div class="main-header">
            <h1>{info['icon']} {dept} Department</h1>
            <p>{info['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        for col, title, val in zip([c1, c2, c3],
                                   ["👨‍⚕️ Head of Dept", "🕐 OPD Timings", "🚨 Emergency"],
                                   [info["head"], "8:00 AM – 10:00 PM", "24 / 7"]):
            col.markdown(f'<div class="metric-card"><h2 style="font-size:1.1rem;">{title}</h2><p style="font-weight:600;">{val}</p></div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card" style="margin-top:15px;">
            <p>📍 <b>{HOSPITAL['name']}</b> — {HOSPITAL['location']}, Tehsil {HOSPITAL['tehsil']}, District {HOSPITAL['district']}</p>
            <p>📞 {HOSPITAL['phone']} | ✉️ {HOSPITAL['email']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(GRASS_DIVIDER, unsafe_allow_html=True)
        st.markdown(f"### 👨‍⚕️ Doctors in {dept}")

        dept_docs = [d for d in DOCTORS if d["dept"] == dept]
        for doc in dept_docs:
            col1, col2 = st.columns([1, 4])
            with col1:
                show_image(doc["img"], fallback_emoji="👨‍⚕️", width=120)
            with col2:
                st.markdown(f"""
                <div class="doctor-card">
                    <h3 style="color:#00695c; margin:0;">{doc['name']}</h3>
                    <p style="margin:5px 0;"><b>Experience:</b> {doc['exp']}</p>
                    <p style="margin:5px 0;">📅 {doc['days']} | 🕐 {doc['time']}</p>
                    <p style="margin:5px 0;">💰 Fee: Rs. {doc['fee']}</p>
                </div>
                """, unsafe_allow_html=True)

            if st.button(f"📅 Book Appointment with {doc['name']}", key=f"book_{doc['name']}"):
                st.session_state.prefill_doctor = doc["name"]
                st.session_state.prefill_dept = dept
                st.session_state.nav_to = "📅 Appointment"
                st.session_state.selected_department = None
                st.rerun()

        st.markdown(GRASS_DIVIDER, unsafe_allow_html=True)
        st.markdown("### 🏥 Services Offered")
        for svc in SERVICES.get(dept, ["General Consultation"]):
            st.markdown(f"- ✅ **{svc}**")
        return

    st.markdown("## 🏢 Our Departments")
    st.caption("👉 Tap **View Details** on any department to see doctors, services & book an appointment.")

    cols = st.columns(2)
    for i, (dept, info) in enumerate(DEPARTMENTS.items()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="dept-card">
                <h2 style="font-size:2.2rem; margin:0;">{info['icon']}</h2>
                <h3>{dept}</h3>
                <p>{info['desc']}</p>
                <p><b>Head:</b> {info['head']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔍 View {dept} Details", key=f"dept_{dept}", use_container_width=True):
                st.session_state.selected_department = dept
                st.rerun()

def doctors_page():
    st.markdown("## 👨‍⚕️ Our Expert Doctors")
    dept_list = ["All"] + list(DEPARTMENTS.keys())
    selected = st.selectbox("🔍 Filter by Department", dept_list)
    filtered = DOCTORS if selected == "All" else [d for d in DOCTORS if d["dept"] == selected]
    for doc in filtered:
        col1, col2 = st.columns([1, 4])
        with col1:
            show_image(doc["img"], fallback_emoji="👨‍⚕️", width=140)
        with col2:
            st.markdown(f"""
            <div class="doctor-card">
                <h3 style="color:#00695c; margin:0;">{doc['name']}</h3>
                <p style="margin:5px 0;"><b>Dept:</b> {doc['dept']} • <b>Exp:</b> {doc['exp']}</p>
                <p style="margin:5px 0;">📅 {doc['days']} | 🕐 {doc['time']}</p>
                <p style="margin:5px 0;">💰 Rs. {doc['fee']}</p>
            </div>
            """, unsafe_allow_html=True)

def appointment_page():
    st.markdown("## 📅 Book an Appointment")
    prefill_dept = st.session_state.get("prefill_dept") or "Cardiology"
    prefill_doc = st.session_state.get("prefill_doctor")
    dept_index = list(DEPARTMENTS.keys()).index(prefill_dept)

    with st.form("appt_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Patient Name")
            age = st.number_input("Age", 1, 120, 25)
            phone = st.text_input("Phone")
        with col2:
            dept = st.selectbox("Department", list(DEPARTMENTS.keys()), index=dept_index)
            docs = [d["name"] for d in DOCTORS if d["dept"] == dept] or ["No doctor available"]
            idx = docs.index(prefill_doc) if prefill_doc in docs else 0
            doctor = st.selectbox("Doctor", docs, index=idx)
            appt_date = st.date_input("Appointment Date", min_value=date.today())
            appt_time = st.time_input("Appointment Time", value=dtime(10, 0))

        reason = st.text_area("Reason / Symptoms")
        fee = next((d["fee"] for d in DOCTORS if d["name"] == doctor), 1000)
        st.markdown(f"### 💰 Fee: **Rs. {fee}**")
        pay_now = st.checkbox("Pay Now (Demo)")
        submit = st.form_submit_button("✅ Book Appointment")

        if submit:
            if not (name and phone):
                st.error("Please fill Name and Phone.")
            else:
                if pay_now:
                    ok, msg = process_payment("4242424242424242", "12/28", "123", fee)
                    if ok:
                        st.success(msg)

                add_appointment(
                    st.session_state.user_id, name, age, phone, dept, doctor,
                    str(appt_date), str(appt_time), reason, fee
                )
                send_email(st.session_state.user_id, "patient@example.com",
                           f"{HOSPITAL['name']} - Appointment Confirmation",
                           f"Dear {name}, appt with {doctor} on {appt_date} {appt_time}.")
                send_sms(st.session_state.user_id, phone,
                         f"{HOSPITAL['name']}: Appt with {doctor} on {appt_date}.")

                st.success(f"✅ Booked with **{doctor}** on {appt_date} {appt_time}.")
                st.balloons()
                st.session_state.prefill_doctor = None
                st.session_state.prefill_dept = None

def my_appointments_page():
    st.markdown("## 📋 My Appointments")
    rows = get_appointments_by_user(st.session_state.user_id)
    if not rows:
        st.info("No appointments yet.")
    else:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

def calendar_page():
    st.markdown("## 📅 Doctor Availability Calendar")
    doc_names = [d["name"] for d in DOCTORS]
    selected_doc = st.selectbox("Select Doctor", doc_names)
    info = next(d for d in DOCTORS if d["name"] == selected_doc)
    st.markdown(f"""
    <div class="doctor-card">
        <h3 style="color:#00695c;">{info['name']}</h3>
        <p><b>Department:</b> {info['dept']}</p>
        <p><b>Available Days:</b> {info['days']}</p>
        <p><b>Timing:</b> {info['time']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 📌 Booked Slots")
    schedule = get_doctor_schedule(selected_doc)
    if not schedule:
        st.info("No bookings yet.")
    else:
        st.dataframe(pd.DataFrame(schedule), use_container_width=True)

def lab_reports_page():
    st.markdown("## 🧪 Laboratory & Experiments")
    c1, c2 = st.columns(2)
    with c1:
        st.image("https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=1200&q=85", caption="Hospital Laboratory", use_container_width=True)
    with c2:
        st.image("https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=85", caption="Medical Laboratory Experiment", use_container_width=True)
    st.markdown("### 📋 Patient Lab Reports")
    rows = get_lab_reports(st.session_state.user_id)
    if not rows:
        st.info("No lab reports available.")
    else:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

def billing_page():
    st.markdown("## 💳 Billing & Payments")
    rows = get_bills(st.session_state.user_id)
    if not rows:
        st.info("No bills found.")
        return
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.markdown("### 💰 Pay an Unpaid Bill")
    unpaid = [b for b in rows if b["status"] == "Unpaid"]
    if not unpaid:
        st.success("All bills are paid 🎉")
    else:
        options = {f"Bill #{b['id']} - {b['description']} - Rs.{b['amount']}": b["id"] for b in unpaid}
        choice = st.selectbox("Select Bill", list(options.keys()))
        if st.button("Pay Now"):
            ok, msg = process_payment("4242424242424242", "12/28", "123", 0)
            if ok:
                pay_bill(options[choice])
                st.success("✅ Bill paid!")
                st.rerun()

def notifications_page():
    st.markdown("## 🔔 Notifications")
    rows = get_notifications(st.session_state.user_id)
    if not rows:
        st.info("No notifications.")
    else:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

def emergency_page():
    st.image("https://images.unsplash.com/photo-1516841273335-e39b37888115?auto=format&fit=crop&w=1200&q=85", caption="Emergency Ward — 24/7 Emergency Services", use_container_width=True)
    st.image("https://images.unsplash.com/photo-1587745416684-47953f16f02f?auto=format&fit=crop&w=1200&q=85", caption="Ambulance & Emergency Response", use_container_width=True)
    st.markdown(f"""
    <div class="emergency-box">
        <h1>🚨 EMERGENCY SERVICES</h1>
        <h2>Call: {HOSPITAL['rescue']} | Hospital: {HOSPITAL['phone']}</h2>
        <p style="font-size:1.2rem;">Available 24/7</p>
        <p>📍 {HOSPITAL['location']}, Tehsil {HOSPITAL['tehsil']}, District {HOSPITAL['district']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 🏥 Accident & Emergency (A&E)
    - 🚑 Ambulances with advanced life support
    - 🩺 Triage area for quick assessment
    - 💉 Resuscitation rooms
    - 🫀 Cardiac Emergency Unit
    - 🧠 Stroke Unit
    """)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card"><h4>🕐 Emergency Timings</h4><p>Open 24/7</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card"><h4>📞 Contacts</h4><p>Rescue: {HOSPITAL["rescue"]}<br>Hospital: {HOSPITAL["phone"]}<br>Email: {HOSPITAL["email"]}</p></div>', unsafe_allow_html=True)

def about_page():
    st.markdown(f"## ℹ️ About {HOSPITAL['name']}")
    st.write(f"""
    **{HOSPITAL['name']}** is a trusted healthcare institution located in 
    {HOSPITAL['location']}, committed to providing quality medical services to 
    the people of Tehsil {HOSPITAL['tehsil']} and District {HOSPITAL['district']}.
    """)
    st.markdown("---")
    st.markdown("### 📍 Contact Us")
    st.markdown(f"""
    <div class="card">
        <p><b>🏥 Name:</b> {HOSPITAL['name']}</p>
        <p><b>📍 Location:</b> {HOSPITAL['location']}</p>
        <p><b>🏛️ Tehsil:</b> {HOSPITAL['tehsil']}</p>
        <p><b>🗺️ District:</b> {HOSPITAL['district']}, Punjab, Pakistan</p>
        <p><b>📞 Phone:</b> {HOSPITAL['phone']}</p>
        <p><b>✉️ Email:</b> {HOSPITAL['email']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🗺️ Find Us on Map")
    st.markdown("""
    <iframe width="100%" height="300" style="border:0; border-radius:12px;"
        loading="lazy" allowfullscreen
        src="https://www.google.com/maps?q=Kot+Bahadur+Shah+Ahmad+Pur+Sial+Jhang&output=embed"></iframe>
    """, unsafe_allow_html=True)

def admin_panel():
    st.markdown("## 🛠️ Admin Panel")
    tabs = st.tabs(["📋 Appointments", "👥 Users", "🧪 Lab Reports", "💳 Bills", "🔔 Notifications"])

    with tabs[0]:
        appts = get_all_appointments()
        if not appts:
            st.info("No appointments.")
        else:
            st.dataframe(pd.DataFrame(appts), use_container_width=True)
            ids = [a["id"] for a in appts]
            sel = st.selectbox("Appointment ID", ids)
            status = st.selectbox("Status", ["Pending", "Confirmed", "Completed", "Cancelled"])
            pay_status = st.selectbox("Payment Status", ["Unpaid", "Paid"])
            if st.button("Update"):
                update_appointment_status(sel, status, pay_status)
                st.success("Updated!")
                st.rerun()

    with tabs[1]:
        st.dataframe(pd.DataFrame(get_all_users()), use_container_width=True)

    with tabs[2]:
        with st.form("lab_form"):
            uid = st.number_input("User ID", 1, 9999, 2)
            pname = st.text_input("Patient Name")
            test = st.text_input("Test Name")
            result = st.text_input("Result")
            rng = st.text_input("Normal Range")
            status = st.selectbox("Status", ["Normal", "Abnormal", "Critical"])
            if st.form_submit_button("Add Report") and pname and test:
                add_lab_report(uid, pname, test, result, rng, status)
                st.success("Report added.")
        st.dataframe(pd.DataFrame(get_lab_reports()), use_container_width=True)

    with tabs[3]:
        with st.form("bill_form"):
            uid = st.number_input("User ID ", 1, 9999, 2)
            pname = st.text_input("Patient Name ")
            desc = st.text_input("Description")
            amt = st.number_input("Amount (Rs.)", 0, 1000000, 1000)
            if st.form_submit_button("Add Bill") and pname and desc:
                add_bill(uid, pname, desc, amt)
                st.success("Bill added.")
        st.dataframe(pd.DataFrame(get_bills()), use_container_width=True)

    with tabs[4]:
        st.dataframe(pd.DataFrame(get_notifications()), use_container_width=True)

# ======================================================
# MAIN ROUTING
# ======================================================
def main():
    if not st.session_state.logged_in:
        login_page()
        return

    pages = [
        "🏠 Home", "🏥 Facilities", "🏢 Departments", "👨‍⚕️ Doctors",
        "📅 Appointment", "📋 My Appointments",
        "🗓️ Doctor Calendar", "🧪 Lab Reports",
        "💳 Billing", "🔔 Notifications",
        "🚨 Emergency", "ℹ️ About & Contact",
    ]
    if st.session_state.role == "admin":
        pages.append("🛠️ Admin Panel")

    default_index = 0
    if st.session_state.nav_to and st.session_state.nav_to in pages:
        default_index = pages.index(st.session_state.nav_to)
        st.session_state.nav_to = None

    with st.sidebar:
        show_image("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=300&q=80", fallback_emoji="🏥", width=80)
        st.markdown(f"### 🏥 {HOSPITAL['name']}")
        st.caption(f"{HOSPITAL['location']} • {HOSPITAL['district']}")
        st.markdown("---")
        st.markdown(f"### 👋 {st.session_state.username}")
        st.caption(f"Role: {st.session_state.role.upper()}")
        st.markdown("---")
        page = st.radio("📌 Navigation", pages, index=default_index)
        st.markdown("---")
        if st.button("🚪 Logout"):
            for k in ["logged_in", "username", "user_id", "role"]:
                st.session_state[k] = False if k == "logged_in" else ("" if k != "user_id" else None)
            st.session_state.selected_department = None
            st.rerun()

    routes = {
        "🏠 Home": home_page,
        "🏥 Facilities": facilities_page,
        "🏢 Departments": departments_page,
        "👨‍⚕️ Doctors": doctors_page,
        "📅 Appointment": appointment_page,
        "📋 My Appointments": my_appointments_page,
        "🗓️ Doctor Calendar": calendar_page,
        "🧪 Lab Reports": lab_reports_page,
        "💳 Billing": billing_page,
        "🔔 Notifications": notifications_page,
        "🚨 Emergency": emergency_page,
        "ℹ️ About & Contact": about_page,
        "🛠️ Admin Panel": admin_panel,
    }
    routes.get(page, home_page)()

    st.markdown(f"""
    <div class="footer">
        <p><b>🏥 {HOSPITAL['name']}</b> — {HOSPITAL['location']}, Tehsil {HOSPITAL['tehsil']}, District {HOSPITAL['district']}</p>
        <p>📞 {HOSPITAL['phone']} | ✉️ {HOSPITAL['email']} | 🚨 Rescue: {HOSPITAL['rescue']}</p>
        <p>© 2025 {HOSPITAL['name']} | All Rights Reserved</p><p>Prepared by <b>Mazhar Abbas</b></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()