# Multi-Agent Supply Chain Inventory Simulation - Project Requirements

## 1. Project Summary

This project simulates a multi-tier supply chain network using a multi-agent system. The system models how customer demand propagates through retailers, warehouses, manufacturers, and logistics providers. The main objective is to study and reduce the bullwhip effect while preventing stockouts and keeping inventory holding costs low.

The simulation will be implemented in Python using Mesa as the agent-based modeling framework. Pandas and Matplotlib will be used to collect, analyze, and visualize simulation results.

## 2. Problem Domain

Supply chains often suffer from demand amplification. Small variations in customer demand can create increasingly larger variations in orders placed by retailers, warehouses, and manufacturers. This phenomenon is known as the bullwhip effect.

The project will simulate this behavior in a simplified but realistic supply chain. Agents will make decentralized decisions based on local information, inventory levels, demand signals, production capacity, and delivery delays.

## 3. Main Goals

The project should achieve the following goals:

- Model a multi-tier supply chain using autonomous agents.
- Simulate dynamic customer demand over multiple time steps.
- Track inventory levels at retailer, warehouse, and manufacturer levels.
- Simulate restocking, production, shipping, and delivery delays.
- Detect and measure stockout events.
- Calculate inventory holding costs.
- Measure the bullwhip effect using demand and order variance.
- Compare different inventory policies or parameter settings.
- Produce plots and metrics that support analysis in the final report.

## 4. Technology Stack

The expected technology stack is:

- Programming language: Python
- Agent-based modeling framework: Mesa
- Data processing: Pandas
- Visualization: Matplotlib
- Optional numerical utilities: NumPy
- Optional configuration format: Python config file or JSON

Suggested dependencies:

```text
mesa
pandas
matplotlib
numpy
```

## 5. Agent Types

### 5.1 Customer Agent

The Customer Agent represents end-user demand.

Responsibilities:

- Generate product demand at each simulation step.
- Place orders to an assigned retailer.
- Record whether the requested demand was fulfilled.
- Contribute to service-level and stockout metrics.

Possible demand models:

- Random uniform demand.
- Poisson-distributed demand.
- Seasonal or trend-based demand for advanced experiments.

Required state:

- Agent ID.
- Assigned retailer.
- Demand history.
- Fulfilled demand history.
- Unfulfilled demand history.

### 5.2 Retailer Agent

The Retailer Agent sells goods to customers and requests replenishment from the warehouse.

Responsibilities:

- Receive customer orders.
- Fulfill orders from local inventory when possible.
- Record partial fulfillment or stockouts.
- Monitor local inventory level.
- Place replenishment orders to the warehouse when inventory falls below a reorder threshold.
- Store order and inventory history.

Required state:

- Current inventory.
- Reorder point.
- Target stock level.
- Pending customer orders.
- Pending replenishment orders.
- Stockout count.
- Holding cost.

Expected decision rule:

- If inventory is below the reorder point, order enough goods to reach the target stock level.

### 5.3 Warehouse Agent

The Warehouse Agent manages regional inventory and supplies retailers.

Responsibilities:

- Receive replenishment orders from retailers.
- Fulfill retailer orders when inventory is available.
- Allocate limited stock across retailers when demand exceeds available inventory.
- Aggregate retailer demand.
- Place production orders to the manufacturer.
- Track regional inventory and order history.

Required state:

- Current inventory.
- Reorder point.
- Target stock level.
- Incoming retailer orders.
- Orders placed to manufacturer.
- Shipment history.
- Holding cost.

Optional allocation policies:

- First-come, first-served.
- Proportional allocation.
- Priority-based allocation.

### 5.4 Manufacturer Agent

The Manufacturer Agent produces goods based on warehouse orders.

Responsibilities:

- Receive orders from warehouses.
- Produce goods subject to a maximum daily production capacity.
- Queue orders that exceed production capacity.
- Send produced goods through the logistics process.
- Track production history, backlog, and fulfilled manufacturer orders.

Required state:

- Daily production capacity.
- Production backlog.
- Completed production.
- Orders received from warehouses.
- Shipments sent.

Important constraint:

- The manufacturer cannot produce more than its maximum capacity during a simulation step.

### 5.5 Logistics Agent

