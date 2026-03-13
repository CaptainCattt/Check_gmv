import time
import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
sys.path.append(os.path.abspath("."))

st.markdown("""
<h1 style="
    text-align:center;
    font-size:38px;
    font-weight:800;
    color:#111;
">
🔥 TODAY PERFORMANCE REPORT 🔥
</h1>
""", unsafe_allow_html=True)

st.markdown("""
        <style>
        body {
            background: linear-gradient(135deg, #6366F1, #8B5CF6);
            height: 100vh;
        }
        .login-card {
            background: white;
            padding: 40px 35px;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            max-width: 420px;
            margin: 80px auto;
            animation: fadeIn 0.5s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity:0; transform: translateY(15px);}
            to {opacity:1; transform: translateY(0);}
        }
        .title {
            font-size: 28px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
            color: #1F2937;
        }
        .subtitle {
            text-align: center;
            font-size: 15px;
            color: #6B7280;
            margin-bottom: 25px;
        }
        </style>
    """, unsafe_allow_html=True)


def set_latest_df(df, name="df_latest"):
    # Xóa tất cả DataFrame cũ trong session_state trừ Flow nếu muốn giữ
    keys_to_remove = [k for k in st.session_state.keys() if k.endswith("_df")]
    for k in keys_to_remove:
        del st.session_state[k]
    st.session_state[name] = df


