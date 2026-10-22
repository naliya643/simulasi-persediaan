import pandas as pd
import streamlit as st

from simulator import (
    load_demand_distribution,
    run_monte_carlo,
    simulate_one_run,
    validate_distribution,
)

st.set_page_config(page_title="Simulasi Persediaan Monte Carlo", page_icon="📦", layout="wide")

st.title("Simulasi Persediaan Barang")
st.caption("Model persediaan sederhana menggunakan Simulasi Monte Carlo")
st.info(
    "Proyek ini menggunakan data sintetis sebagai contoh pembelajaran. "
    "Hasilnya merupakan estimasi berdasarkan asumsi yang dipilih, bukan prediksi pasti."
)

with st.sidebar:
    st.header("Parameter simulasi")
    initial_stock = st.number_input("Stok awal (unit)", min_value=0, max_value=100000, value=100, step=10)
    reorder_point = st.number_input("Titik pemesanan ulang / ROP (unit)", min_value=0, max_value=100000, value=30, step=5)
    order_quantity = st.number_input("Jumlah setiap pemesanan (unit)", min_value=1, max_value=100000, value=80, step=10)
    lead_time = st.number_input("Waktu pengadaan / lead time (hari)", min_value=1, max_value=60, value=3, step=1)
    days = st.number_input("Lama simulasi (hari)", min_value=1, max_value=365, value=30, step=1)
    replications = st.number_input("Jumlah pengulangan Monte Carlo", min_value=10, max_value=10000, value=500, step=100)
    seed = st.number_input("Seed (agar hasil dapat diulang)", min_value=0, max_value=999999, value=42, step=1)

st.subheader("Distribusi permintaan harian")
st.write(
    "Edit tabel di bawah jika ingin mengubah asumsi permintaan. "
    "Total probabilitas harus sama dengan 1 (atau 100%)."
)
default_distribution = load_demand_distribution("data/demand_distribution.csv")
edited = st.data_editor(
    default_distribution,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "demand": st.column_config.NumberColumn("Permintaan (unit)", min_value=0, step=1),
        "probability": st.column_config.NumberColumn("Probabilitas", min_value=0.0, max_value=1.0, step=0.05, format="%.2f"),
    },
    key="distribution_editor",
)

try:
    distribution = validate_distribution(edited)
    st.success(f"Distribusi valid. Total probabilitas = {distribution['probability'].sum():.2f}")
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if reorder_point >= initial_stock + order_quantity:
    st.warning("Catatan: ROP cukup tinggi dibandingkan stok awal dan jumlah pesanan. Ini boleh saja, tetapi dapat memicu pemesanan lebih awal.")

if st.button("Jalankan simulasi", type="primary", use_container_width=True):
    summary, sample_results = run_monte_carlo(
        distribution=distribution,
        initial_stock=int(initial_stock),
        reorder_point=int(reorder_point),
        order_quantity=int(order_quantity),
        lead_time=int(lead_time),
        days=int(days),
        replications=int(replications),
        seed=int(seed),
    )
    detail = simulate_one_run(
        distribution=distribution,
        initial_stock=int(initial_stock),
        reorder_point=int(reorder_point),
        order_quantity=int(order_quantity),
        lead_time=int(lead_time),
        days=int(days),
        seed=int(seed),
    )

    st.session_state["summary"] = summary
    st.session_state["sample_results"] = sample_results
    st.session_state["detail"] = detail

if "summary" in st.session_state:
    summary = st.session_state["summary"]
    sample_results = st.session_state["sample_results"]
    detail = st.session_state["detail"]

    st.subheader("Ringkasan hasil Monte Carlo")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rata-rata permintaan", f"{summary['mean_demand']:.2f} unit/hari")
    c2.metric("Rata-rata penjualan", f"{summary['mean_sales']:.2f} unit/hari")
    c3.metric("Rata-rata unit tidak terpenuhi", f"{summary['mean_lost_units']:.2f} unit/simulasi")
    c4.metric("Simulasi mengalami kehabisan stok", f"{summary['stockout_probability']:.1%}")

    st.caption(
        f"Ringkasan dihitung dari {int(replications):,} pengulangan, masing-masing selama {int(days)} hari."
    )

    st.subheader("Contoh satu jalannya simulasi")
    st.line_chart(detail.set_index("day")[["ending_stock", "demand"]])
    st.write("Keterangan: garis stok adalah stok akhir setiap hari; garis permintaan menunjukkan permintaan harian.")

    display_columns = {
        "day": "Hari",
        "starting_stock": "Stok awal hari",
        "demand": "Permintaan",
        "sales": "Penjualan terpenuhi",
        "lost_units": "Permintaan tidak terpenuhi",
        "arrivals": "Barang masuk",
        "ending_stock": "Stok akhir hari",
        "order_placed": "Pesanan dibuat",
    }
    st.dataframe(detail.rename(columns=display_columns), use_container_width=True, hide_index=True)

    st.subheader("Sebaran hasil dari seluruh pengulangan")
    st.write("Setiap baris mewakili satu pengulangan simulasi.")
    st.dataframe(sample_results.head(100), use_container_width=True, hide_index=True)

    st.download_button(
        "Unduh detail satu simulasi (CSV)",
        data=detail.to_csv(index=False).encode("utf-8"),
        file_name="detail_simulasi.csv",
        mime="text/csv",
    )
    st.download_button(
        "Unduh hasil semua pengulangan (CSV)",
        data=sample_results.to_csv(index=False).encode("utf-8"),
        file_name="hasil_monte_carlo.csv",
        mime="text/csv",
    )
    st.download_button(
        "Unduh ringkasan (CSV)",
        data=pd.DataFrame([summary]).to_csv(index=False).encode("utf-8"),
        file_name="ringkasan_simulasi.csv",
        mime="text/csv",
    )

with st.expander("Asumsi dan batasan model"):
    st.markdown(
        """
        - Permintaan harian dipilih secara acak dari distribusi diskret yang ditampilkan.
        - Barang yang tersedia dijual terlebih dahulu; permintaan yang melebihi stok dicatat sebagai permintaan tidak terpenuhi (lost sales), bukan utang/backorder.
        - Pemesanan dilakukan ketika **posisi persediaan** (stok tersedia + pesanan yang belum tiba) sama dengan atau di bawah ROP.
        - Pesanan datang setelah jumlah hari lead time yang ditentukan.
        - Model tidak memasukkan biaya simpan, biaya pesan, kedaluwarsa, perubahan harga, atau beberapa jenis barang.
        - Data contoh bersifat sintetis dan perlu diganti dengan data observasi jika ingin digunakan untuk keputusan bisnis nyata.
        """
    )

st.divider()
st.caption("Dibuat untuk pembelajaran Simulasi dan Pemodelan. Dokumentasikan asumsi, pengujian, dan kontribusi pengerjaan secara jujur di GitHub.")
