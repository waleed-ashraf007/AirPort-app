from supabase import create_client, Client
import pandas as pd
import streamlit as st

# -------------------------------------------------------------------
# 1. Supabase Credentials (from .streamlit/secrets.toml)
# -------------------------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Initialize the Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------------------------------
# 2. Database Interaction Functions
# -------------------------------------------------------------------

def get_all_flights():
    """
    Fetch all flights from the Flight table.
    """
    try:
        # If your table is named "flights" (lowercase) in Supabase, use 'flights' instead of 'Flight'
        response = supabase.table('Flight').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error fetching flights: {e}")
        return []


def get_maintenance_summary():
    """
    Fetch basic maintenance information from the Maintenance table.
    """
    try:
        # Adjust table/column names if different in Supabase
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


def call_login_procedure(email: str, password: str, role: str) -> bool:
    """
    Calls one of the stored login functions (e.g., sp_loginadmin)
    via Supabase's Remote Procedure Call (RPC).

    role should be one of: "Passenger", "Admin", "Pilot", "Crew"
    if your functions in Postgres are named sp_loginpassenger, sp_loginadmin, etc.
    """
    # Build the RPC function name: e.g. "sp_loginadmin"
    procedure_name = f"sp_login{role}".lower()  # -> sp_loginadmin, sp_loginpilot, ...

    try:
        # Parameter names must match the function definition in Postgres (p_email, p_password)
        response = supabase.rpc(
            procedure_name,
            {"p_email": email, "p_password": password}
        ).execute()

        # If your Postgres function RETURNS int (1 or 0), response.data is usually a scalar or list.
        # Example if it returns integer directly: response.data == 1
        if response.data == 1:
            return True
        # If it returns a record like {success: 1}, uncomment this and adapt:
        # if response.data and isinstance(response.data, list) and response.data[0].get("success") == 1:
        #     return True

        return False

    except Exception as e:
        print(f"RPC call failed during login: {e}")
        return False


# -------------------------------------------------------------------
# 3. Quick CLI Test (optional)
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("Running quick connectivity test...")

    flights = get_all_flights()
    if flights:
        print(f"Success: Retrieved {len(flights)} flights.")
    else:
        print("Failure: Could not retrieve flight data.")

    # Test login for an Admin user (email/password must exist and match in DB)
    if call_login_procedure("hassan.admin@example.com", "admin123", "Admin"):
        print("Success: Admin login test passed.")
    else:
        print("Failure: Admin login test failed.")