def compute_kpi(df: pd.DataFrame):
    """
    Input: df = DataFrame AllOrder hoặc Income đã load
    Output: dict các KPI
    """
    # đảm bảo có các cột cần thiết
    df = df.copy()

    # 1️⃣ Số đơn đã đặt
    total_orders = df['Order ID'].nunique()

    # 2️⃣ Số đơn đã hủy
    canceled_orders = df[df['Order Substatus']
                         == 'Cancelled']['Order ID'].nunique()

    # 3️⃣ GMV ước tính
    if 'SKU Subtotal After Discount' in df.columns and 'SKU Platform Discount' in df.columns:
        # Chỉ lấy các đơn không bị hủy
        df_valid = df[df["Order Status"] != 'Cancelled']
        gmv = df_valid['SKU Subtotal After Discount'].sum(
        ) + df_valid['SKU Platform Discount'].sum()

    else:
        gmv = None

    # Chuẩn hóa SKU Category
    df["SKU Category"] = df["Seller SKU"].copy()

    # Danh sách các mẫu thay thế
    replacements = {
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH|COMBO-SC-MIX|SC_COMBO_MIX|SC_COMBO_MIX_LIVESTREAM|COMBO-SC_LIVESTREAM|SC_COMBO_MIX_01|MIX_X1\+X2|MIX_X1\+X2_LIVESTREAM)$": "COMBO-SC",
        r"^(SC_X1|X1)$": "SC-450g",
        r"^(SC_X2|X2)$": "SC-x2-450g",
        r"^(SC_COMBO_X1|COMBO-CAYVUA-X1|SC_COMBO_X1_LIVESTREAM|COMBO-SCX1|COMBO-SCX1_LIVESTREAM|COMBO_X1_LIVESTREAM|COMBO_X1)$": "COMBO-SCX1",
        r"^(SC_COMBO_X2|COMBO-SIEUCAY-X2|SC_COMBO_X2_LIVESTREAM|COMBO-SCX2|COMBO-SCX2_LIVESTREAM|COMBO_X2_LIVESTREAM|COMBO_X2)$": "COMBO-SCX2",
        r"^(BTHP-Cay-200gr|BTHP_Cay)$": "BTHP-CAY",
        r"^(BTHP-200gr|BTHP_KhongCay)$": "BTHP-0CAY",
        r"^(BTHP_COMBO_MIX|BTHP003_combo_mix|MIX_Cay\+KhongCay)$": "BTHP-COMBO",
        r"^(BTHP_COMBO_KhongCay|BTHP003_combo_kocay|COMBO_BTHP_KhongCay)$": "BTHP-COMBO-0CAY",
        r"^(BTHP_COMBO_Cay|BTHP003_combo_cay|COMBO_BTHP_Cay)$": "BTHP-COMBO-CAY",
        r"^(BTHP-COMBO\+SC_X1|BTHP_COMBO_MIX\+SC_X1|MIX_BTHP\+X1)$": "MIX_BTHP+X1",
        r"^(BTHP-COMBO\+SC_X2|BTHP_COMBO_MIX\+SC_X2|MIX_BTHP\+X2)$": "MIX_BTHP+X2",

        r"^(BTHP-2Cay-2KhongCay|MIX_2Cay\+2KhongCay)": "COMBO_4BTHP",
        r"^(BTHP-4Hu-KhongCay|4HU_BTHP_KhongCay|4Hu_BTHP_KhongCay)$": "4BTHP_0CAY",
        r"^(BTHP-4Hu-Cay|4HU_BTHP_Cay|4Hu_BTHP_Cay)$": "4BTHP_CAY",
        r"^(ST-SATETOM-X1|SC-SATE-TOM-X1|ST_STT|STT)$": "SATETOM_X1",
        r"^(SC-TIEUCHAY-X1|SC_TCLC|TCLC)$": "TIEUCHAY_X1",
        r"^(MIX_STT\+TCLC)$": "MIX_STT_TCLC",
        r"^(COMBO_STT)$": "COMBO_STT",
        r"^(COMBO_TCLC)$": "COMBO_TCLC",
        # Newadd
        r"^(MIX_X1\+STT)$": "MIX_X1_STT",
        r"^(MIX_X2\+STT)$": "MIX_X2_STT",
        r"^(MIX_X1\+TCLC)$": "MIX_X1_TCLC",
        r"^(MIX_X2\+TCLC)$": "MIX_X2_TCLC",

        # Ao caytedai
        r"^(ClothSet_X1_M)$": "ClothSet_X1_M",
        r"^(ClothSet_X1_L)$": "ClothSet_X1_L",
        r"^(ClothSet_X1_XL)$": "ClothSet_X1_XL",
        r"^(ClothSet_X2_M)$": "ClothSet_X2_M",
        r"^(ClothSet_X2_L)$": "ClothSet_X2_L",
        r"^(ClothSet_X2_XL)$": "ClothSet_X2_XL",

        # Ao Tshirt
        r"^(TShirt_White_M)$": "TShirt_White_M",
        r"^(TShirt_White_L)$": "TShirt_White_L",
        r"^(TShirt_White_XL)$": "TShirt_White_XL",
        r"^(TShirt_Black_M)$": "TShirt_Black_M",
        r"^(TShirt_Black_L)$": "TShirt_Black_L",
        r"^(TShirt_Black_XL)$": "TShirt_Black_XL",
    }

    for pattern, replacement in replacements.items():
        df["SKU Category"] = df["SKU Category"].str.replace(
            pattern, replacement, regex=True
        )

    # 4️⃣ % đơn theo SKU
    sku_counts = df.groupby('SKU Category')['Order ID'].nunique()
    sku_percent = (sku_counts / total_orders * 100).reset_index()
    sku_percent.columns = ['SKU', '% đơn']

    df["Province"] = df["Province"].replace(
        {
            "Ba Ria– Vung Tau": "Bà Rịa - Vũng Tàu",
            "Bà Rịa-Vũng Tàu": "Bà Rịa - Vũng Tàu",
            "Ba Ria - Vung Tau": "Bà Rịa - Vũng Tàu",
            "Bac Giang": "Bắc Giang",
            "Bac Lieu": "Bạc Liêu",
            "Bac Ninh": "Bắc Ninh",
            "Ben Tre": "Bến Tre",
            "Binh Dinh": "Bình Định",
            "Binh Duong": "Bình Dương",
            "Binh Duong Province": "Bình Dương",
            "Binh Phuoc": "Bình Phước",
            "Binh Thuan": "Bình Thuận",
            "Ca Mau": "Cà Mau",
            "Ca Mau Province": "Cà Mau",
            "Can Tho": "Cần Thơ",
            "Phố Cần Thơ": "Cần Thơ",
            "Da Nang": "Đà Nẵng",
            "Da Nang City": "Đà Nẵng",
            "Phố Đà Nẵng": "Đà Nẵng",
            "Dak Lak": "Đắk Lắk",
            "Đắc Lắk": "Đắk Lắk",
            "Ðắk Nông": "Đắk Nông",
            "Đắk Nông": "Đắk Nông",
            "Dak Nong": "Đắk Nông",
            "Dong Nai": "Đồng Nai",
            "Dong Nai Province": "Đồng Nai",
            "Dong Thap": "Đồng Tháp",
            "Dong Thap Province": "Đồng Tháp",
            "Ha Nam": "Hà Nam",
            "Ha Noi": "Hà Nội",
            "Ha Noi City": "Hà Nội",
            "Phố Hà Nội": "Hà Nội",
            "Hai Phong": "Hải Phòng",
            "Phố Hải Phòng": "Hải Phòng",
            "Ha Tinh": "Hà Tĩnh",
            "Hau Giang": "Hậu Giang",
            "Hô-Chi-Minh-Ville": "Hồ Chí Minh",
            "Ho Chi Minh": "Hồ Chí Minh",
            "Ho Chi Minh City": "Hồ Chí Minh",
            "Kota Ho Chi Minh": "Hồ Chí Minh",
            "Hoa Binh": "Hòa Bình",
            "Hoà Bình": "Hòa Bình",
            "Hung Yen": "Hưng Yên",
            "Khanh Hoa": "Khánh Hòa",
            "Khanh Hoa Province": "Khánh Hòa",
            "Khánh Hoà": "Khánh Hòa",
            "Kien Giang": "Kiên Giang",
            "Kiến Giang": "Kiên Giang",
            "Long An Province": "Long An",
            "Nam Dinh": "Nam Định",
            "Nghe An": "Nghệ An",
            "Ninh Binh": "Ninh Bình",
            "Ninh Thuan": "Ninh Thuận",
            "Quang Binh": "Quảng Bình",
            "Quang Tri": "Quảng Trị",
            "Quang Nam": "Quảng Nam",
            "Quang Ngai": "Quảng Ngãi",
            "Quang Ninh": "Quảng Ninh",
            "Quang Ninh Province": "Quảng Ninh",
            "Soc Trang": "Sóc Trăng",
            "Tay Ninh": "Tây Ninh",
            "Thai Binh": "Thái Bình",
            "Thanh Hoa": "Thanh Hóa",
            "Thanh Hoá": "Thanh Hóa",
            "Hai Duong": "Hải Dương",
            "Thừa Thiên Huế": "Thừa Thiên-Huế",
            "Thua Thien Hue": "Thừa Thiên-Huế",
            "Vinh Long": "Vĩnh Long",
            "Tra Vinh": "Trà Vinh",
            "Vinh Phuc": "Vĩnh Phúc",
            "Cao Bang": "Cao Bằng",
            "Lai Chau": "Lai Châu",
            "Ha Giang": "Hà Giang",
            "Lam Dong": "Lâm Đồng",
            "Lao Cai": "Lào Cai",
            "Phu Tho": "Phu Tho",
            "Phu Yen": "Phú Yên",
            "Thai Nguyen": "Thái Nguyên",
            "Son La": "Sơn La",
            "Tuyen Quang": "Tuyên Quang",
            "Yen Bai": "Yên Bái",
            "Dien Bien": "Điện Biên",
            "Tien Giang": "Tiền Giang",
        }
    )

    # 5️⃣ % đơn theo khu vực
    if 'Province' in df.columns:
        region_counts = df.groupby('Province')['Order ID'].nunique()
        region_percent = (region_counts / total_orders * 100).reset_index()
        region_percent.columns = ['Khu vực', '% đơn']
    else:
        region_percent = pd.DataFrame()

    return {
        "total_orders": total_orders,
        "canceled_orders": canceled_orders,
        "gmv": gmv,
        "sku_percent": sku_percent,
        "region_percent": region_percent
    }


