import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# Import functions
from supabase_config import (
    get_all_flights,
    get_maintenance_summary,
    get_passenger_bookings,
    call_login_procedure,
    get_passenger_by_email
)

# -------------------------------------------------------------------
# 1. PDF Generation Functions
# -------------------------------------------------------------------
def create_flight_schedule_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="Flight Schedule")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Airport Flight Schedule Report", styles['Title']))
    story.append(Spacer(1, 0.25 * inch))

    df = pd.DataFrame(data)
    # Ensure columns exist before selecting
    cols = ['FlightID', 'FromAirportCode', 'ToAirportCode', 'ScheduledDep', 'Status', 'Price']
    available_cols = [c for c in cols if c in df.columns]
    
    report_df = df[available_cols]
    
    table_data = [report_df.columns.tolist()] + report_df.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ]))
    story.append(table)
    doc.build(story)
    return buffer.getvalue()

def create_ticket_pdf(booking, flight):
    """Generate a PDF ticket for a single booking"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="E-Ticket")
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("✈️ Your E-Ticket", styles['Title']))
    story.append(Spacer(1, 0.2*inch))

    # --- FIX: Use .get() to handle case-sensitivity safely ---
    booking_id = booking.get("BookingID") or booking.get("bookingid") or "N/A"
    pno = booking.get("PassengerPNO") or booking.get("passengerpno") or "N/A"
    flight_id = booking.get("FlightID") or booking.get("flightid") or "N/A"
    seat = booking.get("SeatNumber") or booking.get("seatnumber") or "N/A"
    time = booking.get("BookingTime") or booking.get("bookingtime") or "N/A"
    weight = booking.get("BaggageWeight") or booking.get("baggageweight") or 0

    # Booking Info
    booking_data = [
        ["Booking ID", str(booking_id)],
        ["Passenger PNO", str(pno)],
        ["Flight ID", str(flight_id)],
        ["Seat Number", str(seat)],
        ["Booking Time", str(time)],
        ["Baggage Weight (kg)", str(weight)]
    ]
    
    table = Table(booking_data, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))

    # Flight Info
    # Use .get() here as well
    flight_from = flight.get("FromAirportCode") or flight.get("fromairportcode") or ""
    flight_to = flight.get("ToAirportCode") or flight.get("toairportcode") or ""
    flight_dep = flight.get("ScheduledDep") or flight.get("scheduleddep") or ""
    flight_status = flight.get("Status") or flight.get("status") or ""
    flight_price = flight.get("Price") or flight.get("price") or ""

    flight_data = [
        ["From", flight_from],
        ["To", flight_to],
        ["Departure", str(flight_dep)],
        ["Status", flight_status],
        ["Price ($)", str(flight_price)]
    ]
    table2 = Table(flight_data, colWidths=[2*inch, 3*inch])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0B3C5D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(table2)

    doc.build(story)
    return buffer.getvalue()

# -------------------------------------------------------------------
# 2. Streamlit UI Functions
# -------------------------------------------------------------------
def set_background_image():
    BACKGROUND_IMAGE_URL = "https://images.unsplash.com/photo-1542296332-2e4473faf563?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YWlycG9ydHxlbnwwfHwwfHx8MA%3D%3D"
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{BACKGROUND_IMAGE_URL}");
        background-size: cover;
        background-attachment: fixed;
    }}
    .main > div {{
        background-color: rgba(255,255,255,0.95);
        padding: 20px;
        border-radius: 10px;
        color: black;
    }}
    h1,h2,h3,h4,h5 {{ color:black; }}
    [data-testid="stSidebar"] {{
        background-color: rgba(200,200,200,0.85);
    }}
    .team-box {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: rgba(255,255,255,0.92);
        padding: 14px 18px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        color: #0B3C5D;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
        z-index: 9999;
    }}
    </style>
    """, unsafe_allow_html=True)

# Login page
def show_login_page():
    st.sidebar.header("Login")
    role_options = ['Admin','Pilot','Passenger','Crew']
    with st.sidebar.form("login_form"):
        role = st.selectbox("Select Role", role_options)
        email = st.text_input("Email", placeholder="e.g., hassan.admin@example.com")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if call_login_procedure(email, password, role):
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = role
                st.session_state['user_email'] = email
                
                # Fetch PassportNo for Passenger
                if role == "Passenger":
                    passenger_info = get_passenger_by_email(email)
                    if passenger_info:
                        # Use .get() here too to be safe
                        pno = passenger_info.get('PassportNo') or passenger_info.get('passportno')
                        st.session_state['user_pno'] = pno
                    else:
                        st.error("Could not find passenger details.")
                        
                st.sidebar.success(f"Login successful as {role}!")
                st.rerun()
            else:
                st.sidebar.error("Login failed. Check credentials or role.")

