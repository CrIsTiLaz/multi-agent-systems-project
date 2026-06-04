"""Customer agent skeleton."""

from dataclasses import dataclass, field
from random import Random
from typing import Any


@dataclass
class CustomerAgent:
    unique_id: str
    assigned_retailer: Any
    demand_history: list[int] = field(default_factory=list)
    fulfilled_demand_history: list[int] = field(default_factory=list)
    unfulfilled_demand_history: list[int] = field(default_factory=list)

    def generate_demand(self, current_step: int, rng: Random, min_demand: int, max_demand: int) -> int:
        """Generate demand and place the order with the assigned retailer."""

        demand = rng.randint(min_demand, max_demand)
        self.demand_history.append(demand)
        self.assigned_retailer.receive_customer_order(
            {
                "step": current_step,
                "customer_id": self.unique_id,
                "customer": self,
                "quantity": demand,
            }
        )
        return demand

    def record_fulfillment(self, fulfilled_quantity: int, unfulfilled_quantity: int) -> None:
        self.fulfilled_demand_history.append(fulfilled_quantity)
        self.unfulfilled_demand_history.append(unfulfilled_quantity)
