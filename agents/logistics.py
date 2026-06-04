"""Logistics component skeleton."""

from dataclasses import dataclass, field


@dataclass
class LogisticsAgent:
    unique_id: str
    shipments: list[dict] = field(default_factory=list)
    delivered_shipments: list[dict] = field(default_factory=list)

    def create_shipment(
        self,
        origin: object,
        destination: object,
        quantity: int,
        departure_step: int,
        lead_time: int,
    ) -> dict:
        shipment = {
            "origin": origin,
            "destination": destination,
            "quantity": quantity,
            "departure_step": departure_step,
            "arrival_step": departure_step + lead_time,
            "delivered": False,
        }
        self.shipments.append(shipment)
        return shipment

    def update_shipments(self, current_step: int) -> list[dict]:
        due_shipments = [
            shipment
            for shipment in self.shipments
            if not shipment["delivered"] and shipment["arrival_step"] <= current_step
        ]
        self.shipments = [shipment for shipment in self.shipments if shipment not in due_shipments]
        return due_shipments

    def deliver(self, shipments: list[dict]) -> int:
        delivered_quantity = 0
        for shipment in shipments:
            shipment["destination"].receive_shipment(int(shipment["quantity"]))
            shipment["delivered"] = True
            self.delivered_shipments.append(shipment)
            delivered_quantity += int(shipment["quantity"])
        return delivered_quantity
