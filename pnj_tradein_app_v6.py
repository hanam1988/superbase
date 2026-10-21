import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Connection to Supabase helper
try:
    from supabase import create_client, Client
    HAS_SUPABASE_LIB = True
except ImportError:
    HAS_SUPABASE_LIB = False

# Page Configuration
st.set_page_config(
    page_title="PNJ - Tra Cứu & Hướng Dẫn Thu Đổi",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background-color: #003468;
        padding: 18px 25px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #F7D070 !important;
        margin: 0;
        font-size: 26px;
        font-weight: 700;
    }
    .main-header p {
        color: #E0E0E0;
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    .card-pa {
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: white;
        font-weight: bold;
    }
    .pa1-bg { background-color: #28a745; }
    .pa2-bg { background-color: #d39e00; }
    .pa3-bg { background-color: #dc3545; }
    .del-btn-container { margin-top: 28px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>💎 PNJ - HỆ THỐNG TRA CỨU & HƯỚNG DẪN THU ĐỔI CHUYỂN ĐỔI</h1>
    <p>Áp dụng theo QĐ 442-2026-TB-P.VHBL-TĐTGTTHML-PNJ & PL A2 (Hiệu lực từ 30/09/2026)</p>
</div>
""", unsafe_allow_html=True)

# Lấy URL và Key từ Streamlit Secrets nếu có
default_url = st.secrets.get("SUPABASE_URL", "") if hasattr(st, "secrets") else ""
default_key = st.secrets.get("SUPABASE_KEY", "") if hasattr(st, "secrets") else ""

# Supabase Settings Sidebar
st.sidebar.title("🔌 Cấu Hình CSDL Supabase")
sb_url = st.sidebar.text_input("Supabase URL:", value=default_url)
sb_key = st.sidebar.text_input("Supabase API Key:", value=default_key, type="password")
store_code = st.sidebar.text_input("Mã Cửa Hàng (HUB):", value="HUB-001")

supabase_client = None
if HAS_SUPABASE_LIB and sb_url.strip() and sb_key.strip():
    try:
        supabase_client = create_client(sb_url.strip(), sb_key.strip())
        st.sidebar.success("✅ Đã kết nối Supabase!")
    except Exception as e:
        st.sidebar.error(f"❌ Lỗi kết nối: {e}")

GROUPS_INFO = {
    "N1": {"name": "Vàng miếng, Nhẫn khoen, Vàng Phúc Lộc Tài, Kim Bảo", "allowed_to": ["N2", "N3", "N4", "N5", "N6", "N7"], "payment": "T+2", "schedule": "100% sau 2 ngày làm việc (T+2)"},
    "N3": {"name": "TS Công nghệ Ý, KGĐ, Dây chuyền, ECZ/CZ", "allowed_to": ["N2", "N3", "N5"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N4": {"name": "Vàng 21.9K - 24K (91.6% - 99.99%), Quà tặng sưu tầm", "allowed_to": ["N2", "N3", "N4", "N5"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N7": {"name": "Style by PNJ (KGĐ, CZ/ECZ, Dây chuyền)", "allowed_to": ["N6", "N7"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N8": {"name": "Danh mục Heart2Heart", "allowed_to": ["N8"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N9": {"name": "Danh mục Kind Heart", "allowed_to": ["N9"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N10": {"name": "Charm phong thủy đặc biệt, Bao lì xì phong thủy", "allowed_to": ["N10"], "payment": "T+7", "schedule": "100% sau 7 ngày làm việc (T+7)"},
    "N2": {"name": "TS Kim Cương, Đá màu, Ngọc trai, TS Vỏ", "allowed_to": ["N2", "N5"], "payment": "T+120", "schedule": "10% (T/T+1) | 20% (T+30) | 25% (T+60) | 25% (T+90) | 20% (T+120)"},
    "N5": {"name": "Kim cương rời, Đá màu rời, Ngọc trai rời, Cẩm thạch", "allowed_to": ["N2", "N5"], "payment": "T+120", "schedule": "10% (T/T+1) | 20% (T+30) | 25% (T+60) | 25% (T+90) | 20% (T+120)"},
    "N6": {"name": "Style by PNJ (TS Kim cương, Đá màu, Ngọc trai)", "allowed_to": ["N6"], "payment": "T+120", "schedule": "10% (T/T+1) | 20% (T+30) | 25% (T+60) | 25% (T+90) | 20% (T+120)"}
}

if 'old_items' not in st.session_state:
    st.session_state.old_items = [{'id': 1, 'group': None, 'val': 0}]
if 'new_items' not in st.session_state:
    st.session_state.new_items = [{'id': 1, 'group': None, 'val': 0}]
if 'next_old_id' not in st.session_state:
    st.session_state.next_old_id = 2
if 'next_new_id' not in st.session_state:
    st.session_state.next_new_id = 2

tab_calculator, tab_user_guide, tab_matrix, tab_faq, tab_database = st.tabs([
    "📋 1. TÍNH TOÁN CẤN TRỪ & PHƯƠNG ÁN",
    "📖 2. HƯỚNG DẪN QUY TRÌNH THU ĐỔI",
    "📊 3. MA TRẬN MAPPING & LỘ TRÌNH",
    "❓ 4. HỎI ĐÁP Q&A THƯỜNG GẶP",
    "🗄️ 5. QUẢN LÝ DỮ LIỆU SUPABASE"
])

with tab_calculator:
    st.subheader("📋 Tính Toán Cấn Trừ & Xác Định Phương Án Thanh Toán")
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        st.markdown("### 🛍️ 1. Hàng Cũ Thu Đổi / Mua Lại (Bảng kê)")
        old_items_processed = []
        total_old_val = 0
        to_delete_old = None

        for idx, item in enumerate(st.session_state.old_items):
            c_group, c_val, c_del = st.columns([5.5, 3.2, 1.3])
            def format_group_old(x):
                if x is None or x == "":
                    return "❓ -- Chọn nhóm hàng --"
                info = GROUPS_INFO[x]
                return f"[{info['payment']}] N{x[1:]} - {info['name'][:30]}..."

            options_list = [None] + list(GROUPS_INFO.keys())
            curr_index = options_list.index(item['group']) if item['group'] in options_list else 0

            with c_group:
                selected_g = st.selectbox(f"Món BK{idx+1}:", options=options_list, index=curr_index, format_func=format_group_old, key=f"old_g_select_{item['id']}")
                item['group'] = selected_g
            with c_val:
                val = st.number_input(f"Giá trị BK{idx+1} (VNĐ):", min_value=0, value=item['val'], step=1000000, key=f"old_val_input_{item['id']}")
                item['val'] = val
            with c_del:
                st.markdown("<div class='del-btn-container'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Xóa", key=f"del_old_{item['id']}", help="Xóa món này"):
                    to_delete_old = item['id']

            if item['group'] is not None and item['val'] > 0:
                old_items_processed.append({"id": f"BK{idx+1}", "group": item['group'], "name": GROUPS_INFO[item['group']]["name"], "value": item['val'], "payment": GROUPS_INFO[item['group']]["payment"], "schedule": GROUPS_INFO[item['group']]["schedule"]})
                total_old_val += item['val']

        if to_delete_old is not None:
            st.session_state.old_items = [x for x in st.session_state.old_items if x['id'] != to_delete_old]
            st.rerun()

        if st.button("➕ Thêm món cũ (BK)", key="add_old_btn"):
            st.session_state.old_items.append({'id': st.session_state.next_old_id, 'group': None, 'val': 0})
            st.session_state.next_old_id += 1
            st.rerun()

        st.metric("TỔNG GIÁ TRỊ HÀNG CỦ (BK):", f"{total_old_val:,.0f} VNĐ")

    with col_input2:
        st.markdown("### 🛒 2. Hàng Mới Khách Mua (Hóa đơn)")
        new_items_processed = []
        total_new_val = 0
        to_delete_new = None

        for idx, item in enumerate(st.session_state.new_items):
            c_group, c_val, c_del = st.columns([5.5, 3.2, 1.3])
            def format_group_new(x):
                if x is None or x == "":
                    return "❓ -- Chọn nhóm hàng --"
                info = GROUPS_INFO[x]
                return f"[{info['payment']}] N{x[1:]} - {info['name'][:30]}..."

            options_list_new = [None] + list(GROUPS_INFO.keys())
            curr_index_new = options_list_new.index(item['group']) if item['group'] in options_list_new else 0

            with c_group:
                selected_g_new = st.selectbox(f"Món HĐ{idx+1}:", options=options_list_new, index=curr_index_new, format_func=format_group_new, key=f"new_g_select_{item['id']}")
                item['group'] = selected_g_new
            with c_val:
                val = st.number_input(f"Giá trị HĐ{idx+1} (VNĐ):", min_value=0, value=item['val'], step=1000000, key=f"new_val_input_{item['id']}")
                item['val'] = val
            with c_del:
                st.markdown("<div class='del-btn-container'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Xóa", key=f"del_new_{item['id']}", help="Xóa món này"):
                    to_delete_new = item['id']

            if item['group'] is not None and item['val'] > 0:
                new_items_processed.append({"id": f"HĐ{idx+1}", "group": item['group'], "name": GROUPS_INFO[item['group']]["name"], "value": item['val'], "rem_val": item['val']})
                total_new_val += item['val']

        if to_delete_new is not None:
            st.session_state.new_items = [x for x in st.session_state.new_items if x['id'] != to_delete_new]
            st.rerun()

        if st.button("➕ Thêm món mới (HĐ)", key="add_new_btn"):
            st.session_state.new_items.append({'id': st.session_state.next_new_id, 'group': None, 'val': 0})
            st.session_state.next_new_id += 1
            st.rerun()

        st.metric("TỔNG GIÁ TRỊ HÀNG MỚI (HĐ):", f"{total_new_val:,.0f} VNĐ")

    st.markdown("---")
    st.markdown("### ⚙️ Điều Kiện Vận Hành & Tuân Thủ Quầy")
    col_cond1, col_cond2, col_cond3 = st.columns(3)
    with col_cond1:
        is_hub = st.checkbox("Cửa hàng là Điểm Trung Tâm (HUB)?", value=True)
    with col_cond2:
        same_customer = st.checkbox("Hóa đơn cũ & mới CÙNG MÃ KHÁCH HÀNG?", value=True)
    with col_cond3:
        customer_phone = st.text_input("Số điện thoại / Mã KH:", value="0901234567")

    can_tru_list = []
    du_item_list = []
    total_can_tru = 0
    total_chi_sau = 0
    new_pool = [{**item} for item in new_items_processed]
    
    for old in old_items_processed:
        old_val_rem = old["value"]
        for new in new_pool:
            if old_val_rem <= 0: break
            if new["rem_val"] <= 0: continue
            allowed_groups = GROUPS_INFO[old["group"]]["allowed_to"]
            if new["group"] in allowed_groups:
                matched_amount = min(old_val_rem, new["rem_val"])
                can_tru_list.append({"old_id": old["id"], "old_group": old["group"], "new_id": new["id"], "new_group": new["group"], "amount": matched_amount})
                old_val_rem -= matched_amount
                new["rem_val"] -= matched_amount
                total_can_tru += matched_amount
        if old_val_rem > 0:
            du_item_list.append({"id": old["id"], "group": old["group"], "amount": old_val_rem, "payment": old["payment"], "schedule": old["schedule"]})
            total_chi_sau += old_val_rem

    st.markdown("---")
    st.markdown("### 🎯 KẾT QUẢ PHÂN LOẠI PHƯƠNG ÁN THANH TOÁN")
    
    has_unselected_old = any(x['group'] is None for x in st.session_state.old_items if x['val'] > 0)
    has_unselected_new = any(x['group'] is None for x in st.session_state.new_items if x['val'] > 0)
    if has_unselected_old or has_unselected_new:
        st.warning("⚠️ Vui lòng chọn Nhóm Hàng cho tất cả các món để hệ thống tính toán chính xác!")

    pa_code = "N/A"
    if total_old_val == 0 and total_new_val == 0:
        st.info("👋 Hãy chọn Nhóm hàng và nhập giá trị món hàng ở trên để bắt đầu tính toán.")
    elif total_new_val == 0:
        pa_code = "PA3"
        pa_title = "🔴 Phương Án 3: MUA LẠI HOÀN TOÀN"
        pa_bg = "pa3-bg"
        pa_desc = "Khách hàng bán lại sản phẩm và không phát sinh hóa đơn mua mới."
    elif total_chi_sau == 0 and total_can_tru == total_old_val:
        pa_code = "PA1"
        pa_title = "🟢 Phương Án 1: CHUYỂN ĐỔI HOÀN TOÀN"
        pa_bg = "pa1-bg"
        pa_desc = "Toàn bộ giá trị sản phẩm cũ được cấn trừ hết vào hóa đơn mới. Khách hàng đóng thêm tiền chênh lệch (nếu có)."
    else:
        pa_code = "PA2"
        pa_title = "🟡 Phương Án 2: CHUYỂN ĐỔI MỘT PHẦN (Chỉ thực hiện tại Cửa Hàng HUB)"
        pa_bg = "pa2-bg"
        pa_desc = f"Cấn trừ {total_can_tru:,.0f} VNĐ vào hóa đơn mới. Công ty sẽ chi trả lại phần tiền thừa {total_chi_sau:,.0f} VNĐ cho khách theo lộ trình thanh toán."

    if total_old_val > 0 or total_new_val > 0:
        st.markdown(f"""
        <div class="card-pa {pa_bg}">
            <h3 style="margin:0; color:white;">{pa_title}</h3>
            <p style="margin:5px 0 0 0; font-weight:normal;">{pa_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.success(f"**Tổng tiền cấn trừ ngay:** {total_can_tru:,.0f} VNĐ")
            if can_tru_list:
                for ct in can_tru_list:
                    st.write(f"• **{ct['old_id']}** (N{ct['old_group'][1:]}) ➔ Cấn trừ **{ct['amount']:,.0f} VNĐ** sang **{ct['new_id']}** (N{ct['new_group'][1:]})")
        with res_col2:
            st.warning(f"**Công ty chi trả sau:** {total_chi_sau:,.0f} VNĐ")
            if du_item_list:
                for du in du_item_list:
                    st.write(f"• **{du['id']}** (N{du['group'][1:]}): Dư **{du['amount']:,.0f} VNĐ** ➔ Lộ trình **{du['payment']}** ({du['schedule']})")

        st.markdown("---")
        if st.button("💾 LƯU GIAO DỊCH VÀO SUPABASE", type="primary"):
            if supabase_client:
                try:
                    # Chú ý: Truyền trực tiếp Python list/dict cho cột JSONB
                    record_data = {
                        "ma_cua_hang": store_code,
                        "so_dien_thoai_kh": customer_phone,
                        "phuong_an": pa_code,
                        "tong_hang_cu": float(total_old_val),
                        "tong_hang_moi": float(total_new_val),
                        "tien_can_tru": float(total_can_tru),
                        "tien_chi_sau": float(total_chi_sau),
                        "chi_tiet_cu": old_items_processed,
                        "chi_tiet_moi": new_items_processed
                    }
                    res = supabase_client.table("giao_dich_thu_doi").insert(record_data).execute()
                    st.success("🎉 Đã lưu thành công giao dịch vào CSDL Supabase!")
                except Exception as err:
                    st.error(f"❌ Lỗi từ Supabase: {err}")
                    st.info("💡 MẸO: Nếu gặp lỗi RLS (Row Level Security), hãy vào Supabase SQL Editor và chạy lệnh: 'ALTER TABLE giao_dich_thu_doi DISABLE ROW LEVEL SECURITY;'")
            else:
                st.error("⚠️ Chưa kết nối Supabase! Vui lòng kiểm tra Supabase URL và Key ở thanh SideBar bên trái.")

with tab_user_guide:
    st.subheader("📖 Hướng Dẫn Chi Tiết Quy Trình Thu Đổi & Mua Lại Sản Phẩm PNJ")
    st.write("Tài liệu hướng dẫn trực quan dành cho Khách hàng và Nhân viên tư vấn bán hàng toàn hệ thống PNJ.")

with tab_matrix:
    st.subheader("📊 Bảng Ma Trận Mapping Nhóm Hàng & Lộ Trình Thanh Toán PNJ")
    matrix_data = [{"Mã Nhóm": k, "Tên Dòng Sản Phẩm": v["name"], "Nhóm Cho Phép Đổi Sang": ", ".join(v["allowed_to"]), "Thời Gian Thanh Toán": v["payment"], "Chi Tiết Lộ Trình Chi Trả": v["schedule"]} for k, v in GROUPS_INFO.items()]
    st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

with tab_faq:
    st.subheader("❓ Các Câu Hỏi Thường Gặp Của Nhân Viên & Khách Hàng (Q&A)")
    with st.expander("Q1: Khách hàng muốn bán lại món cũ nhưng cửa hàng không phải HUB thì làm thế nào?"):
        st.write("👉 **Trả lời:** Cửa hàng thường không có chức năng tiếp nhận giao dịch Mua lại (PA3) hoặc Chuyển đổi một phần (PA2). Nhân viên hướng dẫn khách hàng đến Cửa hàng HUB gần nhất trong khung giờ từ 15h00 đến 17h00 để thực hiện.")

with tab_database:
    st.subheader("🗄️ Quản Lý Dữ Liệu Giao Dịch Thu Đổi (Supabase)")
    if supabase_client:
        if st.button("🔄 Tải Dữ Liệu Từ Supabase"):
            try:
                response = supabase_client.table("giao_dich_thu_doi").select("*").order("created_at", desc=True).execute()
                if response.data:
                    st.dataframe(pd.DataFrame(response.data), use_container_width=True)
                else:
                    st.info("Chưa có giao dịch nào được lưu.")
            except Exception as e:
                st.error(f"❌ Lỗi truy vấn: {e}")
    else:
        st.warning("⚠️ Chưa kết nối Supabase. Vui lòng nhập Supabase URL và API Key ở góc trái ứng dụng!")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6c757d; font-size: 13px;'>© 2026 Phu Nhuan Jewelry Joint Stock Company (PNJ).</div>", unsafe_allow_html=True)
