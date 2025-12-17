from supabase import create_client, Client
import streamlit as st

# --- 1. Supabase Credentials ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    st.error("Secrets not found! Make sure .streamlit/secrets.toml exists.")
    st.stop()

# Initialize the Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------------------------
# 2. Database Interaction Functions
# -------------------------------------------------------------------

def get_all_flights():
    """Fetch all flights."""
    try:
        response = supabase.table('Flight').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return []

def get_maintenance_summary():
    """Fetch maintenance data."""
    try:
        response = (
            supabase.table('Maintenance')
            .select('*')  # Select * is safer to avoid KeyErrors
            .order('Status', desc=False)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error fetching maintenance: {e}")
        return []

def call_login_procedure(email: str, password: str, role: str):
    """
    Calls the stored login procedure.
    Handles different return formats from Supabase RPC.
    """
    procedure_name = f'sp_login{role}'.lower()
    
    try:
        response = supabase.rpc(
            procedure_name,
            {'p_email': email, 'p_password': password}
        ).execute()

        # LOGIC FIX: Supabase RPC return values can vary.
        # It might return True, 1, [1], or [{'success': 1}]
        data = response.data
        
        if data:
            # If data is a list (e.g., [{'success': 1}] or [1])
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                # Check for dictionary format
                if isinstance(first_item, dict):
                    return first_item.get('success', 0) == 1
                # Check for direct integer format
                return first_item == 1
            
            # If data is a direct scalar (e.g., 1 or True)
            if data == 1 or data is True:
                return True
                
        return False

    except Exception as e:
        print(f"RPC call failed during login: {e}")
        return False

def get_passenger_bookings(passenger_pno: str):
    """Fetch bookings for a specific passenger by PassportNo."""
    try:
        # --- CRITICAL FIX HERE ---
        # Changed specific columns to '*' so we don't miss 'PassengerPNO'
        # causing the KeyError in the PDF generator.
        response = (
            supabase.table('Bookings')
            .select('*') 
            .eq('PassengerPNO', passenger_pno)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        return []

def get_passenger_by_email(email: str):
    """Fetch a single Passenger record by email."""
    try:
        response = (
            supabase.table('Passenger')
            .select('*')
            .eq('Email', email)
            # .single() raises an error if no rows found, so we handle that in except
            .single() 
            .execute()
        )
        return response.data
    except Exception as e:
        # It is normal to fail if user doesn't exist yet or email is wrong
        print(f"Error/Info fetching user by email: {e}")
        return None

# -------------------------------------------------------------------
# 3. Connection Test (Only runs if you run this file directly)
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("Running quick connectivity test...")
    
    # Test 1: Fetch Flights
    flights = get_all_flights()
    if flights:
        print(f"Success: Retrieved {len(flights)} flights.")
    else:
        print("Failure: Could not retrieve flight data.")
    
    # Test 2: Login (Change credentials to a real user in your DB)
    if call_login_procedure('hassan.admin@example.com', 'admin123', 'Admin'):
        print("Success: Admin login test passed.")
    else:
        print("Failure: Admin login test failed.")
