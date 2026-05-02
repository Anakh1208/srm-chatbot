import os
from supabase import create_client, Client
from dotenv import load_dotenv  # ADD THIS

load_dotenv()  # ADD THIS - loads .env file

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"URL: {SUPABASE_URL}")  # Should print your URL, not None
print(f"KEY: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY else "KEY: None")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)