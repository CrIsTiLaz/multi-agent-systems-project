"""Warehouse agent skeleton."""

from dataclasses import dataclass, field


@dataclass
class WarehouseAgent:
    unique_id: str
    inventory: int
    reorder_point: int
    target_stock: int
    incoming_retailer_orders: list[dict] = field(default_factory=list)
    manufacturer_order_history: list[int] = field(default_factory=list)
    shipment_history: list[int] = field(default_factory=list)
    inventory_history: list[int] = field(default_factory=list)
    holding_cost: float = 0.0
    daily_retailer_demand_history: list[int] = field(default_factory=list)

    def receive_retailer_order(self, order: dict) -> None:
        self.incoming_retailer_orders.append(order)

    def receive_shipment(self, quantity: int) -> None:
        self.inventory += quantity

    def process_retailer_orders(
        self,
        logistics: object,
        current_step: int,
        lead_time: int,
    ) -> dict[str, int]:
        requested = 0
        shipped = 0
        unfilled = 0
        remaining_orders: list[dict] = []

        for order in self.incoming_retailer_orders:
            quantity = int(order["quantity"])
            requested += quantity
            fulfilled = min(quantity, self.inventory)
            shortage = quantity - fulfilled

            if fulfilled > 0:
                self.inventory -= fulfilled
                shipped += fulfilled
                self.shipment_history.append(fulfilled)
                logistics.create_shipment(
                    origin=self,
                    destination=order["retailer"],
                    quantity=fulfilled,
                    departure_step=current_step,
                    lead_time=lead_time,
                )

            if shortage > 0:
                unfilled += shortage
                order["quantity"] = shortage
                remaining_orders.append(order)
            else:
                order["retailer"].mark_replenishment_shipped(order)

        self.incoming_retailer_orders = remaining_orders
        self.daily_retailer_demand_history.append(requested)
        self.inventory_history.append(self.inventory)

        return {
            "requested": requested,
            "shipped": shipped,
            "unfilled": unfilled,
        }

    def place_manufacturer_order(
        self,
        manufacturer: object,
        current_step: int,
        policy: str = "simple",
        expected_lead_time: int = 1,
        safety_stock: int = 0,
        forecasting_window: int = 7,
    ) -> int:
        if self.inventory >= self.reorder_point:
            self.manufacturer_order_history.append(0)
            return 0

        if policy == "forecast":
            recent_demand = self.daily_retailer_demand_history[-forecasting_window:]
            forecast = sum(recent_demand) / len(recent_demand) if recent_demand else 0
            desired_stock = round(forecast * expected_lead_time + safety_stock)
        else:
            desired_stock = self.target_stock

        order_quantity = max(desired_stock - self.inventory, 0)
        order = {
            "step": current_step,
            "warehouse_id": self.unique_id,
            "warehouse": self,
            "quantity": order_quantity,
        }
        self.manufacturer_order_history.append(order_quantity)
        manufacturer.receive_warehouse_order(order)
        return order_quantity
