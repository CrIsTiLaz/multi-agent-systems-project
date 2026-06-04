# Multi-Agent Supply Chain Inventory Simulation

Agent-based simulation of a multi-tier supply chain built with Python and Mesa. Autonomous agents exchange orders and shipments across customers, retailers, a warehouse, a manufacturer, and logistics. The model studies how stochastic demand propagates upstream, how inventory policies perform under lead times and capacity limits, and how the **bullwhip effect** amplifies order variability.

## Problem Domain

Supply chains often react to small changes in customer demand with much larger swings in orders placed by retailers, warehouses, and manufacturers. That **demand amplification** is the bullwhip effect. It is driven by delayed information, batch reordering, and limited production or transport capacity.

This project simulates that behavior in a simplified network:

- **Goal:** minimize stockouts and holding cost while observing (and comparing policies that affect) upstream order volatility.
- **Constraints:** fixed lead times, daily production capacity, decentralized decisions (each agent uses only local state and neighbor messages).
- **Outputs:** service level, stockout rate, inventory levels, holding cost, and bullwhip ratios (variance of upstream orders vs. customer demand).

One product, one simulated day per step, stochastic customer demand (uniform random units per customer per day).

## Architecture

The system is a **discrete-time** simulation orchestrated by `SupplyChainModel` (`model.py`). Agents do not use a central planner; they communicate only with the **next tier**:

```text
  [Customer] ──order──> [Retailer] ──replenish──> [Warehouse] ──produce──> [Manufacturer]
       ^                    ^                         ^                        |
       |                    |                         |                        |
       └──── fulfill ───────┘                         └── shipments ─────────┘
                                    [Logistics: in-transit queue, fixed lead times]
```

| Component | Role |
|-----------|------|
| **CustomerAgent** | Generates daily demand; sends orders to an assigned retailer. |
| **RetailerAgent** | Fulfills customer orders from stock; reorders from warehouse when below reorder point. |
| **WarehouseAgent** | Fulfills retailer orders; reorders from manufacturer when below reorder point. |
| **ManufacturerAgent** | Produces up to daily capacity; excess demand stays in backlog. |
| **LogisticsAgent** | Creates shipments with fixed lead times; delivers to retailers or warehouse. |

**Daily step order** (same sequence every day):

1. Customers generate demand and place orders  
2. Retailers process customer orders  
3. Retailers place replenishment orders  
4. Warehouses process retailer orders (ship via logistics)  
5. Warehouses place manufacturer orders  
6. Manufacturers produce (ship via logistics)  
7. Logistics marks due shipments  
8. Deliveries increase destination inventory  
9. Metrics collected  

**Policies:** simple `(reorder point, target stock)` by default; optional forecast-based policy with moving-average demand and safety stock (`config.py`).

**Analysis pipeline:** `run.py` → baseline + parameter experiments → `analysis.py` (metrics, bullwhip) → `visualization.py` (plots) → `results/`.

## Project Layout

```text
agents/          # Customer, Retailer, Warehouse, Manufacturer, Logistics
model.py         # SupplyChainModel and step orchestration
config.py        # Simulation parameters
run.py           # Entry point
analysis.py      # Metrics, experiments, report
visualization.py # Plots
results/         # CSV data, report.md, plots/
```

## Running

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

Writes metrics and summaries to `results/data/`, notes to `results/report.md`, and plots to `results/plots/` when Matplotlib is available.

## Key Results Files

- `results/data/baseline_metrics.csv` — daily time series  
- `results/data/experiment_summary.csv` — baseline vs. reorder points, lead times, capacity, forecast policy  
- `results/plots/` — demand, inventory, tier orders, stockouts, holding cost, bullwhip  

See `PROJECT_REQUIREMENTS.md` for the full specification and implementation checklist.
