import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PNPI - Pak Navy Polytechnic Institute",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0b132b;
        color: #ffffff;
    }
    .main-header {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #6fffe9;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: center;
        margin-bottom: 25px;
    }
    .main-header h1 {
        color: #6fffe9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .main-header h4 {
        color: #5bc0be;
        margin-top: 0;
    }
    .css-card {
        background: #1c2541;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #6fffe9;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .badge-pass {
        background-color: #2ec4b6;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-fail {
        background-color: #e63946;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .css-1d3710w {
        background-color: #0b132b;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA STRUCTURE SETUP
# -----------------------------------------------------------------------------
SEMESTER_SUBJECTS = {
    "Semester 1": [
        ("Engineering Mathematics-I", "Engr. Tariq Mehmood"),
        ("Applied Physics", "Dr. Aisha Khan"),
        ("Basic Electrical Engineering", "Engr. Bilal Ahmed"),
        ("Computer Programming (C++)", "Prof. Salman Shah"),
        ("Engineering Drawing & CAD", "Engr. Hamza Ali"),
        ("Workshop Technology", "Inst. Rashid Minhas"),
        ("English Communication Skills", "Ms. Fatima Noor"),
        ("Islamic / Pak Studies", "Prof. Abdul Rehman")
    ],
    "Semester 2": [
        ("Engineering Mathematics-II", "Engr. Tariq Mehmood"),
        ("Electronic Devices & Circuits", "Dr. Kamran Akram"),
        ("Digital Logic Design", "Engr. Usman Ghani"),
        ("Mechanics of Materials", "Dr. Aisha Khan"),
        ("Thermodynamics", "Engr. Hassan Raza"),
        ("Object-Oriented Programming (Python)", "Prof. Salman Shah"),
        ("Instrumentation & Measurements", "Engr. Bilal Ahmed")
    ],
    "Semester 3": [
        ("Microcontrollers & Embedded Systems", "Engr. Usman Ghani"),
        ("Sensors & Actuators", "Dr. Kamran Akram"),
        ("Fluid Mechanics & Hydraulics", "Engr. Hassan Raza"),
        ("Control Systems Engineering", "Dr. Zainab Malik"),
        ("Manufacturing Processes", "Inst. Rashid Minhas"),
        ("Signals & Systems", "Engr. Bilal Ahmed"),
        ("Numerical Analysis", "Engr. Tariq Mehmood")
    ],
    "Semester 4": [
        ("Robotics & Automation", "Dr. Zainab Malik"),
        ("PLC & Industrial Automation", "Engr. Usman Ghani"),
        ("Power Electronics", "Dr. Kamran Akram"),
        ("Pneumatic & Hydraulic Systems", "Engr. Hassan Raza"),
        ("Machine Design & CAD/CAM", "Engr. Hamza Ali")
    ],
    "Semester 5": [
        ("Mechatronics System Design (Capston)", "Dr. Zainab Malik"),
        ("Artificial Intelligence in Robotics", "Prof. Salman Shah"),
        ("Industrial IoT & Cyber-Physical Systems", "Engr. Bilal Ahmed"),
        ("Engineering Management & Economics", "Ms. Fatima Noor"),
        ("Safety, Health & Environment (HSE)", "Inst. Rashid Minhas")
    ]
}

@st.cache_data
def generate_student_data():
    students_db = {}
    semesters = list(SEMESTER_SUBJECTS.keys())
    roll_counter = 101

    for sem in semesters:
        subjects = [sub[0] for sub in SEMESTER_SUBJECTS[sem]]
        for i in range(1, 9):
            roll_no = f"PNPI-ME-{roll_counter}"
            marks = {}

            for idx, sub in enumerate(subjects):
                marks[sub] = 68 if (i + idx) % 3 == 0 else 82

            students_db[roll_no] = {
                "name": f"Student {i}",
                "roll_no": roll_no,
                "semester": sem,
                "marks": marks
            }
            roll_counter += 1

    students_db["PNPI-101"] = {
        "name": "Ali Raza",
        "roll_no": "PNPI-101",
        "semester": "Semester 1",
        "marks": {
            "Engineering Mathematics-I": 85,
            "Applied Physics": 78,
            "Basic Electrical Engineering": 90,
            "Computer Programming (C++)": 76,
            "Engineering Drawing & CAD": 88,
            "Workshop Technology": 74,
            "English Communication Skills": 80,
            "Islamic / Pak Studies": 82
        }
    }

    return students_db

students_db = generate_student_data()

# -----------------------------------------------------------------------------
# 3. HEADER & NAVIGATION
# -----------------------------------------------------------------------------
col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.markdown("""
        <div style="text-align: center; font-size: 70px; color: #6fffe9;">
            ⚓
        </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
        <div class="main-header">
            <h1>PAK NAVY POLYTECHNIC INSTITUTE (PNPI)</h1>
            <h4>West Wharf Road, Karachi</h4>
            <p style="color:#6fffe9; font-weight:bold;">
                Department of Mechatronics Engineering
            </p>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.title("⚓ Navigation")
menu = st.sidebar.radio(
    "Go to",
    [
        "Home & Technology Overview",
        "Course Curriculum & Teachers",
        "Student Result Portal"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Institute Location:**\nWest Wharf Road, Karachi, Pakistan."
)

# -----------------------------------------------------------------------------
# 4. PAGE 1: HOME & OVERVIEW
# -----------------------------------------------------------------------------
if menu == "Home & Technology Overview":
    st.title("Welcome to PNPI Karachi")

    st.markdown("""
    Pak Navy Polytechnic Institute (PNPI) is a premier technical training
    institution dedicated to producing high-caliber engineering technicians
    and practical engineers.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="css-card">
            <h3>🤖 Offered Technology</h3>
            <h4 style="color:#6fffe9;">Mechatronics Engineering</h4>
            <p>
            A multidisciplinary field combining mechanical, electrical,
            computer, and control systems engineering to design smart
            automated systems and robotics.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="css-card">
            <h3>📊 Program Structure</h3>
            <ul>
                <li><b>Total Semesters:</b> 5 Semesters</li>
                <li><b>Batch Capacity:</b> 8 Students per Semester</li>
                <li><b>Passing Criteria:</b> Minimum 75% per subject required</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. PAGE 2: COURSES & TEACHERS
# -----------------------------------------------------------------------------
elif menu == "Course Curriculum & Teachers":
    st.title("📚 Mechatronics Engineering - Course Curriculum")
    st.caption("Browse course breakdown and assigned faculty members per semester.")

    selected_sem = st.selectbox(
        "Select Semester to View Details:",
        list(SEMESTER_SUBJECTS.keys())
    )

    st.subheader(f"Subjects & Faculty for {selected_sem}")

    subjects_data = SEMESTER_SUBJECTS[selected_sem]
    df_courses = pd.DataFrame(
        subjects_data,
        columns=["Subject Name", "Assigned Faculty / Instructor"]
    )
    df_courses.index += 1

    st.table(df_courses)

# -----------------------------------------------------------------------------
# 6. PAGE 3: STUDENT RESULT PORTAL
# -----------------------------------------------------------------------------
elif menu == "Student Result Portal":
    st.title("🎓 Student Examination Portal")
    st.write(
        "Enter your credentials below to check your official semester "
        "examination results."
    )

    st.markdown('<div class="css-card">', unsafe_allow_html=True)

    col_input1, col_input2 = st.columns(2)

    with col_input1:
        student_name_input = st.text_input("Enter Student Full Name:")

    with col_input2:
        roll_no_input = st.text_input(
            "Enter Roll Number (e.g., PNPI-101):"
        )

    login_btn = st.button("Check Result", type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("ℹ️ Click here to view sample Login credentials for testing"):
        st.write("Aap niche diye gae Roll Numbers se test kar sakte hain:")
        st.write("- **Roll No:** `PNPI-101` | **Name:** `Ali Raza` (Semester 1)")
        st.write("- **Roll No:** `PNPI-ME-109` | **Name:** `Student 1` (Semester 2)")

    if login_btn:
        if not student_name_input or not roll_no_input:
            st.warning("⚠️ Please enter both your Name and Roll Number.")
        else:
            roll_key = roll_no_input.strip()

            if roll_key in students_db:
                student = students_db[roll_key]

                if student["name"].lower().strip() == student_name_input.lower().strip():
                    st.success(f"Welcome, **{student['name']}**!")

                    st.markdown("### 📋 Student Information")
                    st.write(f"**Roll Number:** {student['roll_no']}")
                    st.write("**Program:** Mechatronics Engineering")
                    st.write(f"**Current Semester:** {student['semester']}")

                    st.markdown("---")
                    st.markdown("### 📝 Semester Marksheet")

                    result_rows = []
                    overall_pass = True

                    for sub, marks in student["marks"].items():
                        status = "PASS" if marks >= 75 else "FAIL"

                        if marks < 75:
                            overall_pass = False

                        result_rows.append({
                            "Subject Name": sub,
                            "Marks Obtained (%)": f"{marks}%",
                            "Passing Marks": "75%",
                            "Status": status
                        })

                    df_results = pd.DataFrame(result_rows)
                    df_results.index += 1

                    st.table(df_results)

                    if overall_pass:
                        st.markdown("""
                            <div style="text-align:center;" class="badge-pass">
                                <h3>🎉 OVERALL STATUS: PASSED</h3>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div style="text-align:center;" class="badge-fail">
                                <h3>
                                ❌ OVERALL STATUS: FAILED
                                (Required: Minimum 75% in all subjects)
                                </h3>
                            </div>
                        """, unsafe_allow_html=True)

                else:
                    st.error(
                        "❌ Name does not match with the provided Roll Number. "
                        "Please check again."
                    )
            else:
                st.error(
                    "❌ Invalid Roll Number. Record not found in PNPI Database."
                )
