"""Logika simulasi persediaan Monte Carlo.

Model:
- Permintaan harian dipilih dari distribusi diskret.
- Lost sales: permintaan yang tidak dapat dipenuhi tidak menjadi backlog.
- Pemesanan dipicu jika inventory position <= reorder point.
- Pesanan tiba pada awal hari t + lead_time.
"""

from pathlib import Path
import numpy as np
import pandas as pd


def load_demand_distribution(path):
    """Muat distribusi permintaan dari CSV."""
    return pd.read_csv(path)


def validate_distribution(distribution):
    """Validasi dan kembalikan distribusi dengan format standar."""
    required = {"demand", "probability"}
    if not required.issubset(distribution.columns):
        raise ValueError("Distribusi wajib memiliki kolom 'demand' dan 'probability'.")

    result = distribution[["demand", "probability"]].copy()
    if result.empty:
        raise ValueError("Distribusi permintaan tidak boleh kosong.")

    result["demand"] = pd.to_numeric(result["demand"], errors="coerce")
    result["probability"] = pd.to_numeric(result["probability"], errors="coerce")

    if result.isna().any().any():
        raise ValueError("Nilai permintaan dan probabilitas harus berupa angka.")
    if (result["demand"] < 0).any():
        raise ValueError("Permintaan tidak boleh negatif.")
    if not np.all(np.isclose(result["demand"], np.round(result["demand"]))):
        raise ValueError("Permintaan harus berupa bilangan bulat.")
    if (result["probability"] < 0).any():
        raise ValueError("Probabilitas tidak boleh negatif.")
    if result["probability"].sum() <= 0:
        raise ValueError("Total probabilitas harus lebih besar dari nol.")
    if not np.isclose(result["probability"].sum(), 1.0, atol=1e-6):
        raise ValueError(
            f"Total probabilitas harus 1.00, saat ini {result['probability'].sum():.4f}."
        )

    result["demand"] = result["demand"].astype(int)
    result = result.groupby("demand", as_index=False)["probability"].sum()
    result = result.sort_values("demand").reset_index(drop=True)
    if not np.isclose(result["probability"].sum(), 1.0, atol=1e-6):
        raise ValueError("Total probabilitas setelah validasi harus 1.00.")
    return result


def simulate_one_run(
    distribution,
    initial_stock=100,
    reorder_point=30,
    order_quantity=80,
    lead_time=3,
    days=30,
    seed=42,
):
    """Jalankan satu replikasi simulasi dan kembalikan detail per hari."""
    distribution = validate_distribution(distribution)

    if initial_stock < 0:
        raise ValueError("Stok awal tidak boleh negatif.")
    if reorder_point < 0:
        raise ValueError("ROP tidak boleh negatif.")
    if order_quantity <= 0:
        raise ValueError("Jumlah pemesanan harus lebih besar dari nol.")
    if lead_time < 1:
        raise ValueError("Lead time minimal 1 hari.")
    if days < 1:
        raise ValueError("Durasi simulasi minimal 1 hari.")

    rng = np.random.default_rng(seed)
    demand_values = distribution["demand"].to_numpy()
    probabilities = distribution["probability"].to_numpy()

    on_hand = int(initial_stock)
    # Daftar pesanan yang akan tiba: (hari_kedatangan, jumlah_unit).
    pipeline = []
    records = []

    for day in range(1, int(days) + 1):
        # Barang yang dijadwalkan tiba pada hari ini masuk di awal hari.
        arrivals = sum(qty for arrival_day, qty in pipeline if arrival_day == day)
        pipeline = [(arrival_day, qty) for arrival_day, qty in pipeline if arrival_day != day]
        on_hand += arrivals
        starting_stock = on_hand

        demand = int(rng.choice(demand_values, p=probabilities))
        sales = min(on_hand, demand)
        lost_units = demand - sales
        on_hand -= sales

        outstanding = sum(qty for _, qty in pipeline)
        inventory_position = on_hand + outstanding
        order_placed = 0

        # Pesanan yang dibuat hari ini tiba pada awal hari day + lead_time.
        if inventory_position <= reorder_point:
            order_placed = int(order_quantity)
            pipeline.append((day + int(lead_time), order_placed))

        records.append(
            {
                "day": day,
                "starting_stock": starting_stock,
                "arrivals": int(arrivals),
                "demand": demand,
                "sales": int(sales),
                "lost_units": int(lost_units),
                "ending_stock": int(on_hand),
                "inventory_position": int(inventory_position),
                "order_placed": order_placed,
                "outstanding_orders_end_of_day": int(sum(qty for _, qty in pipeline)),
            }
        )

    return pd.DataFrame(records)


def run_monte_carlo(
    distribution,
    initial_stock=100,
    reorder_point=30,
    order_quantity=80,
    lead_time=3,
    days=30,
    replications=500,
    seed=42,
):
    """Jalankan banyak replikasi dan kembalikan ringkasan serta hasil per replikasi."""
    distribution = validate_distribution(distribution)
    if replications < 1:
        raise ValueError("Jumlah replikasi minimal 1.")

    seed_sequence = np.random.SeedSequence(int(seed))
    child_seeds = seed_sequence.spawn(int(replications))
    rows = []

    for replication, child_seed in enumerate(child_seeds, start=1):
        run_seed = int(child_seed.generate_state(1)[0])
        detail = simulate_one_run(
            distribution=distribution,
            initial_stock=initial_stock,
            reorder_point=reorder_point,
            order_quantity=order_quantity,
            lead_time=lead_time,
            days=days,
            seed=run_seed,
        )
        total_demand = int(detail["demand"].sum())
        total_sales = int(detail["sales"].sum())
        lost_units = int(detail["lost_units"].sum())
        rows.append(
            {
                "replication": replication,
                "total_demand": total_demand,
                "total_sales": total_sales,
                "total_lost_units": lost_units,
                "ending_stock": int(detail.iloc[-1]["ending_stock"]),
                "number_of_orders": int((detail["order_placed"] > 0).sum()),
                "stockout_days": int((detail["lost_units"] > 0).sum()),
                "experienced_stockout": bool((detail["lost_units"] > 0).any()),
            }
        )

    results = pd.DataFrame(rows)
    summary = {
        "replications": int(replications),
        "days_per_replication": int(days),
        "mean_demand": float(results["total_demand"].mean() / days),
        "mean_sales": float(results["total_sales"].mean() / days),
        "mean_lost_units": float(results["total_lost_units"].mean()),
        "stockout_probability": float(results["experienced_stockout"].mean()),
        "mean_ending_stock": float(results["ending_stock"].mean()),
        "mean_number_of_orders": float(results["number_of_orders"].mean()),
        "mean_stockout_days": float(results["stockout_days"].mean()),
    }
    return summary, results
