from supabase import create_client, Client
from app.config import settings

# Use Service Role Key if available, otherwise fall back to Anon Key
# Service Role Key bypasses RLS.
key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
supabase: Client = create_client(settings.SUPABASE_URL, key)