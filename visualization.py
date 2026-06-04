"""Plot generation for simulation outputs."""

from __future__ import annotations

import os
from pathlib import Path

from analysis import calculate_bullwhip_ratios

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path("results/matplotlib-cache")))
os.environ.setdefault("XDG_CACHE_HOME", str(Path("results/cache")))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


PLOT_DIR = Path("results/plots")


def generate_plots(metrics: list[dict], output_dir: Path = PLOT_DIR) -> list[Path]:
    if plt is None:
        return []

    output_dir.mkdir(parents=True, exist_ok=True)
    generated = [
        _line_plot(
            metrics,
            ["customer_demand"],
            "Customer Demand Over Time",
            "Demand units",
            output_dir / "customer_demand.png",
        ),
        _line_plot(
            metrics,
            ["retailer_inventory", "warehouse_inventory"],
            "Inventory Levels Over Time",
            "Inventory units",
            output_dir / "inventory_levels.png",
        ),
        _line_plot(
            metrics,
            [
                "retailer_replenishment_order_quantity",
                "warehouse_manufacturer_order_quantity",
            ],
            "Orders by Supply Chain Tier",
            "Order units",
            output_dir / "tier_orders.png",
        ),
        _line_plot(
            metrics,
            ["customer_unfulfilled", "retailer_stockouts"],
            "Stockout Events Over Time",
            "Count",
            output_dir / "stockouts.png",
        ),
        _line_plot(
            metrics,
            ["holding_cost"],
            "Holding Cost Over Time",
            "Cost",
            output_dir / "holding_cost.png",
        ),
        _bar_plot(
            calculate_bullwhip_ratios(metrics),
            "Bullwhip Ratio Comparison",
            output_dir / "bullwhip_ratios.png",
        ),
    ]
    return generated


def _line_plot(
    metrics: list[dict],
    columns: list[str],
    title: str,
    ylabel: str,
    path: Path,
) -> Path:
    steps = [row["step"] for row in metrics]
    plt.figure(figsize=(10, 5))
    for column in columns:
        plt.plot(steps, [row.get(column, 0) for row in metrics], label=column)
    plt.title(title)
    plt.xlabel("Step")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path


def _bar_plot(values: dict[str, float], title: str, path: Path) -> Path:
    plt.figure(figsize=(8, 5))
    plt.bar(values.keys(), values.values(), color=["#2563eb", "#f97316"])
    plt.title(title)
    plt.ylabel("Variance ratio")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    return path
