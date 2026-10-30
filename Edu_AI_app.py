"""EduAI | Student Success & Retention AI — student portal prototype.

Fictional student records and a rule-based academic support flag.
Run: python -m streamlit run Edu_AI_app.py
"""
import html
import pandas as pd
import streamlit as st

st.set_page_config(page_title="EduAI | Student Success & Retention AI", page_icon="E", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { --navy:#142D4E; --navy2:#203D60; --grey:#64748B; --border:#DCE3EA; }
.stApp { background:#FFFFFF; color:#1D2939; }
h1,h2,h3 { color:#142D4E !important; letter-spacing:-.02em; }
[data-testid="stSidebar"] { background:#F2F5F8; border-right:1px solid #DCE3EA; }
[data-testid="stSidebar"] * { color:#142D4E; }
[data-testid="stMetric"] { background:#FFF; border:1px solid #DCE3EA; border-radius:9px; padding:17px; }
.stButton button[kind="primary"], [data-testid="stFormSubmitButton"] button { background:#142D4E !important; color:white !important; border:1px solid #142D4E !important; border-radius:7px; }
.stButton button { border-radius:7px; }
[data-testid="stProgressBar"] div[role="progressbar"] > div { background:#142D4E !important; }
.edu-header { background:#142D4E; border-radius:10px; padding:29px 34px; margin-bottom:22px; }
.edu-header h1 { color:#FFFFFF !important; margin:0 0 6px; font-size:2rem; }
.edu-header p { color:#DFE7F0; margin:0; }
.edu-panel { background:#FFFFFF; border:1px solid #DCE3EA; border-radius:9px; padding:18px 22px; margin:12px 0; }
.edu-panel h3 { margin:0 0 7px; font-size:1.12rem; }
.edu-muted { color:#64748B; font-size:.91rem; }
.edu-badge { display:inline-block; padding:5px 11px; border-radius:5px; font-weight:650; font-size:.83rem; }
.edu-badge-risk { background:#FBE9E8; color:#9B2525; }
.edu-badge-good { background:#E7F2EC; color:#216243; }
</style>
""", unsafe_allow_html=True)

# Fictional academic records. These are NOT data from the trained ML model.
STUDENTS = {
    "EDU001": {
        "name": "Lerato Mokoena", "password": "Demo123!",
        "course": "Diploma in Information Technology", "year": "Year 3",
        "modules": {
            "Development Software": [("Assignment 1",85),("Practical Test",78),("Quiz 1",90),("Assignment 2",None)],
            "Business Analysis": [("Assignment 1",75),("Test 1",68),("Quiz 1",82),("Assignment 2",None)],
            "Information Systems": [("Assignment 1",88),("Test 1",79),("Quiz 1",84)],
            "System Software": [("Quiz 1",91),("Test 1",85),("Assignment 1",None)],
        },
    },
    "EDU002": {
        "name": "Thabo Dlamini", "password": "Demo123!",
        "course": "Diploma in Information Technology", "year": "Year 3",
        "modules": {
            "Development Software": [("Assignment 1",39),("Practical Test",32),("Quiz 1",45),("Assignment 2",None)],
            "Business Analysis": [("Assignment 1",41),("Test 1",35),("Quiz 1",43),("Assignment 2",None)],
            "Information Systems": [("Assignment 1",46),("Test 1",38),("Quiz 1",None)],
            "System Software": [("Quiz 1",44),("Test 1",40),("Assignment 1",None)],
        },
    },
}


def marks_for(assessments):
    return [mark for _, mark in assessments if mark is not None]


def average_for(assessments):
    marks = marks_for(assessments)
    return sum(marks) / len(marks) if marks else None


def completion_for(assessments):
    return len(marks_for(assessments)) / len(assessments) if assessments else 0.0


def summary_for(student):
    assessments = [a for items in student["modules"].values() for a in items]
    marks = marks_for(assessments)
    return {
        "modules": len(student["modules"]),
        "completed": len(marks),
        "total": len(assessments),
        "pending": len(assessments) - len(marks),
        "average": sum(marks) / len(marks) if marks else None,
        "completion": len(marks) / len(assessments) if assessments else 0,
    }


def login():
    st.markdown('<div class="edu-header"><h1>EduAI</h1><p>Student Success &amp; Retention AI</p></div>', unsafe_allow_html=True)
    _, middle, _ = st.columns([1, 1.15, 1])
    with middle:
        st.subheader("Student sign in")
        st.write("Access your modules, assessment results and academic support.")
        with st.form("student_login", clear_on_submit=False):
            student_number = st.text_input("Student number", placeholder="Student number")
            password = st.text_input("Password", type="password", placeholder="Password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submitted:
            student_number = student_number.strip().upper()
            student = STUDENTS.get(student_number)
            if student is not None and password == student["password"]:
                st.session_state["eduai_student_id"] = student_number
                st.rerun()
            else:
                st.error("Student number or password is incorrect.")


def dashboard(student):
    name = html.escape(student["name"].split()[0])
    st.markdown(f'<div class="edu-header"><h1>Welcome back, {name}</h1><p>Your academic overview and progress</p></div>', unsafe_allow_html=True)
    summary = summary_for(student)
    cols = st.columns(4)
    cols[0].metric("Enrolled modules", summary["modules"])
    cols[1].metric("Assessments completed", f'{summary["completed"]}/{summary["total"]}')
    cols[2].metric("Average mark", f'{summary["average"]:.1f}%' if summary["average"] is not None else "N/A")
    cols[3].metric("Pending assessments", summary["pending"])
    st.subheader("Academic standing")
    if summary["average"] is not None and summary["average"] < 50:
        st.error("At risk of failing — your current average is below 50%. Please contact your lecturer or academic support team and prioritise outstanding assessments.")
    elif summary["average"] is not None:
        st.success("On track — your current average is at least 50%. Continue preparing for upcoming assessments.")
    else:
        st.info("Your academic standing will appear after marks are available.")
    st.caption("Academic standing is a demonstration rule based on fictional marks, not a neural-network prediction.")
    st.subheader("Assessment completion")
    st.progress(summary["completion"])
    st.caption(f'{summary["completion"]:.0%} of listed assessments completed')
    st.subheader("My modules")
    cols = st.columns(2)
    for i, (module, assessments) in enumerate(student["modules"].items()):
        avg = average_for(assessments)
        with cols[i % 2]:
            label = f"{avg:.1f}% average" if avg is not None else "No marks yet"
            st.markdown(f'<div class="edu-panel"><h3>{html.escape(module)}</h3><div class="edu-muted">{label}</div></div>', unsafe_allow_html=True)
            st.progress(completion_for(assessments))
            st.caption(f'{completion_for(assessments):.0%} completed')


def modules_page(student):
    st.title("My modules")
    st.write("Review performance and assessment completion in each module.")
    for module, assessments in student["modules"].items():
        with st.expander(module, expanded=True):
            avg = average_for(assessments)
            a, b = st.columns(2)
            a.metric("Average mark", f"{avg:.1f}%" if avg is not None else "N/A")
            b.metric("Completion", f"{completion_for(assessments):.0%}")
            st.progress(completion_for(assessments))
            rows = [{"Assessment": title, "Mark (%)": mark, "Status": "Completed" if mark is not None else "Pending"} for title, mark in assessments]
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
            if avg is not None and avg < 50:
                st.warning("This module needs attention. Review feedback and contact your lecturer.")


def assessments_page(student):
    st.title("My assessments")
    rows = [{"Module": module, "Assessment": title, "Mark (%)": mark, "Status": "Completed" if mark is not None else "Pending"}
            for module, assessments in student["modules"].items() for title, mark in assessments]
    df = pd.DataFrame(rows)
    selected = st.selectbox("Filter by module", ["All modules", *student["modules"].keys()])
    if selected != "All modules":
        df = df[df["Module"] == selected]
    st.dataframe(df, hide_index=True, use_container_width=True)
    completed = df.dropna(subset=["Mark (%)"]).copy()
    if not completed.empty:
        completed["Assessment"] = completed["Module"] + " | " + completed["Assessment"]
        st.subheader("Assessment marks")
        st.bar_chart(completed.set_index("Assessment")["Mark (%)"])


def chatbot_page(student):
    st.title("EduAI student support")
    st.write("Ask about study strategies, academic performance and time management.")
    from chatbot import RiskChatbot
    if "eduai_bot" not in st.session_state:
        st.session_state["eduai_bot"] = RiskChatbot()
    if "eduai_chats" not in st.session_state:
        st.session_state["eduai_chats"] = {}
    sid = st.session_state["eduai_student_id"]
    messages = st.session_state["eduai_chats"].setdefault(sid, [])
    for message in messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    question = st.chat_input("Ask a question")
    if question:
        messages.append({"role": "user", "content": question})
        bot = st.session_state["eduai_bot"]
        if hasattr(bot, "get_response"):
            response = bot.get_response(question)
        elif hasattr(bot, "respond"):
            response = bot.respond(question)
        elif hasattr(bot, "answer"):
            response = bot.answer(question)
        else:
            response = "Chatbot response method needs to be connected to this interface."
        messages.append({"role": "assistant", "content": str(response)})
        st.rerun()


if "eduai_student_id" not in st.session_state:
    st.session_state["eduai_student_id"] = None

sid = st.session_state["eduai_student_id"]
if sid not in STUDENTS:
    st.session_state["eduai_student_id"] = None
    login()
else:
    student = STUDENTS[sid]
    st.sidebar.title("EduAI")
    st.sidebar.caption("Student Success & Retention AI")
    st.sidebar.divider()
    st.sidebar.write(f'**{student["name"]}**')
    st.sidebar.caption(student["course"])
    st.sidebar.caption(student["year"])
    st.sidebar.divider()
    page = st.sidebar.radio("Navigation", ["Dashboard", "My modules", "My assessments", "Student support"])
    st.sidebar.divider()
    if st.sidebar.button("Sign out", use_container_width=True):
        st.session_state["eduai_student_id"] = None
        st.rerun()
    if page == "Dashboard":
        dashboard(student)
    elif page == "My modules":
        modules_page(student)
    elif page == "My assessments":
        assessments_page(student)
    else:
        try:
            chatbot_page(student)
        except Exception as error:
            st.error("The chatbot could not be loaded. Its interface may need an adjustment.")
            st.caption(str(error))