def flow1(file_obj):
    df = pd.read_csv(file_obj)
    return df


uploaded_file = st.sidebar.file_uploader(
    "Upload CSV", type="csv", key="csv_upload_sidebar"
)

if uploaded_file:
    st.sidebar.success("CSV Uploaded!")
    if st.sidebar.button("Check GMV Now"):
        df = flow1(uploaded_file)
        set_latest_df(df, "df_latest")
        st.session_state["flow_name"] = "Flow 1 Result"


# Inject CSS làm đẹp
st.markdown(
    """
    <style>
        .kpi-card {
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            background-color: white;
            border: 1px solid #e6e6e6;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .kpi-value {
            font-size: 36px; 
            font-weight: 700; 
            margin-top: 5px;
        }
        .kpi-title {
            font-size: 18px;
            font-weight: 600;
            color: #444;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================
# UI CHÍNH
# ==============================
if "df_latest" in st.session_state:
    df = st.session_state["df_latest"]
    kpi = compute_kpi(df)

    st.markdown(
        "<h2 style='text-align:center; font-size:28px; font-weight:bold;'>🚀 Tổng quan đơn hàng hôm nay 🚀</h2>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title" style="font-size:24px; font-weight:bold;">📦 Tổng số đơn</div>
                <div class="kpi-value" style="color:#00796B">{kpi['total_orders']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title" style="font-size:24px; font-weight:bold;">❌ Đơn đã hủy</div>
                <div class="kpi-value" style="color:#C62828">{kpi['canceled_orders']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="kpi-card" style="margin-top:25px;">
            <div class="kpi-title" style="font-size:24px; font-weight:bold;">💰 GMV ước tính</div>
            <div class="kpi-value" style="color:#EF6C00">{kpi['gmv']:,.0f}₫</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------- % đơn theo SKU ----------
    st.markdown("<br><br>", unsafe_allow_html=True)
    fig_sku = px.pie(
        kpi["sku_percent"],
        names="SKU",
        values="% đơn",
        title="Tỷ lệ đơn theo SKU"
    )
    st.subheader("Tỷ lệ đơn theo SKU")
    st.plotly_chart(fig_sku)

    # st.dataframe(kpi["sku_percent"])

    # ---------- % đơn theo khu vực ----------
    if not kpi["region_percent"].empty:
        fig_region = px.pie(
            kpi["region_percent"],
            names="Khu vực",
            values="% đơn",
            title="Tỷ lệ đơn theo khu vực"
        )
    st.subheader("Tỷ lệ đơn theo khu vực")
    st.plotly_chart(fig_region)

    # st.dataframe(kpi["region_percent"])
