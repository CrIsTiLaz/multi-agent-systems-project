"""Analysis and experiment utilities for the supply chain simulation."""

from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path
from statistics import fmean, variance
from typing import Iterable

from config import DEFAULT_CONFIG, SimulationConfig
from model import SupplyChainModel

try:
    import pandas as pd
except ImportError:  # The CSV fallback keeps the project runnable before dependencies are installed.
    pd = None


DATA_DIR = Path("results/data")
REPORT_PATH = Path("results/report.md")


def run_simulation(config: SimulationConfig = DEFAULT_CONFIG) -> list[dict]:
    model = SupplyChainModel(config)
    return model.run()


def to_dataframe(metrics: list[dict]):
    if pd is None:
        return metrics
    return pd.DataFrame(metrics)


def save_metrics(metrics: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pd is not None:
        pd.DataFrame(metrics).to_csv(path, index=False)
        return

    if not metrics:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(metrics[0].keys()))
        writer.writeheader()
        writer.writerows(metrics)


def calculate_bullwhip_ratios(metrics: list[dict]) -> dict[str, float]:
    customer_demand = _series(metrics, "customer_demand")
    retailer_orders = _series(metrics, "retailer_replenishment_order_quantity")
    warehouse_orders = _series(metrics, "warehouse_manufacturer_order_quantity")

    demand_variance = _variance_or_zero(customer_demand)
    if demand_variance == 0:
        return {"retailer_bullwhip_ratio": 0.0, "warehouse_bullwhip_ratio": 0.0}

    return {
        "retailer_bullwhip_ratio": _variance_or_zero(retailer_orders) / demand_variance,
        "warehouse_bullwhip_ratio": _variance_or_zero(warehouse_orders) / demand_variance,
    }


def summarize_metrics(name: str, config: SimulationConfig, metrics: list[dict]) -> dict:
    total_demand = sum(_series(metrics, "customer_demand"))
    total_fulfilled = sum(_series(metrics, "customer_fulfilled"))
    total_unfulfilled = sum(_series(metrics, "customer_unfulfilled"))
    final = metrics[-1] if metrics else {}
    bullwhip = calculate_bullwhip_ratios(metrics)

    return {
        "experiment": name,
        "steps": len(metrics),
        "policy": config.inventory_policy,
        "retailer_reorder_point": config.retailer_reorder_point,
        "warehouse_reorder_point": config.warehouse_reorder_point,
        "retailer_lead_time": config.retailer_lead_time,
        "warehouse_lead_time": config.warehouse_lead_time,
        "manufacturer_daily_capacity": config.manufacturer_daily_capacity,
        "total_demand": total_demand,
        "total_fulfilled": total_fulfilled,
        "total_unfulfilled": total_unfulfilled,
        "service_level": total_fulfilled / total_demand if total_demand else 1.0,
        "stockout_rate": total_unfulfilled / total_demand if total_demand else 0.0,
        "total_holding_cost": sum(_series(metrics, "holding_cost")),
        "average_retailer_inventory": _mean(_series(metrics, "average_retailer_inventory")),
        "average_warehouse_inventory": _mean(_series(metrics, "average_warehouse_inventory")),
        "final_manufacturer_backlog": final.get("manufacturer_backlog", 0),
        **bullwhip,
    }


def run_baseline() -> tuple[list[dict], dict]:
    metrics = run_simulation(DEFAULT_CONFIG)
    save_metrics(metrics, DATA_DIR / "baseline_metrics.csv")
    summary = summarize_metrics("baseline", DEFAULT_CONFIG, metrics)
    save_summary_rows([summary], DATA_DIR / "baseline_summary.csv")
    return metrics, summary


def run_experiments() -> list[dict]:
    experiments = {
        "baseline": DEFAULT_CONFIG,
        "low_reorder_points": replace(
            DEFAULT_CONFIG,
            retailer_reorder_point=35,
            warehouse_reorder_point=150,
        ),
        "high_reorder_points": replace(
            DEFAULT_CONFIG,
            retailer_reorder_point=80,
            warehouse_reorder_point=300,
        ),
        "short_lead_times": replace(DEFAULT_CONFIG, retailer_lead_time=1, warehouse_lead_time=3),
        "long_lead_times": replace(DEFAULT_CONFIG, retailer_lead_time=4, warehouse_lead_time=8),
        "low_capacity": replace(DEFAULT_CONFIG, manufacturer_daily_capacity=180),
        "high_capacity": replace(DEFAULT_CONFIG, manufacturer_daily_capacity=450),
        "forecast_policy": replace(DEFAULT_CONFIG, inventory_policy="forecast", safety_stock=80),
    }

    summaries = []
    for name, config in experiments.items():
        metrics = run_simulation(config)
        save_metrics(metrics, DATA_DIR / f"{name}_metrics.csv")
        summaries.append(summarize_metrics(name, config, metrics))

    save_summary_rows(summaries, DATA_DIR / "experiment_summary.csv")
    return summaries


def save_summary_rows(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if pd is not None:
        pd.DataFrame(rows).to_csv(path, index=False)
        return

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(baseline_summary: dict, experiment_summaries: list[dict]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    best_service = max(experiment_summaries, key=lambda row: row["service_level"])
    lowest_bullwhip = min(experiment_summaries, key=lambda row: row["retailer_bullwhip_ratio"])

    lines = [
        "# Supply Chain Simulation Report",
        "",
        "## Methodology",
        "",
        "The model simulates one product moving through customers, three retailers, one warehouse, one manufacturer, and a logistics component. Each step represents one day. Customers generate stochastic demand, retailers fulfill from inventory and reorder, the warehouse fulfills retailer replenishment orders and orders production, the manufacturer produces subject to capacity, and logistics enforces fixed delivery lead times.",
        "",
        "## Baseline Results",
        "",
        _format_summary(baseline_summary),
        "",
        "## Experiment Highlights",
        "",
        f"- Highest service level: {best_service['experiment']} ({best_service['service_level']:.3f}).",
        f"- Lowest retailer bullwhip ratio: {lowest_bullwhip['experiment']} ({lowest_bullwhip['retailer_bullwhip_ratio']:.3f}).",
        "",
        "## Limitations and Future Work",
        "",
        "- The network uses one warehouse and one manufacturer, so allocation behavior is simple.",
        "- Reorder policies are intentionally basic and can create large upstream backlogs.",
        "- Future work can add multiple warehouses, variable lead times, transportation costs, and adaptive policies.",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _format_summary(summary: dict) -> str:
    return "\n".join(
        [
            f"- Service level: {summary['service_level']:.3f}",
            f"- Stockout rate: {summary['stockout_rate']:.3f}",
            f"- Total holding cost: {summary['total_holding_cost']:.2f}",
            f"- Retailer bullwhip ratio: {summary['retailer_bullwhip_ratio']:.3f}",
            f"- Warehouse bullwhip ratio: {summary['warehouse_bullwhip_ratio']:.3f}",
            f"- Final manufacturer backlog: {summary['final_manufacturer_backlog']}",
        ]
    )


def _series(metrics: list[dict], key: str) -> list[float]:
    return [float(row.get(key, 0)) for row in metrics]


def _variance_or_zero(values: Iterable[float]) -> float:
    values = list(values)
    return variance(values) if len(values) > 1 else 0.0


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return fmean(values) if values else 0.0
