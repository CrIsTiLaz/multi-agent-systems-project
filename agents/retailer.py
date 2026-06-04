"""Retailer agent skeleton."""

from dataclasses import dataclass, field


@dataclass
class RetailerAgent:
    unique_id: str
    inventory: int
    reorder_point: int
    target_stock: int
    pending_customer_orders: list[dict] = field(default_factory=list)
    pending_replenishment_orders: list[dict] = field(default_factory=list)
    stockout_count: int = 0
    holding_cost: float = 0.0
    order_history: list[int] = field(default_factory=list)
    inventory_history: list[int] = field(default_factory=list)
    daily_demand_history: list[int] = field(default_factory=list)

    def receive_customer_order(self, order: dict) -> None:
        self.pending_customer_orders.append(order)

    def receive_shipment(self, quantity: int) -> None:
        self.inventory += quantity

    def process_customer_orders(self) -> dict[str, int]:
        total_requested = 0
        total_fulfilled = 0
        total_unfulfilled = 0

        for order in self.pending_customer_orders:
            requested = int(order["quantity"])
            fulfilled = min(requested, self.inventory)
            unfulfilled = requested - fulfilled

            self.inventory -= fulfilled
            total_requested += requested
            total_fulfilled += fulfilled
            total_unfulfilled += unfulfilled

            if unfulfilled > 0:
                self.stockout_count += 1

            customer = order.get("customer")
            if customer is not None:
                customer.record_fulfillment(fulfilled, unfulfilled)

        self.pending_customer_orders.clear()
        self.daily_demand_history.append(total_requested)
        self.inventory_history.append(self.inventory)

        return {
            "requested": total_requested,
            "fulfilled": total_fulfilled,
            "unfulfilled": total_unfulfilled,
            "stockouts": self.stockout_count,
        }

    def place_replenishment_order(
        self,
        warehouse: object,
        current_step: int,
        policy: str = "simple",
        expected_lead_time: int = 1,
        safety_stock: int = 0,
        forecasting_window: int = 7,
    ) -> int:
        if self.inventory >= self.reorder_point:
            self.order_history.append(0)
            return 0

        if policy == "forecast":
            recent_demand = self.daily_demand_history[-forecasting_window:]
            forecast = sum(recent_demand) / len(recent_demand) if recent_demand else 0
            desired_stock = round(forecast * expected_lead_time + safety_stock)
        else:
            desired_stock = self.target_stock

        order_quantity = max(desired_stock - self.inventory, 0)
        order = {
            "step": current_step,
            "retailer_id": self.unique_id,
            "retailer": self,
            "quantity": order_quantity,
        }
        self.pending_replenishment_orders.append(order)
        self.order_history.append(order_quantity)
        warehouse.receive_retailer_order(order)
        return order_quantity

    def mark_replenishment_shipped(self, order: dict) -> None:
        if order in self.pending_replenishment_orders:
            self.pending_replenishment_orders.remove(order)
