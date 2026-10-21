from supabase import create_client, Client
import streamlit as st

# Lấy URL và Key từ st.secrets hoặc giao diện Sidebar
url = st.secrets.get("SUPABASE_URL", "")
key = st.secrets.get("SUPABASE_KEY", "")

supabase: Client = create_client(url, key)

# Thao tác INSERT dữ liệu giao dịch vào Supabase:
record_data = {
    "ma_cua_hang": "HUB-001",
    "so_dien_thoai_kh": "0901234567",
    "phuong_an": "PA2",
    "tong_hang_cu": 134000000,
    "tong_hang_moi": 131000000,
    "tien_can_tru": 131000000,
    "tien_chi_sau": 3000000
}

response = supabase.table("giao_dich_thu_doi").insert(record_data).execute()