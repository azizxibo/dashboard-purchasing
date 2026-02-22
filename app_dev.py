import streamlit as st
import pandas as pd
import numpy as np

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
# SIDEBAR - ENTRY ACCESS
# =========================
with st.sidebar:
    st.subheader("🔐 Entry Access")

    pin_input = st.text_input(
        "Masukkan PIN",
        type="password",
        key="pin_input"
    )

    if st.button("Akses Entry"):
        if pin_input == "1234":   # PIN_BENAR = "1234" misalnya
            st.session_state.auth_ok = True
            st.success("Akses entry aktif")
        else:
            st.session_state.auth_ok = False
            st.error("PIN salah")

    # info status (opsional tapi rapi)
    if st.session_state.get("auth_ok"):
        st.caption("🟢 Mode Entry Aktif")
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

    petty_cash = pd.read_csv(url_petty, sep=",", encoding="utf-8", engine="python")
    purchase_request = pd.read_csv(url_pr, sep=",", encoding="utf-8", engine="python")
    cutting_stock = pd.read_csv(url_stock, sep=",", encoding="utf-8", engine="python")

    petty_cash = clean_cols(petty_cash)
    purchase_request = clean_cols(purchase_request)
    cutting_stock = clean_cols(cutting_stock)

    return petty_cash, purchase_request, cutting_stock

petty_cash, pr_data, stock_data = load_data()

# =========================
# NAVIGATION: TABS
# =========================
tab_labels = ["Petty Cash", "Purchase Request", "Cutting Stock", "Entry Data"]
st.caption(f"Total opsi menu: {len(tab_labels)}")
tabs = st.tabs(tab_labels)

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

    petty_cash = petty_cash.sort_values("DATE")
    petty_cash["SALDO_NUM"] = petty_cash["JUMLAH_BERSIH"].cumsum().astype("int64")

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
    # SORTING UNTUK TAMPILAN
    # =========================
    df = df.sort_values("DATE", ascending=False).reset_index(drop=True)
    df.insert(0, "NO", range(1, len(df) + 1))

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

    show_cols = [c for c in ["DATE","KETERANGAN","DESKRIPSI","PROJECT/PJ","TIPE"] if c in df.columns]

    if "KET.PV" in df.columns:
        df["KET.PV"] = df["KET.PV"].fillna("").astype(str).str.upper().str.strip()
        show_cols.insert(4, "KET.PV")  # setelah PROJECT/PJ (opsional)

    view = df[show_cols + ["JUMLAH_NUM", "SALDO_NUM"]].copy()
    # Format DATE agar hanya tampil tanggal saja
    if "DATE" in view.columns:
        view["DATE"] = pd.to_datetime(view["DATE"]).dt.strftime("%d/%m/%Y")

    def pv_style(val: str):
        v = str(val).upper().strip()

        if v == "SUDAH BUAT PV":
        # Hijau lembut, teks hitam
            return (
            "background-color: #C8F7C5;"
            "color: #000000;"
            "font-weight: 600;"
        )

        if v == "BELUM BUAT PV":
        # Merah lembut, teks putih
            return (
            "background-color: #F8C6C6;"
            "color: #000000;"
            "font-weight: 600;"
        )

        return ""

    if "KET.PV" in view.columns:
        st.dataframe(view.style.applymap(pv_style, subset=["KET.PV"]), width="stretch")
    else:
        st.dataframe(view, width="stretch")


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

        k1, k2 = st.columns(2)
        k1.metric("Total Estimasi Pembelian", format_rp(total_estimation))
        k2.metric("Total Item Request", total_item)

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

    for col in ["QTY", "SAFETY STOCK"]:
        if col in stock_data.columns:
            stock_data[col] = pd.to_numeric(stock_data[col], errors="coerce").fillna(0)

    if "QTY" in stock_data.columns and "SAFETY STOCK" in stock_data.columns:
        stock_data["SYSTEM STATUS"] = stock_data.apply(
            lambda r: "RE-STOCK" if r["QTY"] <= r["SAFETY STOCK"] else "AMAN",
            axis=1
        )

        restock_count = int((stock_data["SYSTEM STATUS"] == "RE-STOCK").sum())
        aman_count = int((stock_data["SYSTEM STATUS"] == "AMAN").sum())

        c1, c2 = st.columns(2)
        c1.metric("Item Perlu Re-Stock", restock_count)
        c2.metric("Item Aman", aman_count)

        st.subheader("Prioritas Re-Stock")
        st.dataframe(
            stock_data[stock_data["SYSTEM STATUS"] == "RE-STOCK"].sort_values("QTY"),
            width="stretch"
        )

    st.subheader("Data Stok Lengkap")
    st.dataframe(stock_data, width="stretch")

# ==========================================================
# TAB 4: ENTRY DATA (PLACEHOLDER)
# ==========================================================
with tabs[3]:
    st.header("📝 Entry Data (Internal Use)")

    if not st.session_state.get("auth_ok", False):
        st.warning("🔒 Akses dibatasi. Masukkan PIN untuk membuka menu entry.")
        st.stop()

    st.info(
        "Menu ini akan digunakan untuk:\n"
        "- Input Petty Cash\n"
        "- Input Purchase Request\n"
        "- Update Cutting Stock\n\n"
        "Form akan ditambahkan pada tahap berikutnya."
    )

# ==========================================================
# FORM PETTY CASH (ENTRY DATA)
# ==========================================================
    st.subheader("💰 Form Input Petty Cash")

    with st.form("form_petty_cash", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Tanggal")

            project_select = st.selectbox(
                "Project (jika ada)",
                ["", "Project SPK.073/25", "Project SPK.074/25", "Project SPK.075/25"]
            )
            project_text = st.text_input("Project manual (opsional)")

        with col2:
            pj_select = st.selectbox(
                "PJ (jika ada)",
                ["", "Aziz"]
            )
            pj_text = st.text_input("PJ manual (opsional)")

        keterangan = st.text_input("Keterangan Singkat")
        deskripsi = st.text_area("Deskripsi Transaksi")

        tipe = st.radio("Tipe Transaksi", ["IN", "OUT"], horizontal=True)
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000)

        submitted = st.form_submit_button("💾 Simpan Data")

        if submitted:

            project_final = project_text if project_text else project_select
            pj_final = pj_text if pj_text else pj_select

            project_pj = project_final if project_final else pj_final

            if not project_pj:
                st.warning("⚠️ Project atau PJ wajib diisi.")
            elif jumlah == 0:
                st.warning("⚠️ Jumlah tidak boleh 0.")
            else:
                new_row = {
                    "DATE": date,
                    "KETERANGAN": keterangan,
                    "TIPE": tipe,
                    "JUMLAH": jumlah,
                    "DESKRIPSI": deskripsi,
                    "PROJECT/PJ": project_pj,
                    "KET.PV": "Belum PV"
                }

                st.success("✅ Data valid & siap disimpan")
                st.json(new_row)
