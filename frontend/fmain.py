import streamlit as st
import requests
import datetime
import pandas as pd

# --- CONFIGURATION ---
API_URL = "https://bookit-api-naxn.onrender.com/api/v1"
st.set_page_config(page_title="Booking System", page_icon="📅", layout="wide")
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        color: #d1d1d1;
    }
    
    /* The Red Sidebar */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#4a0404, #1a0202);
        border-right: 2px solid #8b0000;
    }
    
    /* Lab-style Header */
    h1, h2, h3 {
        color: #ff4b4b !important;
        font-family: 'Courier New', Courier, monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Buttons that look like Emergency Kill-Switches */
    .stButton>button {
        color: #ffffff;
        background-color: #8b0000;
        border: 2px solid #ff0000;
        border-radius: 0px; /* Sharp edges for a clinical look */
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ff0000;
        border-color: #ffffff;
        color: black;
        box-shadow: 0 0 15px #ff0000;
    }

    /* Input box styling */
    .stTextInput>div>div>input {
        background-color: #1a1a1a;
        color: #ff4b4b;
        border: 1px solid #4a0404;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_headers():
    """Returns the Authorization header with the current JWT token."""
    if "token" in st.session_state and st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}

def login(email, password):
    """Authenticates the user and returns the token."""
    try:
        res = requests.post(f"{API_URL}/login/access-token", data={"username": email, "password": password})
        if res.status_code == 200:
            return res.json()
        else:
            st.error(f"Login failed: {res.text}")
    except Exception as e:
        st.error(f"Connection Error: {e}")
    return None

def register(email, password, full_name):
    """Creates a new user account."""
    try:
        payload = {
            "email": email,
            "password": password,
            "full_name": full_name,
            "is_active": True
        }
        res = requests.post(f"{API_URL}/users/", json=payload)
        if res.status_code == 200:
            return True
        else:
            st.error(f"Registration failed: {res.text}")
    except Exception as e:
        st.error(f"Connection Error: {e}")
    return False

def get_current_user_role(token):
    """Checks if the logged-in user is an Admin."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        res = requests.get(f"{API_URL}/users/me", headers=headers)
        if res.status_code == 200:
            user_data = res.json()
            return user_data.get("is_superuser", False)
    except:
        pass
    return False

def fetch_resources():
    """Gets list of available rooms/resources."""
    try:
        res = requests.get(f"{API_URL}/resources/", headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except:
        return []

def fetch_my_bookings():
    """Gets the logged-in user's bookings."""
    try:
        res = requests.get(f"{API_URL}/bookings/", headers=get_headers())
        return res.json() if res.status_code == 200 else []
    except:
        return []

def book_resource(resource_id, start_dt, end_dt):
    """Sends a booking request."""
    payload = {
        "resource_id": resource_id,
        "start_time": start_dt.isoformat(),
        "end_time": end_dt.isoformat()
    }
    try:
        res = requests.post(f"{API_URL}/bookings/", json=payload, headers=get_headers())
        return res
    except Exception as e:
        st.error(f"Booking Error: {e}")
        return None

# --- UI STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --- MAIN APP LOGIC ---
if not st.session_state.token:
    # 🔐 AUTH SCREEN (Login + Sign Up)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📘 Bookit.")
        
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        
        # TAB 1: LOGIN
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_pass")
                submit_login = st.form_submit_button("Login")
                
                if submit_login:
                    data = login(email, password)
                    if data:
                        token = data["access_token"]
                        st.session_state.token = token
                        # Check Admin Role immediately after login
                        st.session_state.is_admin = get_current_user_role(token)
                        st.success("Login Successful!")
                        st.rerun()

        # TAB 2: SIGN UP
        with tab_signup:
            with st.form("signup_form"):
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submit_signup = st.form_submit_button("Create Account")
                
                if submit_signup:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif not new_email or not new_password:
                        st.error("❌ Please fill in all fields.")
                    else:
                        if register(new_email, new_password, new_name):
                            st.success("✅ Account created! Switch to Login tab.")
                            st.balloons()

else:
    # 🏠 DASHBOARD SCREEN
    with st.sidebar:
        st.title("Navigation")
        st.sidebar.image("https://img.icons8.com/ios-filled/100/8b0000/blood-drop.png", width=50)
        
        # DYNAMIC MENU: Only show Admin Panel if user is Admin
        options = ["Book a Room", "My Bookings"]
        if st.session_state.is_admin:
            options.append("Admin Panel")
            
        page = st.radio("Go to", options)
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.is_admin = False
            st.rerun()

    if page == "Book a Room":
        st.title("📅 Book a Resource")
        
        resources = fetch_resources()
        if resources:
            res_options = {r["name"]: r["id"] for r in resources}
            selected_name = st.selectbox("Select a Room", list(res_options.keys()))
            selected_id = res_options[selected_name]
            
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", datetime.date.today())
            with col2:
                start_time = st.time_input("Start Time", datetime.time(9, 0))
                duration = st.number_input("Duration (hours)", min_value=1, max_value=8, value=1)
            
            if st.button("Confirm Booking"):
                start_dt = datetime.datetime.combine(date, start_time)
                end_dt = start_dt + datetime.timedelta(hours=duration)
                
                with st.spinner("Booking..."):
                    res = book_resource(selected_id, start_dt, end_dt)
                    if res and res.status_code == 200:
                        st.success("✅ Booking Confirmed!")
                        st.balloons()
                    elif res and res.status_code == 409:
                        st.error("⚠️ Conflict! This room is already booked.")
                    else:
                        st.error(f"Error: {res.text if res else 'Unknown'}")
        else:
            st.warning("No resources found. Ask an admin to add rooms!")

    elif page == "My Bookings":
        st.title("🎟️ My Bookings")
        bookings = fetch_my_bookings()
        if bookings:
            df = pd.DataFrame(bookings)
            cols_to_show = ["resource_id", "start_time", "end_time", "status"]
            valid_cols = [c for c in cols_to_show if c in df.columns]
            
            # Display the data
            st.dataframe(df[valid_cols], width=1000) 

            # --- THE EXPORT FEATURE ---
            st.markdown("---")
            csv = df[valid_cols].to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="🩸 Export Evidence (CSV)",
                data=csv,
                file_name=f"forensic_report_{datetime.date.today()}.csv",
                mime="text/csv",
                help="Download your booking history for forensic analysis."
            )
        else:
            st.info("No evidence found in the logs.")

    elif page == "Admin Panel":
        # Double check role here for security
        if not st.session_state.is_admin:
            st.error("⛔ Access Denied")
        else:
            st.title("🛠️ Admin Controls")
            
            st.subheader("Add New Resource")
            with st.form("add_resource_form"):
                name = st.text_input("Resource Name (e.g., Conference Room A)")
                type_ = st.selectbox("Type", ["Room", "Desk", "Equipment"])
                capacity = st.number_input("Capacity", min_value=1, value=5)
                description = st.text_area("Description")
                
                if st.form_submit_button("Create Resource"):
                    payload = {"name": name, "type": type_, "capacity": capacity, "description": description}
                    try:
                        res = requests.post(f"{API_URL}/resources/", json=payload, headers=get_headers())
                        if res.status_code == 200:
                            st.success(f"✅ Created: {name}")
                            st.balloons()
                        elif res.status_code == 403:
                            st.error("⛔ Forbidden: You are not an Admin.")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Connection Failed: {e}")