# Admin dashboard
def show_dashboard():
    st.sidebar.success(f"Logged in as: {st.session_state['user_role']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.header("1. Global Flight Schedule")
    flights_data = get_all_flights()
    if flights_data:
        df_flights = pd.DataFrame(flights_data)
        st.dataframe(df_flights, use_container_width=True)
        pdf_report = create_flight_schedule_pdf(flights_data)
        st.download_button("Download Flight Schedule PDF", pdf_report, "Flight_Schedule.pdf","application/pdf")
    else:
        st.info("No flight data available.")

    if st.session_state['user_role']=='Admin':
        st.markdown("---")
        st.header("2. Admin Only: Maintenance Report")
        maintenance_data = get_maintenance_summary()
        if maintenance_data:
            df_maintenance = pd.DataFrame(maintenance_data)
            st.subheader("Maintenance Status Distribution")
            status_counts = df_maintenance['Status'].value_counts().reset_index()
            status_counts.columns=['Status','Count']
            st.bar_chart(status_counts.set_index('Status'))
            st.subheader("Raw Maintenance Data")
            st.dataframe(df_maintenance, use_container_width=True)

# Passenger dashboard
def show_passenger_dashboard():
    st.header("My Bookings and E-Tickets")
    
    # Sidebar Logout (Required here too)
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    passenger_pno = st.session_state.get("user_pno")
    if not passenger_pno:
        st.error("Error: Passenger PassportNo not found. Please log in again.")
        return

    bookings = get_passenger_bookings(passenger_pno)
    if not bookings:
        st.info("You do not have any active bookings.")
        return

    df = pd.DataFrame(bookings)
    st.subheader("Current Bookings")
    st.dataframe(df, use_container_width=True)

    # Generate PDF for each booking
    flights = get_all_flights() # Fetch once outside loop for efficiency
    
    st.markdown("---")
    st.subheader("Download Tickets")
    
    for i, booking in enumerate(bookings):
        # Match booking flight ID to flight list
        flight_id = booking.get("FlightID") or booking.get("flightid")
        
        # Find matching flight
        flight_info = next((f for f in flights if f.get("FlightID") == flight_id), {})

        # Generate PDF
        try:
            pdf_bytes = create_ticket_pdf(booking, flight_info)
            
            # --- FIX: UNIQUE KEY for every button ---
            booking_id = booking.get("BookingID") or booking.get("bookingid") or i
            
            st.download_button(
                label=f"Download Ticket (Booking #{booking_id})",
                data=pdf_bytes,
                file_name=f"E_Ticket_{booking_id}.pdf",
                mime="application/pdf",
                key=f"btn_{booking_id}" # Unique key prevents Streamlit errors
            )
        except Exception as e:
            st.error(f"Error generating ticket for Booking {booking_id}: {e}")


# -------------------------------------------------------------------
# 3. App Initialization / Entry Point
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# 3. App Initialization / Entry Point
# -------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Airport Management Dashboard")
# st.title("Happy to Serve") # You can remove this if you want the bottom title to be the main one
set_background_image()

# --- MODIFIED: Team Box + Big Bottom Title ---
st.markdown("""
    <style>
    /* 1. CSS for Team Box (Bottom Right) */
    .team-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: rgba(255,255,255,0.9);
        padding: 15px 20px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        color: #0B3C5D;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        z-index: 9999;
    }
    
    /* 2. CSS for Big Bottom Title (Bottom Middle) */
    .bottom-title {
        position: fixed;
        bottom: 30px;         /* Distance from bottom */
        left: 50%;            /* Center horizontally */
        transform: translateX(-50%); /* Perfect centering adjustment */
        
        font-size: 3.5rem;    /* Big Font Size */
        font-weight: 900;     /* Extra Bold */
        font-family: 'Arial Black', sans-serif;
        
        /* Styling to make it pop on any background */
        color: #FFFFFF;       /* White Text */
        text-shadow: 3px 3px 0px #003366, /* 3D effect dark blue shadow */
                     6px 6px 10px rgba(0,0,0,0.5); /* Soft drop shadow */
        
        z-index: 9998;        /* Layer order */
        text-align: center;
        width: 100%;
        pointer-events: none; /* Allows you to click things behind the text area if needed */
    }
    </style>

    <div class="team-box">
        <div>Waleed Ashraf</div>
        <div>Bishoy Botros</div>
        <div>Omar Ismail</div>
        <div>Meriam Tamer</div>
    </div>

    <div class="bottom-title">
        Online Airport System
    </div>
""", unsafe_allow_html=True)


# --- Session State & Routing Logic (Keep this exactly as you have it) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None

if st.session_state['logged_in']:
    if st.session_state['user_role'] == "Admin":
        show_dashboard()
    elif st.session_state['user_role'] == "Passenger":
        show_passenger_dashboard()
    else:
        st.info(f"No dashboard implemented for role: {st.session_state['user_role']}")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()
else:
    show_login_page()