The Logistics Agent or logistics module simulates product movement between supply chain tiers.

Responsibilities:

- Create shipments between manufacturer, warehouse, and retailer.
- Assign delivery times to each shipment.
- Track in-transit goods.
- Deliver goods when their arrival time is reached.
- Optionally model delivery variability or congestion.

Required state:

- Shipment queue.
- Origin and destination for each shipment.
- Quantity in each shipment.
- Departure step.
- Arrival step.
- Delivery status.

Possible delivery-time models:

- Fixed lead time.
- Random lead time within a range.
- Lead time based on route or shipment size.

## 6. Communication Requirements

The system should use decentralized communication between neighboring tiers.

Allowed communication paths:

- Customer Agent to Retailer Agent.
- Retailer Agent to Warehouse Agent.
- Warehouse Agent to Manufacturer Agent.
- Manufacturer Agent to Logistics Agent.
- Logistics Agent to Warehouse Agent.
- Logistics Agent to Retailer Agent.

Agents should not require global knowledge of the entire supply chain. Each agent should make decisions based mainly on:

- Its own inventory.
- Orders received from downstream agents.
- Shipments expected from upstream agents.
- Local policy parameters.

Recommended message types:

- Customer order.
- Replenishment order.
- Production order.
- Shipment notification.
- Delivery confirmation.
- Stockout event.

## 7. Simulation Requirements

The simulation should run over discrete time steps. One step can represent one day.

At each step:

1. Customers generate demand and place orders.
2. Retailers process customer orders.
3. Retailers place replenishment orders if needed.
4. Warehouses process retailer orders.
5. Warehouses place orders to manufacturers if needed.
6. Manufacturers produce goods subject to capacity.
7. Logistics updates in-transit shipments.
8. Delivered shipments increase inventory at the destination.
9. Metrics are collected.

The order of actions must be clearly defined because it affects simulation behavior.

Minimum simulation length:

- 100 steps for development testing.
- 365 steps for final yearly analysis.

Recommended experiments:

- Run multiple random seeds.
- Compare short versus long delivery lead times.
- Compare low versus high reorder thresholds.
- Compare fixed demand versus stochastic demand.
- Compare simple reorder policy versus demand forecasting policy.

## 8. Inventory Policy Requirements

The initial implementation should use a simple reorder policy.

Suggested policy:

```text
if inventory < reorder_point:
    order_quantity = target_stock - inventory
```

Optional advanced policy:

```text
forecast = moving_average(previous_demand, window_size)
order_quantity = forecast * expected_lead_time + safety_stock - current_inventory
```

Policy parameters should be easy to change:

- Reorder point.
- Target stock.
- Safety stock.
- Review period.
- Forecasting window.
- Lead time.

## 9. Metrics and Data Collection

The model should collect metrics at every simulation step.

### 9.1 Inventory Metrics

- Retailer inventory level.
- Warehouse inventory level.
- Manufacturer backlog.
- Goods in transit.
- Average inventory per tier.

### 9.2 Demand and Order Metrics

- Customer demand.
- Customer orders fulfilled.
- Customer orders unfulfilled.
- Retailer orders to warehouse.
- Warehouse orders to manufacturer.
- Manufacturer production quantity.

### 9.3 Performance Metrics

- Number of stockout events.
- Stockout rate.
- Service level.
- Holding cost.
- Backlog size.
- Average delivery delay.
- Bullwhip effect ratio.

### 9.4 Bullwhip Effect Formula

The bullwhip effect can be measured by comparing the variance of upstream orders against the variance of customer demand.

```text
Bullwhip Ratio = Variance(upstream orders) / Variance(customer demand)
```

Example:

```text
Retailer Bullwhip Ratio = Variance(retailer orders to warehouse) / Variance(customer demand)
Warehouse Bullwhip Ratio = Variance(warehouse orders to manufacturer) / Variance(customer demand)
```

Higher values indicate stronger demand amplification.

## 10. Visualization Requirements

The project should generate plots for the final analysis.

Required plots:

- Customer demand over time.
- Inventory levels over time.
- Orders placed at each supply chain tier.
- Stockout events over time.
- Bullwhip ratio comparison.
- Holding cost over time.

