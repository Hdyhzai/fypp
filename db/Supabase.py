from EnvReader import Settings
from supabase import Client, create_client

class SupabaseClient:
    
    def create_supabase_client():
    
        settings = Settings()
        
        url: str = settings.SUPABASE_URL
        key: str = settings.SUPABASE_KEY
        
        supabase: Client = create_client(url, key)
        return supabase