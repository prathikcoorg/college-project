import streamlit as st
import requests
import json
import hashlib
import os


USER_DB = "users.json"

def load_users():
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump([], f)
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    users = load_users()
    for user in users:
        if user["email"] == email and user["password"] == hash_password(password):
            return True
    return False

def user_exists(email):
    users = load_users()
    return any(user["email"] == email for user in users)

def add_user(email, password):
    users = load_users()
    users.append({"email": email, "password": hash_password(password)})
    save_users(users)


st.set_page_config(page_title="Job Finder", page_icon="🧭", layout="wide")

def login_signup_ui():
    
    st.markdown("""
        <style>
            .centered {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                gap: 0.5rem;
            }
            .radio-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 1rem;
            }
            .radio-container label {
                align: center;
                display: block;
                width: 100%;
            }
            .stRadio > div {
                display: flex;
                justify-content: center;
                gap: 1rem;
            }
            .stTextInput, .stButton {
                width: 300px !important;
                margin: 0 auto !important;
            }
        </style>
    """, unsafe_allow_html=True)


    st.markdown("<h1 style='text-align: center;'>🔍 Welcome to Job Finder</h1>", unsafe_allow_html=True)
    
    
    with st.container():
        st.markdown('<div class="centered">', unsafe_allow_html=True)
        
        
        st.markdown('<div class="radio-container">', unsafe_allow_html=True)
        choice = st.radio("Are you a new user?", 
                         ["Yes, Sign Up", "Already have an account? Login"],
                         horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if choice == "Already have an account? Login":
            email = st.text_input("Email", key="email_input")
            password = st.text_input("Password", type="password", key="password_input")

            login_button = st.button("Login", use_container_width=True)
            if login_button:
                if authenticate_user(email, password):
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.success("Login successful 🎉")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        elif choice == "Yes, Sign Up":
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")

            signup_button = st.button("Sign Up", use_container_width=True)
            if signup_button:
                if user_exists(email):
                    st.warning("Email already registered.")
                else:
                    add_user(email, password)
                    st.session_state.authenticated = True
                    st.session_state.email = email
                    st.success("Account created successfully!")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def job_finder_ui():
   
    st.markdown("""
        <style>
        body {
            background-color: #0d0d0d;
            color: #f0f0f0;
        }
        .stApp {
            background-color: #0d0d0d;
        }
        h1, h4, label, .stSelectbox label {
            color: #00d2ff !important;
        }
        .job-card {
            background-color: #1a1a1a;
            padding: 16px;
            border-radius: 15px;
            margin-bottom: 16px;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.05);
            font-size: 14px;
        }
        .job-title {
            font-size: 16px;
            font-weight: bold;
            color: #33ccff;
        }
        a {
            color: #33ccff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .job-meta {
            margin-top: 6px;
            font-size: 13px;
            color: #b3b3b3;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🧭 Job Finder Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 15px;'>Search jobs from LinkedIn, JSearch, and Adzuna</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #222;'>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        job_title = st.text_input("💼 Job Title", "Python Developer")
    with col2:
        location = st.text_input("🌍 Location", "India")
    with col3:
        platform = st.selectbox("🛠️ Platform", ["All", "LinkedIn", "JSearch", "Adzuna"])

    search_btn = st.button("🔎 Search", use_container_width=True)

    if search_btn:
        with st.spinner("Searching for jobs..."):
            api_url = f"http://127.0.0.1:5000/search?title={job_title}&location={location}"
            response = requests.get(api_url)

        if response.status_code == 200:
            jobs = response.json()
            filtered_jobs = [job for job in jobs if platform == "All" or job["source"] == platform]

            if filtered_jobs:
                st.success(f"🎯 {len(filtered_jobs)} job(s) found")
                job_cols = st.columns(2)

                for index, job in enumerate(filtered_jobs):
                    with job_cols[index % 2]:
                        st.markdown(f"""
                            <div class="job-card">
                                <div class="job-title">
                                    <a href="{job['link']}" target="_blank">🔗 {job['title']}</a>
                                </div>
                                <div class="job-meta">🏢 <b>Company:</b> {job['company']}</div>
                                <div class="job-meta">📍 <b>Location:</b> {job['location']}</div>
                                <div class="job-meta">🌐 <b>Source:</b> {job['source']}</div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No jobs found. Try different search terms.")
        else:
            st.error("Error fetching job listings from the server.")

    st.markdown("---")
    if st.button("🔓 Logout"):
        st.session_state.authenticated = False
        st.session_state.email = ""
        st.rerun()


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated:
    job_finder_ui()
else:
    login_signup_ui()