Optional plots:

- Service level by experiment.
- Backlog over time.
- In-transit inventory over time.
- Comparison of multiple parameter settings.

## 11. Suggested Project Structure

```text
multi-agent-systems/
├── README.md
├── PROJECT_REQUIREMENTS.md
├── requirements.txt
├── config.py
├── run.py
├── model.py
├── visualization.py
├── analysis.py
├── agents/
│   ├── __init__.py
│   ├── customer.py
│   ├── retailer.py
│   ├── warehouse.py
│   ├── manufacturer.py
│   └── logistics.py
└── results/
    ├── plots/
    └── data/
```

## 12. Achievable Implementation Steps

### Step 1: Define the Scope and Assumptions

Deliverables:

- Decide the number of customers, retailers, warehouses, and manufacturers.
- Decide whether there is one product or multiple products.
- Decide the length of the simulation.
- Decide the basic reorder policy.
- Decide fixed or random lead times.

Suggested first version:

- One product.
- Multiple customers.
- Three retailers.
- One warehouse.
- One manufacturer.
- One logistics component.
- Fixed delivery lead times.
- Simple reorder policy.

Completion criteria:

- The assumptions are written in the README or project report.
- The main parameters are listed in `config.py`.

### Step 2: Create the Basic Project Skeleton

Deliverables:

- Create Python package structure.
- Add `requirements.txt`.
- Add empty agent files.
- Add a basic `SupplyChainModel` class.
- Add a `run.py` script.

Completion criteria:

- The project can be imported without errors.
- `python run.py` starts a minimal simulation.

### Step 3: Implement the Customer Agent

Deliverables:

- Customer agents generate random demand each step.
- Customers send orders to retailers.
- Demand history is stored.

Completion criteria:

- Demand is generated for each simulation step.
- Total customer demand can be printed or collected.

### Step 4: Implement the Retailer Agent

Deliverables:

- Retailers receive customer orders.
- Retailers reduce inventory when orders are fulfilled.
- Retailers record stockouts when inventory is insufficient.
- Retailers place replenishment orders to the warehouse.

Completion criteria:

- Retail inventory changes over time.
- Stockouts are counted.
- Retailers create warehouse orders when inventory is low.

### Step 5: Implement the Warehouse Agent

Deliverables:

- Warehouse receives retailer replenishment orders.
- Warehouse fulfills retailer orders from inventory.
- Warehouse places manufacturer orders when inventory is low.
- Warehouse records order and inventory history.

Completion criteria:

- Retailer orders affect warehouse inventory.
- Warehouse orders are sent to the manufacturer.

### Step 6: Implement the Manufacturer Agent

Deliverables:

- Manufacturer receives warehouse orders.
- Manufacturer produces goods with a daily capacity limit.
- Unfinished orders are stored as backlog.
- Produced goods are sent to logistics.

Completion criteria:

- Manufacturer production never exceeds daily capacity.
- Backlog increases when demand exceeds capacity.
- Produced goods become shipments.

### Step 7: Implement Logistics and Delivery Delays

Deliverables:

- Create shipment objects or dictionaries.
- Track goods in transit.
- Deliver shipments after the configured lead time.
- Increase destination inventory when shipments arrive.

Completion criteria:

- Goods do not arrive instantly.
- Inventory increases only when delivery time is reached.
- In-transit goods can be measured.

### Step 8: Add Data Collection

Deliverables:

- Use Mesa `DataCollector` or custom logging.
- Collect model-level metrics every step.
- Collect agent-level metrics where useful.
- Export results to Pandas DataFrames.

Completion criteria:

- Simulation results can be accessed after a run.
- Key metrics are available in tabular form.

### Step 9: Add Visualizations

Deliverables:

- Plot customer demand over time.
- Plot retailer and warehouse inventory over time.
- Plot orders between supply chain tiers.
- Plot stockouts.
- Plot bullwhip ratio by tier.

Completion criteria:

- Running the project generates plots.
- Plots can be used directly in the final report.

### Step 10: Implement Bullwhip Analysis

Deliverables:

- Calculate demand variance.
- Calculate variance of retailer orders.
- Calculate variance of warehouse orders.
- Compute bullwhip ratios.

Completion criteria:

