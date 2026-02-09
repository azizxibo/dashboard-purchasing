import streamlit as st
import pandas as pd
import numpy as np

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
st.title("📊 Dashboard Purchasing & Inventory")
st.caption("Monitoring Petty Cash, Purchase Request, dan Cutting Stock")

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
tab_labels = ["Petty Cash", "Purchase Request", "Cutting Stock"]
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
    # KPI (FOKUS CASHFLOW)
    # =========================
    saldo_akhir_all = int(petty_cash["SALDO_NUM"].iloc[-1]) if len(petty_cash) else 0
    total_in = int(df[df["TIPE"] == "IN"]["JUMLAH_NUM"].sum())
    total_out = int(df[df["TIPE"] == "OUT"]["JUMLAH_NUM"].sum())
    net_range = int(df["JUMLAH_BERSIH"].sum())
    total_transaksi = len(df)

    k1, k2, k3, k4, k5 = st.columns([1.2, 1, 1, 1, 1])
    k1.metric("Saldo Akhir (seluruh data)", format_rp(saldo_akhir_all))
    k2.metric("Total IN (filter)", format_rp(total_in))
    k3.metric("Total OUT (filter)", format_rp(total_out))
    k4.metric("Net (filter)", format_rp(net_range))
    k5.metric("Total Transaksi", total_transaksi)

    # =========================
    # TABEL UTAMA (RUPIAH)
    # =========================
    st.subheader("Detail Transaksi")

    show_cols = [c for c in ["DATE","KETERANGAN","DESKRIPSI","PROJECT/PJ","TIPE"] if c in df.columns]

    if "KET.PV" in df.columns:
        df["KET.PV"] = df["KET.PV"].fillna("").astype(str).str.upper().str.strip()
        show_cols.insert(4, "KET.PV")  # setelah PROJECT/PJ (opsional)

    view = df[show_cols + ["JUMLAH_NUM", "SALDO_NUM"]].copy()
    view["JUMLAH"] = view["JUMLAH_NUM"].apply(format_rp)
    view["SALDO"] = view["SALDO_NUM"].apply(format_rp)
    view = view.drop(columns=["JUMLAH_NUM", "SALDO_NUM"])

    def pv_style(val: str):
        v = str(val).upper().strip()
        if v == "SUDAH BUAT PV":
            return "background-color: rgba(0, 200, 0, 0.18); color: #9eff9e; font-weight: 700;"
        if v == "BELUM BUAT PV":
            return "background-color: rgba(255, 0, 0, 0.18); color: #ffb3b3; font-weight: 700;"
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

    if "SUBTOTAL" in pr_data.columns:
        pr_data["SUBTOTAL_NUM"] = parse_rupiah(pr_data["SUBTOTAL"]).astype("int64")
        total_estimation = int(pr_data["SUBTOTAL_NUM"].sum())
    else:
        total_estimation = 0

    c1, c2 = st.columns(2)
    c1.metric("Total Estimasi Pembelian", format_rp(total_estimation))
    c2.metric("Total Item Request", len(pr_data))

    if "PROJECT" in pr_data.columns:
        project_list = ["ALL"] + sorted(pr_data["PROJECT"].dropna().unique().tolist())
        selected_project = st.selectbox("Filter Project", project_list)
        if selected_project != "ALL":
            pr_data = pr_data[pr_data["PROJECT"] == selected_project]

    pr_view = pr_data.copy()
    if "SUBTOTAL_NUM" in pr_view.columns:
        pr_view["SUBTOTAL"] = pr_view["SUBTOTAL_NUM"].apply(format_rp)
        pr_view = pr_view.drop(columns=["SUBTOTAL_NUM"])

    st.subheader("Daftar Purchase Request")
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
