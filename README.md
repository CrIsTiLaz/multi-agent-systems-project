# Multi-Agent Supply Chain Inventory Simulation

## 1. Project Problem Domain

This project simulates a multi-tier supply chain network for studying dynamic inventory management. The system models one product moving from a manufacturer to a warehouse, then to retailers, and finally to customers.

The main problem studied is the **bullwhip effect**: small changes in customer demand can create much larger changes in upstream orders placed by retailers, warehouses, and manufacturers. The simulation also tracks stockouts, inventory holding costs, stochastic customer demand, delivery lead times, and manufacturer production capacity.

The goal is to observe how decentralized agents, each using local information, affect inventory performance and upstream order volatility. The model produces metrics such as service level, stockout rate, holding cost, inventory levels, and bullwhip ratios.

## 2. Project Architecture

The project is a discrete-time multi-agent simulation. One simulation step represents one day. Agents communicate only with neighboring supply chain tiers rather than using a central optimizer.

```text
Customer -> Retailer -> Warehouse -> Manufacturer
              ^             ^              |
              |             |              |
              +------ Logistics: shipments and delivery delays
```

Main agents:

- **CustomerAgent:** generates random demand and places orders.
- **RetailerAgent:** fulfills customer demand from local inventory and reorders from the warehouse.
- **WarehouseAgent:** fulfills retailer replenishment orders and orders production from the manufacturer.
- **ManufacturerAgent:** produces goods with a daily capacity limit and handles production backlog.
- **LogisticsAgent:** manages shipments and delivery delays between tiers.

Daily simulation order:

1. Customers generate demand.
2. Retailers fulfill customer orders.
3. Retailers place replenishment orders.
4. The warehouse processes retailer orders.
5. The warehouse orders from the manufacturer if needed.
6. The manufacturer produces goods.
7. Logistics updates in-transit shipments.
8. Deliveries increase destination inventory.
9. Metrics are collected.

Main files:

- `config.py` - simulation parameters.
- `model.py` - simulation orchestration.
- `agents/` - agent classes.
- `analysis.py` - metrics, bullwhip calculations, and experiments.
- `visualization.py` - plot generation.
- `run.py` - main entry point.
- `results/` - generated CSV files, report, and plots.

## 3. Instructions for Starting the Project

Run the project from the project directory:

```bash
cd /Users/cristi/master/multi-agent-systems/multi-agent-systems-project
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

Running `run.py` executes the baseline simulation and the parameter experiments. It saves the outputs to:

- `results/data/` - CSV metrics and experiment summaries.
- `results/report.md` - generated report notes.
- `results/plots/` - generated charts, if Matplotlib is available.