- The project prints or saves bullwhip ratio results.
- The final report can explain whether the bullwhip effect appeared.

### Step 11: Run Baseline Experiment

Deliverables:

- Run simulation with default parameters.
- Save metrics and plots.
- Record stockout rate, holding cost, service level, and bullwhip ratios.

Completion criteria:

- A baseline result exists for comparison.
- The output is reproducible using a fixed random seed.

### Step 12: Run Parameter Experiments

Deliverables:

- Compare at least two different reorder points.
- Compare at least two different lead times.
- Compare at least two different production capacities.
- Optionally compare simple reorder policy against forecasting policy.

Completion criteria:

- Results show how parameters affect stockouts, cost, and bullwhip.
- The final report includes comparison plots or tables.

### Step 13: Improve the Inventory Policy

Deliverables:

- Add safety stock or moving-average demand forecasting.
- Compare improved policy against the baseline policy.

Completion criteria:

- Improved policy reduces stockouts or bullwhip in at least one scenario.
- Tradeoffs are discussed, such as higher inventory cost.

### Step 14: Prepare Final Report and Presentation

Deliverables:

- Explain the problem domain.
- Describe agent types and their behaviors.
- Include system architecture diagram.
- Explain communication between agents.
- Present simulation results.
- Discuss bullwhip effect observations.
- Discuss limitations and future improvements.

Completion criteria:

- Report includes methodology, experiments, results, and conclusion.
- Project can be demonstrated by running the simulation.

## 13. Minimum Viable Product

The minimum viable version should include:

- One product.
- Customer, retailer, warehouse, manufacturer, and logistics components.
- Random customer demand.
- Retailer and warehouse reorder policies.
- Manufacturer production capacity.
- Delivery lead times.
- Inventory tracking.
- Stockout tracking.
- Bullwhip ratio calculation.
- At least three plots.

## 14. Advanced Features

If time allows, the following features can improve the project:

- Multiple warehouses.
- Multiple products.
- Variable transportation delays.
- Transportation costs.
- Retailer competition.
- Warehouse negotiation with manufacturer.
- Demand forecasting.
- Adaptive reorder thresholds.
- Reinforcement learning for inventory policy.
- Interactive Mesa visualization.
- Batch experiments over many parameter combinations.

## 15. Risks and Mitigation

### Risk: Scope becomes too large

Mitigation:

- Start with one product and one warehouse.
- Add complexity only after the basic simulation works.

### Risk: Agent scheduling creates confusing results

Mitigation:

- Clearly document the order of actions in each step.
- Use a consistent step sequence.

### Risk: Bullwhip effect does not appear clearly

Mitigation:

- Use stochastic demand.
- Add delivery delays.
- Use reorder thresholds and batch ordering.
- Run the simulation for enough steps.

### Risk: Results are difficult to explain

Mitigation:

- Collect simple metrics first.
- Use clear plots.
- Compare only a few important scenarios.

## 16. Suggested Timeline

### Week 1: Design and Setup

- Finalize assumptions.
- Create repository structure.
- Install dependencies.
- Create model skeleton.

### Week 2: Core Agents

- Implement customers.
- Implement retailers.
- Implement warehouse.
- Implement manufacturer.

### Week 3: Logistics and Data Collection

- Add shipment delays.
- Add inventory tracking.
- Add stockout tracking.
- Add data export.

### Week 4: Analysis and Visualization

- Add bullwhip calculation.
- Generate plots.
- Run baseline experiment.

### Week 5: Experiments and Improvements

- Run parameter comparisons.
- Add improved inventory policy.
- Analyze tradeoffs.

### Week 6: Report and Presentation

- Write final report.
- Prepare diagrams.
- Prepare demonstration.
- Clean up code and documentation.

## 17. Final Evaluation Checklist

Use this checklist before submission:

- The simulation runs from a single command.
- All required agent types are implemented.
- Inventory levels change realistically.
- Customer demand is stochastic.
- Stockouts are tracked.
- Manufacturer capacity is enforced.
- Delivery delays are simulated.
- Data is collected for every step.
- Bullwhip ratios are calculated.
- At least three useful plots are generated.
- Results are explained in the report.
- Limitations and future work are discussed.

