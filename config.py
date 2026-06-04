"""Default configuration for the supply chain simulation."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SimulationConfig:
    """Editable parameters for the baseline simulation."""

    random_seed: int = 42
    simulation_steps: int = 365
    product_count: int = 1

    customer_count: int = 30
    retailer_count: int = 3
    warehouse_count: int = 1
    manufacturer_count: int = 1

    retailer_initial_inventory: int = 120
    retailer_reorder_point: int = 50
    retailer_target_stock: int = 150

    warehouse_initial_inventory: int = 500
    warehouse_reorder_point: int = 200
    warehouse_target_stock: int = 650

    manufacturer_daily_capacity: int = 300

    retailer_lead_time: int = 2
    warehouse_lead_time: int = 5

    customer_min_demand: int = 0
    customer_max_demand: int = 8

    retailer_holding_cost_per_unit: float = 0.10
    warehouse_holding_cost_per_unit: float = 0.04

    inventory_policy: Literal["simple", "forecast"] = "simple"
    safety_stock: int = 40
    forecasting_window: int = 7


DEFAULT_CONFIG = SimulationConfig()
