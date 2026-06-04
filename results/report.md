# Supply Chain Simulation Report

## Methodology

The model simulates one product moving through customers, three retailers, one warehouse, one manufacturer, and a logistics component. Each step represents one day. Customers generate stochastic demand, retailers fulfill from inventory and reorder, the warehouse fulfills retailer replenishment orders and orders production, the manufacturer produces subject to capacity, and logistics enforces fixed delivery lead times.

## Baseline Results

- Service level: 0.885
- Stockout rate: 0.115
- Total holding cost: 51863.64
- Retailer bullwhip ratio: 75.943
- Warehouse bullwhip ratio: 315.733
- Final manufacturer backlog: 0

## Experiment Highlights

- Highest service level: high_reorder_points (0.951).
- Lowest retailer bullwhip ratio: high_reorder_points (62.229).

## Limitations and Future Work

- The network uses one warehouse and one manufacturer, so allocation behavior is simple.
- Reorder policies are intentionally basic and can create large upstream backlogs.
- Future work can add multiple warehouses, variable lead times, transportation costs, and adaptive policies.