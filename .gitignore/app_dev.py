import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =========================
# CUSTOM KPI CARD
# =========================
def kpi_card(title, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
        )
    st.markdown("""
    <style>
    .kpi-card {
        background: #111827;
        border: 1px solid #2e2e2e;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.35);
    }
    .kpi-title {
        font-size: 13px;
        color: #9ca3af;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 700;
        color: #f9fafb;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# RUPIAH PARSER (ROBUST)
# =========================
def parse_rupiah(series: pd.Series) -> pd.Series:
    s = (
        series.astype(str)
        .str.replace("Rp", "", regex=False)
        .str.replace("\ufeff", "", regex=False)
        .str.replace("\xa0", "", regex=False)
        .str.strip()
    )

    s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan})

    mask_multi_comma = s.str.match(r"^\d{1,3}(,\d{3})+$", na=False)
    mask_id_dot = s.str.match(r"^\d{1,3}(\.\d{3})+(,\d{2})?$", na=False)
    mask_two_dec_comma = s.str.match(r"^\d{1,3},\d{2}$", na=False)

    out = pd.Series(index=s.index, dtype="float64")

    out[mask_multi_comma] = pd.to_numeric(
        s[mask_multi_comma].str.replace(",", "", regex=False),
        errors="coerce"
    )

    out[mask_id_dot] = pd.to_numeric(
        s[mask_id_dot]
        .str.replace(".", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce"
    )

    # 38,00 -> 38.000 (kali 1000)
    out[mask_two_dec_comma] = (
        pd.to_numeric(s[mask_two_dec_comma].str.replace(",", ".", regex=False), errors="coerce") * 1000
    )

    rest = ~(mask_multi_comma | mask_id_dot | mask_two_dec_comma)
    out[rest] = pd.to_numeric(
        s[rest].str.replace(r"[^0-9]", "", regex=True),
        errors="coerce"
    )

    return out.fillna(0)

def format_rp(x) -> str:
    try:
        return f"Rp {int(x):,}".replace(",", ".")
    except Exception:
        return "Rp 0"

def clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.replace("\xa0", "", regex=False)
        .str.strip()
        .str.upper()
    )
    return df

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Dashboard Purchasing & Inventory", layout="wide")
# INIT SESSION
if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False
st.title("📊 Dashboard Purchasing & Inventory")
st.caption("Monitoring Petty Cash, Purchase Request, dan Cutting Stock")
st.markdown("""
<style>
.kpi-card-red {
    background: linear-gradient(135deg, #2a0f14, #3a141b);
    padding: 25px;
    border-radius: 18px;
    text-align: center;
}
.kpi-card-green {
    background: linear-gradient(135deg, #0f2a18, #144022);
    padding: 25px;
    border-radius: 18px;
    text-align: center;
}
.kpi-title {
    font-size: 14px;
    color: #9fb3c8;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 28px;
    font-weight: bold;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR - ENTRY ACCESS
# =========================
with st.sidebar:
    st.subheader("🔐 Staff Access")

    pin_input = st.text_input(
        "Masukkan PIN",
        type="password",
        key="pin_input"
    )

    if st.button("Akses Staff"):
        if pin_input == "1234":   # PIN_BENAR = "1234" misalnya
            st.session_state.auth_ok = True
            st.success("Akses Staff aktif")
        else:
            st.session_state.auth_ok = False
            st.error("PIN salah")

    # info status (opsional tapi rapi)
    if st.session_state.get("auth_ok"):
        st.caption("🟢 Mode Staff Aktif")
    else:
        st.caption("🔒 Mode View Only")

# =========================
# REFRESH BUTTON
# =========================
if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=60)
def load_data():
    url_petty = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQiqe-WvAEHeE8Uly6uuJ8OYDx3nzNXeVL7dpfkEt5QWkvK3rBqhTC4XdVNicBYBhqINsd9NL1r0IdZ/pub?gid=597462353&single=true&output=csv"
    url_pr    = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQiqe-WvAEHeE8Uly6uuJ8OYDx3nzNXeVL7dpfkEt5QWkvK3rBqhTC4XdVNicBYBhqINsd9NL1r0IdZ/pub?gid=1286954685&single=true&output=csv"
    url_stock = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQiqe-WvAEHeE8Uly6uuJ8OYDx3nzNXeVL7dpfkEt5QWkvK3rBqhTC4XdVNicBYBhqINsd9NL1r0IdZ/pub?gid=180967511&single=true&output=csv"
    url_tracking = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQiqe-WvAEHeE8Uly6uuJ8OYDx3nzNXeVL7dpfkEt5QWkvK3rBqhTC4XdVNicBYBhqINsd9NL1r0IdZ/pub?gid=456535989&single=true&output=csv"

    petty_cash = pd.read_csv(url_petty, sep=",", encoding="utf-8", engine="python")
    purchase_request = pd.read_csv(url_pr, sep=",", encoding="utf-8", engine="python")
    cutting_stock = pd.read_csv(url_stock, sep=",", encoding="utf-8", engine="python")
    tracking_data = pd.read_csv(url_tracking, sep=",", encoding="utf-8", engine="python")

    petty_cash = clean_cols(petty_cash)
    purchase_request = clean_cols(purchase_request)
    cutting_stock = clean_cols(cutting_stock)
    tracking_data = clean_cols(tracking_data)

    return petty_cash, purchase_request, cutting_stock, tracking_data

petty_cash, pr_data, stock_data, tracking_data = load_data()


# =========================
# NAVIGATION: TABS
# =========================
tab_labels = ["💰 Petty Cash", "🛒 Purchase Request", "📦 Cutting Stock", "🔎 Tracking Harga & Supplier", "📊 Analysis"]
st.caption(f"Total opsi menu: {len(tab_labels)}")
tabs = st.tabs(tab_labels)

# =========================
# HELPER FUNCTIONS
# =========================

def pill_style(val, col):
    v = str(val).upper().strip()

    base = (
        "border-radius: 12px;"
        "padding: 4px 10px;"
        "text-align: center;"
        "display: inline-block;"
        "font-weight: 600;"
    )

    # TIPE
    if col == "TIPE":
        if v == "IN":
            return base + "background-color:#C8F7C5; color:#000;"
        if v == "OUT":
            return base + "background-color:#F8C6C6; color:#000;"

    # KETERANGAN
    if col == "KETERANGAN":
        if "PEMBELIAN" in v:
            return base + "background-color:#DFF5E1; color:#1B5E20;"
        if "PEMBAYARAN" in v:
            return base + "background-color:#E8F5E9; color:#1B5E20;"
        if "MASUK" in v:
            return base + "background-color:#FFF3CD; color:#856404;"
        if "DANA" in v:
            return base + "background-color:#D6EAF8; color:#154360;"

    # PV
    if col == "KET.PV":
        if "BELUM" in v:
            return base + "background-color:#F8C6C6; color:#000;"
        if "SUDAH" in v:
            return base + "background-color:#C8F7C5; color:#000;"

    return ""

# ==========================================================
# TAB 1: PETTY CASH (FOCUS CASHFLOW, TANPA PV)
# ==========================================================
with tabs[0]:
    st.header("💰 Petty Cash Monitoring")

    required_cols = ["DATE", "KETERANGAN", "TIPE", "JUMLAH"]
    missing = [c for c in required_cols if c not in petty_cash.columns]
    if missing:
        st.error(f"Kolom wajib hilang: {missing}")
        st.write("Kolom tersedia:", petty_cash.columns.tolist())
        st.stop()

    petty_cash["DATE"] = pd.to_datetime(petty_cash["DATE"], dayfirst=True, errors="coerce")
    petty_cash["TIPE"] = petty_cash["TIPE"].astype(str).str.upper().str.strip()
    petty_cash["JUMLAH_NUM"] = parse_rupiah(petty_cash["JUMLAH"]).astype("int64")

    petty_cash["JUMLAH_BERSIH"] = np.where(
        petty_cash["TIPE"].eq("IN"),
        petty_cash["JUMLAH_NUM"],
        np.where(petty_cash["TIPE"].eq("OUT"), -petty_cash["JUMLAH_NUM"], 0)
    ).astype("int64")

    petty_cash = petty_cash.reset_index(drop=True)
    petty_cash["ROW_ID"] = petty_cash.index

    petty_cash["SALDO_NUM"] = petty_cash["JUMLAH_BERSIH"].cumsum().astype("int64")

        # WARNING jika saldo minus
    if len(petty_cash) > 0 and petty_cash["SALDO_NUM"].iloc[-1] < 0:
        st.error("⚠️ Saldo petty cash minus! Periksa transaksi OUT berlebih")

    # =========================
    # FILTER (TANPA PV)
    # =========================
    colf1, colf2, colf3 = st.columns([2, 1, 2])

    min_d = petty_cash["DATE"].min()
    max_d = petty_cash["DATE"].max()

    date_range = colf1.date_input(
        "Tanggal",
        value=(min_d.date() if pd.notna(min_d) else None, max_d.date() if pd.notna(max_d) else None),
        min_value=min_d.date() if pd.notna(min_d) else None,
        max_value=max_d.date() if pd.notna(max_d) else None
    )

    tipe_filter = colf2.selectbox("Tipe", ["ALL", "IN", "OUT"])
    search_kw = colf3.text_input("Search (keterangan/deskripsi/project)", value="")

    df = petty_cash.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2 and date_range[0] and date_range[1]:
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
        df = df[(df["DATE"] >= start) & (df["DATE"] <= end)]

    if tipe_filter != "ALL":
        df = df[df["TIPE"] == tipe_filter]

    if search_kw.strip():
        kw = search_kw.strip().upper()
        cols_search = [c for c in ["KETERANGAN", "DESKRIPSI", "PROJECT/PJ"] if c in df.columns]
        if cols_search:
            hay = df[cols_search].fillna("").astype(str).agg(" ".join, axis=1).str.upper()
            df = df[hay.str.contains(kw, na=False)]

    # =========================
    # SORTING SESUAI SPREADSHEET (ASCENDING)
    # =========================
    df = df.sort_values("ROW_ID") #TAMPILAN SESUAI URUTAN DI SPREADSHEET
    #KALAU MAU DARI ATAS KE BAWAH ATAU SAMA DENGAN KEBALIKANNYA PAKAI CODE INI df = df.sort_values("ROW_ID", ascending=False).reset_index(drop=True)

    # =========================
    # KPI (FOKUS CASHFLOW)
    # =========================
    saldo_akhir_all = int(petty_cash["SALDO_NUM"].iloc[-1]) if len(petty_cash) else 0
    total_in = int(df[df["TIPE"] == "IN"]["JUMLAH_NUM"].sum())
    total_out = int(df[df["TIPE"] == "OUT"]["JUMLAH_NUM"].sum())
    net_range = int(df["JUMLAH_BERSIH"].sum())
    total_transaksi = len(df)

    k1, k2, k3, k4, k5 = st.columns([1.2, 1, 1, 1, 1])

    with k1:
        kpi_card("Saldo Akhir (seluruh data)", format_rp(saldo_akhir_all))

    with k2:
        kpi_card("Total IN (filter)", format_rp(total_in))

    with k3:
        kpi_card("Total OUT (filter)", format_rp(total_out))

    with k4:
        kpi_card("Net (filter)", format_rp(net_range))

    with k5:
        kpi_card("Total Transaksi", total_transaksi)

    # =========================
    # TABEL UTAMA (RUPIAH)
    # =========================
    st.subheader("Detail Transaksi")

    show_cols = [c for c in ["DATE","KETERANGAN","TIPE","DESKRIPSI","PROJECT/PJ"] if c in df.columns]

    if "KET.PV" in df.columns:
        df["KET.PV"] = df["KET.PV"].fillna("").astype(str).str.upper().str.strip()
        show_cols.insert(5, "KET.PV")

    view = df[show_cols + ["JUMLAH_NUM", "SALDO_NUM"]].copy()

    # =========================
    # FORMAT RUPIAH
    # =========================
    view["JUMLAH"] = view["JUMLAH_NUM"].apply(format_rp)
    view["SALDO"] = view["SALDO_NUM"].apply(format_rp)

    # Drop kolom numeric biar bersih
    view = view.drop(columns=["JUMLAH_NUM", "SALDO_NUM"])

    # Format DATE agar hanya tampil tanggal saja
    if "DATE" in view.columns:
        view["DATE"] = pd.to_datetime(view["DATE"]).dt.strftime("%d/%m/%Y")

    # =========================
    # APPLY PILL STYLE (NEW)
    # =========================
    styler = view.style

    if "TIPE" in view.columns:
        styler = styler.map(lambda v: pill_style(v, "TIPE"), subset=["TIPE"])

    if "KETERANGAN" in view.columns:
        styler = styler.applymap(lambda v: pill_style(v, "KETERANGAN"), subset=["KETERANGAN"])

    if "KET.PV" in view.columns:
        styler = styler.applymap(lambda v: pill_style(v, "KET.PV"), subset=["KET.PV"])

    # 🔥 TAMBAHAN WIDTH & ALIGN TIPE
    if "TIPE" in view.columns:
        styler = styler.set_properties(subset=["TIPE"], **{
            "width": "80px",
            "text-align": "center"
        })

    # =========================
    # DISPLAY TABLE
    # =========================
    st.dataframe(
        styler,
        height=300,
        use_container_width=True,
        hide_index=True
    )
    # ==========================================================
    # TAB 2: PURCHASE REQUEST
    # ==========================================================
    with tabs[1]:
        st.header("🛒 Purchase Request")

        df_pr = pr_data.copy()

        # =========================
        # PARSE SUBTOTAL
        # =========================
        if "SUBTOTAL" in df_pr.columns:
            df_pr["SUBTOTAL_NUM"] = parse_rupiah(df_pr["SUBTOTAL"]).astype("int64")
        else:
            df_pr["SUBTOTAL_NUM"] = 0

        # =========================
        # FILTER SECTION
        # =========================
        colf1, colf2 = st.columns(2)

        # Filter Project
        if "PROJECT" in df_pr.columns:
            project_list = ["ALL"] + sorted(df_pr["PROJECT"].dropna().unique().tolist())
            selected_project = colf1.selectbox("Filter Project", project_list)
            if selected_project != "ALL":
                df_pr = df_pr[df_pr["PROJECT"] == selected_project]

        # Search keyword
        search_kw = colf2.text_input("Search Item / Deskripsi", value="")
        if search_kw.strip():
            kw = search_kw.strip().upper()
            df_pr = df_pr[
                df_pr.astype(str)
                .agg(" ".join, axis=1)
                .str.upper()
                .str.contains(kw, na=False)
            ]

        # =========================
        # KPI SECTION
        # =========================
        total_estimation = int(df_pr["SUBTOTAL_NUM"].sum())
        total_item = len(df_pr)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Estimasi Pembelian</div>
                <div class="kpi-value">{format_rp(total_estimation)}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Item Request</div>
                <div class="kpi-value">{total_item}</div>
            </div>
            """, unsafe_allow_html=True)

        # =========================
        # DISTRIBUSI & RINGKASAN ESTIMASI PER PROJECT
        # =========================
        if "PROJECT" in df_pr.columns and not df_pr.empty:

            st.subheader("📊 Estimasi Purchase per Project")

            summary_project = (
                df_pr.groupby("PROJECT")["SUBTOTAL_NUM"]
                .agg(["sum", "count"])
                .reset_index()
                .sort_values("sum", ascending=False)
            )

            summary_project = summary_project.rename(
                columns={
                    "sum": "TOTAL_ESTIMASI",
                    "count": "JUMLAH_ITEM"
                }
            )

            import plotly.express as px

            fig = px.pie(
                summary_project,
                names="PROJECT",
                values="TOTAL_ESTIMASI",
                hole=0.4
            )

            # 🔥 GANTI TEXT JADI NOMINAL RUPIAH
            fig.update_traces(
                text=summary_project["TOTAL_ESTIMASI"].apply(format_rp),
                textinfo="label+text",
                hovertemplate="<b>%{label}</b><br>Total: %{value:,.0f}<br>Item: %{customdata[0]}<extra></extra>",
                customdata=summary_project[["JUMLAH_ITEM"]].values
            )

            fig.update_layout(
                margin=dict(t=30, b=0, l=0, r=0)
            )

            st.plotly_chart(fig, use_container_width=True)

            # =========================
            # TABLE SUMMARY DI BAWAHNYA
            # =========================
            summary_project["TOTAL ESTIMASI"] = summary_project["TOTAL_ESTIMASI"].apply(format_rp)

            st.dataframe(
                summary_project[["PROJECT", "TOTAL ESTIMASI", "JUMLAH_ITEM"]],
                use_container_width=True
            )

        # =========================
        # TABLE VIEW
        # =========================
        pr_view = df_pr.copy()
        pr_view["SUBTOTAL"] = pr_view["SUBTOTAL_NUM"].apply(format_rp)
        pr_view = pr_view.drop(columns=["SUBTOTAL_NUM"])

        st.subheader("📋 Daftar Purchase Request")
        st.dataframe(pr_view, width="stretch")

# ==========================================================
# TAB 3: CUTTING STOCK
# ==========================================================
with tabs[2]:
    st.header("📦 Cutting Stock Monitoring")

    # Pakai copy supaya tidak merusak data asli
    df_stock = stock_data.copy()

    # Pastikan numeric
    for col in ["QTY", "SAFETY STOCK"]:
        if col in df_stock.columns:
            df_stock[col] = pd.to_numeric(df_stock[col], errors="coerce").fillna(0)

    if "QTY" in df_stock.columns and "SAFETY STOCK" in df_stock.columns:

        # Buat status sistem
        df_stock["SYSTEM STATUS"] = df_stock.apply(
            lambda r: "RE-STOCK" if r["QTY"] <= r["SAFETY STOCK"] else "AMAN",
            axis=1
        )

        restock_count = int((df_stock["SYSTEM STATUS"] == "RE-STOCK").sum())
        aman_count = int((df_stock["SYSTEM STATUS"] == "AMAN").sum())

        # =========================
        # KPI CARD STYLE
        # =========================
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Item Perlu Re-Stock</div>
                <div class="kpi-value">{restock_count}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Item Aman</div>
                <div class="kpi-value">{aman_count}</div>
            </div>
            """, unsafe_allow_html=True)

        # =========================
        # PRIORITAS RESTOCK
        # =========================
        st.subheader("Prioritas Re-Stock")

        df_restock = df_stock[df_stock["SYSTEM STATUS"] == "RE-STOCK"]

        if not df_restock.empty:
            st.dataframe(
                df_restock.sort_values("QTY"),
                use_container_width=True
            )
        else:
            st.info("Semua stok dalam kondisi aman.")

    # =========================
    # DATA LENGKAP
    # =========================
    st.subheader("Data Stok Lengkap")
    st.dataframe(df_stock, use_container_width=True)

# ==========================================================
# TAB 4: TRACKING PRICE
# ==========================================================
with tabs[3]:
    st.header("🔎 Tracking Harga & Supplier")

    if not st.session_state.get("auth_ok", False):
        st.warning("🔒 Akses dibatasi. Masukkan PIN di sidebar untuk membuka menu tracking & Analysis.")
        st.stop()

    df_track = tracking_data.copy()

    required_cols = ["DESCRIPTION", "PROJECT", "UNIT", "HARGA", "SUPPLIER"]
    missing = [c for c in required_cols if c not in df_track.columns]

    if missing:
        st.error(f"Kolom wajib hilang: {missing}")
        st.stop()

    # pastikan harga numerik
    df_track["HARGA_NUM"] = parse_rupiah(df_track["HARGA"]).astype("int64")

    search_item = st.text_input("Cari Nama Barang")

    if search_item.strip():
        df_filtered = df_track[
            df_track["DESCRIPTION"]
            .astype(str)
            .str.upper()
            .str.contains(search_item.upper(), na=False)
        ]

        if df_filtered.empty:
            st.warning("Data tidak ditemukan")
        else:
            st.subheader("Hasil Pencarian")
            view_track = df_filtered.copy()
            view_track["HARGA"] = view_track["HARGA_NUM"].apply(format_rp)

            st.dataframe(
                view_track[["DESCRIPTION","UNIT","PROJECT","SUPPLIER","HARGA"]],
                use_container_width=True
            )

            # SUMMARY ANALYTICS
            min_price = df_filtered["HARGA_NUM"].min()
            max_price = df_filtered["HARGA_NUM"].max()
            avg_price = int(df_filtered["HARGA_NUM"].mean())

            col1, col2, col3 = st.columns(3)
            col1.metric("Harga Terendah", format_rp(min_price))
            col2.metric("Harga Tertinggi", format_rp(max_price))
            col3.metric("Rata-rata Harga", format_rp(avg_price))

            # Supplier paling sering
            top_supplier = df_filtered["SUPPLIER"].value_counts().idxmax()
            st.info(f"Supplier paling sering digunakan: {top_supplier}")
            st.caption("🏷️ Harga berdasarkan histori purchase request dan dapat berubah sewaktu-waktu sesuai kebijakan supplier.")     

# ==========================================================
# TAB 5: ANALYSIS
# ==========================================================
    with tabs[4]:
        st.header("📊 Cashflow Analysis")

        df_cash = petty_cash.copy()

        if df_cash.empty:
            st.error("Data Cashflow kosong.")
            st.stop()

        # =========================
        # Validasi Kolom
        # =========================
        required_cols = ["JUMLAH", "TIPE", "DATE"]
        missing = [c for c in required_cols if c not in df_cash.columns]

        if missing:
            st.error(f"Kolom tidak ditemukan: {missing}")
            st.stop()

        # =========================
        # Cleaning Data (ANTI BEDA ANGKA)
        # =========================
        df_cash["TIPE"] = df_cash["TIPE"].astype(str).str.upper().str.strip()
        df_cash["JUMLAH_NUM"] = parse_rupiah(df_cash["JUMLAH"]).astype("int64")
        df_cash["DATE"] = pd.to_datetime(df_cash["DATE"], errors="coerce")

        # =========================
        # KPI
        # =========================
        total_in = df_cash.loc[df_cash["TIPE"] == "IN", "JUMLAH_NUM"].sum()
        total_out = df_cash.loc[df_cash["TIPE"] == "OUT", "JUMLAH_NUM"].sum()
        net_total = total_in - total_out

        ratio = (total_in / total_out) if total_out > 0 else 0
        ratio_percent = ratio * 100

        # Persentase pengeluaran terhadap pemasukan
        out_percent = (total_out / total_in * 100) if total_in > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card("💰 Total IN", format_rp(total_in))

        with col2:
            kpi_card("💸 Total OUT", format_rp(total_out))
            delta=f"{out_percent:.1f}% dari IN"

        with col3:
            kpi_card("📊 Net Cashflow", format_rp(net_total))
            delta=format_rp(net_total),
            delta_color="normal" if net_total >= 0 else "inverse"

        with col4:
            kpi_card("⚖️ Rasio IN / OUT", f"{ratio:.2f}x")
            delta=f"{ratio_percent:.0f}%"
            
        # Status kesehatan
        if net_total > 0:
            st.success("🟢 Cashflow Sehat (Surplus)")
        elif net_total < 0:
            st.error("🔴 Cashflow Defisit")
        else:
            st.warning("🟡 Break Even")

        # =========================
        # Project Paling Boros
        # =========================
        if "PROJECT/PJ" in df_cash.columns:
            st.subheader("📊 Kontributor Pengeluaran Terbesar")

            df_out = df_cash[df_cash["TIPE"] == "OUT"]

            project_spending = (
                df_out.groupby("PROJECT/PJ")["JUMLAH_NUM"]
                .sum()
                .reset_index()
                .sort_values("JUMLAH_NUM", ascending=False)
            )

            project_spending["TOTAL"] = project_spending["JUMLAH_NUM"].apply(format_rp)

            st.dataframe(
                project_spending[["PROJECT/PJ", "TOTAL"]],
                use_container_width=True
            )

            # Ambil Top 5
            top_projects = project_spending.head(5).copy()

            # Tambah kolom ranking untuk warna
            top_projects["RANK"] = range(1, len(top_projects) + 1)

            # Warna khusus top 1
            top_projects["COLOR"] = top_projects["RANK"].apply(
                lambda x: "Top 1" if x == 1 else "Others"
            )

            fig = px.bar(
                top_projects,
                x="JUMLAH_NUM",
                y="PROJECT/PJ",
                orientation="h",
                color="COLOR",
                color_discrete_map={
                    "Top 1": "#ff4b4b",
                    "Others": "#1f77b4"
                },
                text="JUMLAH_NUM"
            )

            fig.update_layout(
                yaxis=dict(categoryorder="total ascending"),
                xaxis_title="Total Pengeluaran",
                yaxis_title="Project / PIC",
                showlegend=False,
                height=400
            )

            fig.update_traces(
                texttemplate='%{text:,}',
                textposition='outside'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Insight otomatis
            top_name = top_projects.iloc[0]["PROJECT/PJ"]
            top_value = top_projects.iloc[0]["JUMLAH_NUM"]
            total_spending = df_out["JUMLAH_NUM"].sum()

            percentage = (top_value / total_spending) * 100

            st.info(
                f"""
                📌 **Insight:**
                
                Pengeluaran terbesar berasal dari **{top_name}** 
                dengan total sebesar **{format_rp(top_value)}**, 
                berkontribusi sekitar **{percentage:.1f}%** 
                dari total pengeluaran keseluruhan.
                """
            )

        # =========================
        # Analisis Bulanan
        # =========================

        df_cash["MONTH"] = df_cash["DATE"].dt.to_period("M")

        monthly = (
            df_cash.groupby(["MONTH", "TIPE"])["JUMLAH_NUM"]
            .sum()
            .unstack(fill_value=0)
            .reset_index()
            .sort_values("MONTH")
        )

        monthly["NET"] = monthly.get("IN", 0) - monthly.get("OUT", 0)

        monthly["MONTH"] = monthly["MONTH"].astype(str)

        # =========================
        # Tabel Growth
        # =========================
        st.subheader("📊 Detail Cashflow Bulanan")

        display_monthly = monthly.copy()
        display_monthly["NET"] = display_monthly["NET"].apply(format_rp)
        display_monthly["IN"] = display_monthly.get("IN", 0).apply(format_rp)
        display_monthly["OUT"] = display_monthly.get("OUT", 0).apply(format_rp)

        st.dataframe(
            display_monthly[["MONTH", "IN", "OUT", "NET",]],
            use_container_width=True
        )

        # =========================
        # Insight Otomatis
        # =========================

        # Pastikan pakai data numeric (monthly, bukan display_monthly)
        total_in = monthly.get("IN", 0).sum()
        total_out = monthly.get("OUT", 0).sum()
        total_net = monthly["NET"].sum()

        avg_net = monthly["NET"].mean()

        best_month = monthly.loc[monthly["NET"].idxmax()]
        worst_month = monthly.loc[monthly["NET"].idxmin()]

        st.markdown("### 📌 Insight Bulanan")

        st.markdown(f"""
        - Total pemasukan periode ini: **{format_rp(total_in)}**
        - Total pengeluaran periode ini: **{format_rp(total_out)}**
        - Total net cashflow: **{format_rp(total_net)}**
        - Rata-rata net per bulan: **{format_rp(avg_net)}**

        📈 Bulan terbaik: **{best_month['MONTH']}** dengan net **{format_rp(best_month['NET'])}**  
        📉 Bulan terendah: **{worst_month['MONTH']}** dengan net **{format_rp(worst_month['NET'])}**
        """)
