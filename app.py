# app.py

import streamlit as st
import pandas as pd
from io import BytesIO
# Import all functions from the config file
from supabase_config import get_all_flights, get_maintenance_summary, call_login_procedure 

# ReportLab Imports for PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# -------------------------------------------------------------------
# 1. PDF Generation Function (The Crystal Reports Alternative)
# -------------------------------------------------------------------

def create_flight_schedule_pdf(data):
    """Generates a professional PDF report from flight data."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            title="Airport Flight Schedule Report")
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Airport Detailed Flight Schedule Report", styles['Title']))
    story.append(Spacer(1, 0.25 * inch))

    # Data Preparation
    df = pd.DataFrame(data)
    report_df = df[['FlightID', 'FromAirportCode', 'ToAirportCode', 'ScheduledDep', 'Status', 'Price']]
    report_df.columns = ['Flight ID', 'From', 'To', 'Departure', 'Status', 'Price ($)']
    
    # Convert DataFrame to list of lists (including header)
    table_data = [report_df.columns.tolist()] + report_df.values.tolist()

    # Create Table object
    table = Table(table_data, colWidths=[0.7*inch, 0.5*inch, 0.5*inch, 1.5*inch, 0.7*inch, 0.7*inch])
    
    # Table Style for professionalism
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')), # Dark Blue Header
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(table)
    doc.build(story)
    
    return buffer.getvalue()


# -------------------------------------------------------------------
# 2. Streamlit UI Functions
# -------------------------------------------------------------------



def set_background_image():
    """Injects CSS to set a background image and stylize the app."""
    # --- ADD THE NEW URL HERE ---
    BACKGROUND_IMAGE_URL = "https://images.unsplash.com/photo-1542296332-2e4473faf563?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YWlycG9ydHxlbnwwfHwwfHx8MA%3D%3D"
    # -----------------------------
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{BACKGROUND_IMAGE_URL}"); /* Use the provided URL */
            background-size: cover;
            background-attachment: fixed; 
            opacity: 0.9;
        }}
        /* Make the main content area slightly transparent white for text clarity */
        .main > div {{
            background-color: rgba(255, 255, 255, 0.95); 
            padding: 10px;
            border-radius: 10px;
        }}
        /* Make the sidebar slightly transparent grey */
        [data-testid="stSidebar"] {{
            background-color: rgba(200, 200, 200, 0.85); 
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
def show_login_page():
    """Displays the login form."""
    st.sidebar.header("Login")
    role_options = ['Admin', 'Pilot', 'Passenger', 'Crew'] 
    
    with st.sidebar.form("login_form"):
        role = st.selectbox("Select Role", role_options)
        email = st.text_input("Email", placeholder="e.g., hassan.admin@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if call_login_procedure(email, password, role):
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = role
                st.sidebar.success(f"Login successful as {role}!")
                st.rerun() # Rerun to switch to dashboard
            else:
                st.sidebar.error("Login failed. Check credentials or role.")

def show_dashboard():
    """Displays content based on the logged-in user's role."""
    
    st.sidebar.success(f"Logged in as: {st.session_state['user_role']}")
    
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state['logged_in'] = False
        st.session_state['user_role'] = None
        st.rerun()

    # --- 1. Flight Schedule (The Main Report) ---
    st.header("1. Global Flight Schedule")
    flights_data = get_all_flights()
    
    if flights_data:
        df_flights = pd.DataFrame(flights_data)
        st.dataframe(df_flights, use_container_width=True)

        # PDF Download Button
        pdf_report = create_flight_schedule_pdf(flights_data)
        st.download_button(
            label="Download Printable Flight Schedule Report (PDF)",
            data=pdf_report,
            file_name="Flight_Schedule_Report.pdf",
            mime="application/pdf"
        )
    else:
        st.info("No flight data available.")

    # --- 2. Admin-Specific Reports ---
    if st.session_state['user_role'] == 'Admin':
        st.markdown("---")
        st.header("2. Admin Only: Maintenance Status Report (Visualization)")
        
        maintenance_data = get_maintenance_summary()
        if maintenance_data:
            df_maintenance = pd.DataFrame(maintenance_data)
            
            # Visualization Report (Bar Chart)
            st.subheader("Maintenance Status Distribution")
            status_counts = df_maintenance['Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            st.bar_chart(status_counts.set_index('Status')) 
            
            st.subheader("Raw Maintenance Data")
            st.dataframe(df_maintenance, use_container_width=True)
        else:
            st.info("No maintenance data available.")


# -------------------------------------------------------------------
# 3. Initialization (The Entry Point)
# -------------------------------------------------------------------

# Set up the Streamlit page
st.set_page_config(layout="wide", page_title="Airport Management Dashboard")
st.title("✈️ Online Airport System ")
set_background_image()

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

# Decide which page to show
if st.session_state['logged_in']:
    show_dashboard()
else:
    show_login_page()