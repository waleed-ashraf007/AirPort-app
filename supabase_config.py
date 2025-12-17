from supabase import create_client, Client
import pandas as pd
import streamlit as st # <-- ADD THIS LINE BACK

# --- 1. Your Supabase Credentials (SECURELY LOADED) ---
# Load keys securely from .streamlit/secrets.toml
# supabase_config.py



# Corrected lines: Use the KEY names defined in secrets.toml
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] 

# ... rest of the file ...

# Initialize the Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------------------------
# 2. Database Interaction Functions
# -------------------------------------------------------------------

def get_all_flights():
 
    try:
        response = supabase.table('Flight').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return []

def get_maintenance_summary():
 
    try:
        response = (
            supabase.table('Maintenance')
            .select('AircraftID, Description, Status, DatePerformed')
            .order('Status', desc=False)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error fetching maintenance: {e}")
        return []

def call_login_procedure(email: str, password: str, role: str):
    
    Calls one of the stored login functions (e.g., sp_loginadmin) 
    via Supabase's Remote Procedure Call (RPC).
    
    
    # Use lowercase naming for the RPC name as required by PostgreSQL/Supabase
    procedure_name = f'sp_login{role}'.lower() 
    
    try:
        response = supabase.rpc(
            procedure_name,
            {'p_email': email, 'p_password': password}
        ).execute()

        # Check the 'success' flag returned by the stored function (1 or 0)
        if response.data and response.data[0]['success'] == 1:
            return True
        else:
            return False
    except Exception as e:
        print(f"RPC call failed during login: {e}")
        return False

if __name__ == "__main__":
    # Quick test to confirm the connection works
    print("Running quick connectivity test...")
    if get_all_flights():
        print("Success: Flight data retrieved.")
    else:
        print("Failure: Could not retrieve flight data.")
    
    # Test Login
    if call_login_procedure('hassan.admin@example.com', 'admin123', 'Admin'):
        print("Success: Admin login test passed.")
    else:
=======
from supabase import create_client, Client
import pandas as pd
import streamlit as st # <-- ADD THIS LINE BACK

# --- 1. Your Supabase Credentials (SECURELY LOADED) ---
# Load keys securely from .streamlit/secrets.toml
# supabase_config.py



# Corrected lines: Use the KEY names defined in secrets.toml
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"] 

# ... rest of the file ...

# Initialize the Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------------------------
# 2. Database Interaction Functions
# -------------------------------------------------------------------

def get_all_flights():
    
    try:
        response = supabase.table('Flight').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return []

def get_maintenance_summary():
   
    try:
        response = (
            supabase.table('Maintenance')
            .select('AircraftID, Description, Status, DatePerformed')
            .order('Status', desc=False)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error fetching maintenance: {e}")
        return []

def call_login_procedure(email: str, password: str, role: str):
    """
    Calls one of the stored login functions (e.g., sp_loginadmin) 
    via Supabase's Remote Procedure Call (RPC).
    """
    
    # Use lowercase naming for the RPC name as required by PostgreSQL/Supabase
    procedure_name = f'sp_login{role}'.lower() 
    
    try:
        response = supabase.rpc(
            procedure_name,
            {'p_email': email, 'p_password': password}
        ).execute()

        # Check the 'success' flag returned by the stored function (1 or 0)
        if response.data and response.data[0]['success'] == 1:
            return True
        else:
            return False
    except Exception as e:
        print(f"RPC call failed during login: {e}")
        return False

if __name__ == "__main__":
    # Quick test to confirm the connection works
    print("Running quick connectivity test...")
    if get_all_flights():
        print("Success: Flight data retrieved.")
    else:
        print("Failure: Could not retrieve flight data.")
    
    # Test Login
    if call_login_procedure('hassan.admin@example.com', 'admin123', 'Admin'):
        print("Success: Admin login test passed.")
    else:
        4cc418048101a14e48cb2fc3e7ec23ed556a6702
        print("Failure: Admin login test failed.")
