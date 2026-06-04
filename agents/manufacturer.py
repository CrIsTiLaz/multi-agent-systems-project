"""Manufacturer agent skeleton."""

from dataclasses import dataclass, field


@dataclass
class ManufacturerAgent:
    unique_id: str
    daily_capacity: int
    production_backlog: list[dict] = field(default_factory=list)
    completed_production: list[int] = field(default_factory=list)
    orders_received: list[dict] = field(default_factory=list)
    shipments_sent: list[int] = field(default_factory=list)

    def receive_warehouse_order(self, order: dict) -> None:
        self.orders_received.append(order.copy())
        self.production_backlog.append(order.copy())

    def produce(
        self,
        logistics: object,
        current_step: int,
        lead_time: int,
    ) -> dict[str, int]:
        remaining_capacity = self.daily_capacity
        produced_total = 0
        remaining_backlog: list[dict] = []

        for order in self.production_backlog:
            if remaining_capacity <= 0:
                remaining_backlog.append(order)
                continue

            quantity = int(order["quantity"])
            produced = min(quantity, remaining_capacity)
            remaining_capacity -= produced
            produced_total += produced

            if produced > 0:
                self.completed_production.append(produced)
                self.shipments_sent.append(produced)
                logistics.create_shipment(
                    origin=self,
                    destination=order["warehouse"],
                    quantity=produced,
                    departure_step=current_step,
                    lead_time=lead_time,
                )

            shortage = quantity - produced
            if shortage > 0:
                order["quantity"] = shortage
                remaining_backlog.append(order)

        self.production_backlog = remaining_backlog

        return {
            "produced": produced_total,
            "backlog": sum(int(order["quantity"]) for order in self.production_backlog),
        }
