from supabase import create_client

SUPABASE_URL = "https://vyukbnvxlwpiwkqjytoe.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ5dWtibnZ4bHdwaXdrcWp5dG9lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODAyMTU3NDksImV4cCI6MjA5NTc5MTc0OX0.eOaV4UjTiNk23ISrT6r5i0xTsdHvNLVAedk7fK8CFVc"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    res = supabase.table("users").select("*").limit(1).execute()
    print("✅ Koneksi berhasil!")
    print(f"   Data: {res.data}")
except Exception as e:
    print(f"❌ Gagal: {e}")