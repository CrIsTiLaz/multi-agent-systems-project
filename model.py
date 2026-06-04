"""Supply chain model skeleton."""

from __future__ import annotations

import random
from typing import Any

from agents.customer import CustomerAgent
from agents.logistics import LogisticsAgent
from agents.manufacturer import ManufacturerAgent
from agents.retailer import RetailerAgent
from agents.warehouse import WarehouseAgent
from config import DEFAULT_CONFIG, SimulationConfig

try:
    from mesa import Model as MesaModel
except ImportError:  # Allows the skeleton to run before dependencies are installed.
    MesaModel = object


class SupplyChainModel(MesaModel):
    """Minimal model that owns agents and enforces the documented step order."""

    step_order = (
        "customers_generate_demand",
        "retailers_process_customer_orders",
        "retailers_place_replenishment_orders",
        "warehouses_process_retailer_orders",
        "warehouses_place_manufacturer_orders",
        "manufacturers_produce",
        "logistics_update_shipments",
        "deliveries_increase_inventory",
        "metrics_collected",
    )

    def __init__(self, config: SimulationConfig = DEFAULT_CONFIG) -> None:
        if MesaModel is not object:
            super().__init__()

        self.config = config
        self.current_step = 0
        self.random = random.Random(config.random_seed)
        self.metrics: list[dict[str, Any]] = []

        self.retailers = [
            RetailerAgent(
                unique_id=f"retailer-{index + 1}",
                inventory=config.retailer_initial_inventory,
                reorder_point=config.retailer_reorder_point,
                target_stock=config.retailer_target_stock,
            )
            for index in range(config.retailer_count)
        ]
        self.warehouses = [
            WarehouseAgent(
                unique_id=f"warehouse-{index + 1}",
                inventory=config.warehouse_initial_inventory,
                reorder_point=config.warehouse_reorder_point,
                target_stock=config.warehouse_target_stock,
            )
            for index in range(config.warehouse_count)
        ]
        self.manufacturers = [
            ManufacturerAgent(
                unique_id=f"manufacturer-{index + 1}",
                daily_capacity=config.manufacturer_daily_capacity,
            )
            for index in range(config.manufacturer_count)
        ]
        self.logistics = LogisticsAgent(unique_id="logistics-1")
        self.customers = [
            CustomerAgent(
                unique_id=f"customer-{index + 1}",
                assigned_retailer=self.retailers[index % len(self.retailers)],
            )
            for index in range(config.customer_count)
        ]

    def step(self) -> None:
        """Advance one simulation day."""

        self.current_step += 1
        total_customer_demand = self._customers_generate_demand()
        retailer_order_metrics = self._retailers_process_customer_orders()
        retailer_replenishment_quantity = self._retailers_place_replenishment_orders()
        warehouse_order_metrics = self._warehouses_process_retailer_orders()
        warehouse_manufacturer_order_quantity = self._warehouses_place_manufacturer_orders()
        manufacturer_metrics = self._manufacturers_produce()
        due_shipments = self._logistics_update_shipments()
        delivered_quantity = self._deliveries_increase_inventory(due_shipments)
        self._collect_metrics(
            customer_demand=total_customer_demand,
            customer_fulfilled=retailer_order_metrics["fulfilled"],
            customer_unfulfilled=retailer_order_metrics["unfulfilled"],
            retailer_replenishment_order_quantity=retailer_replenishment_quantity,
            warehouse_retailer_shipments=warehouse_order_metrics["shipped"],
            warehouse_unfilled_retailer_orders=warehouse_order_metrics["unfilled"],
            warehouse_manufacturer_order_quantity=warehouse_manufacturer_order_quantity,
            manufacturer_production_quantity=manufacturer_metrics["produced"],
            manufacturer_backlog=manufacturer_metrics["backlog"],
            delivered_quantity=delivered_quantity,
        )

    def run(self, steps: int | None = None) -> list[dict[str, Any]]:
        """Run the model and return collected metrics."""

        total_steps = steps if steps is not None else self.config.simulation_steps
        for _ in range(total_steps):
            self.step()
        return self.metrics

    def _collect_metrics(
        self,
        customer_demand: int,
        customer_fulfilled: int,
        customer_unfulfilled: int,
        retailer_replenishment_order_quantity: int,
        warehouse_retailer_shipments: int,
        warehouse_unfilled_retailer_orders: int,
        warehouse_manufacturer_order_quantity: int,
        manufacturer_production_quantity: int,
        manufacturer_backlog: int,
        delivered_quantity: int,
    ) -> None:
        self.metrics.append(
            {
                "step": self.current_step,
                "customers": len(self.customers),
                "retailers": len(self.retailers),
                "warehouses": len(self.warehouses),
                "manufacturers": len(self.manufacturers),
                "in_transit_shipments": len(self.logistics.shipments),
                "pending_customer_orders": sum(
                    len(retailer.pending_customer_orders) for retailer in self.retailers
                ),
                "customer_demand": customer_demand,
                "customer_fulfilled": customer_fulfilled,
                "customer_unfulfilled": customer_unfulfilled,
                "retailer_stockouts": sum(retailer.stockout_count for retailer in self.retailers),
                "retailer_inventory": sum(retailer.inventory for retailer in self.retailers),
                "average_retailer_inventory": (
                    sum(retailer.inventory for retailer in self.retailers) / len(self.retailers)
                ),
                "retailer_replenishment_order_quantity": retailer_replenishment_order_quantity,
                "pending_retailer_replenishment_orders": sum(
                    len(retailer.pending_replenishment_orders) for retailer in self.retailers
                ),
                "warehouse_incoming_retailer_orders": sum(
                    len(warehouse.incoming_retailer_orders) for warehouse in self.warehouses
                ),
                "warehouse_inventory": sum(warehouse.inventory for warehouse in self.warehouses),
                "average_warehouse_inventory": (
                    sum(warehouse.inventory for warehouse in self.warehouses) / len(self.warehouses)
                ),
                "warehouse_retailer_shipments": warehouse_retailer_shipments,
                "warehouse_unfilled_retailer_orders": warehouse_unfilled_retailer_orders,
                "warehouse_manufacturer_order_quantity": warehouse_manufacturer_order_quantity,
                "manufacturer_production_quantity": manufacturer_production_quantity,
                "manufacturer_backlog": manufacturer_backlog,
                "delivered_quantity": delivered_quantity,
                "delivered_shipments": len(self.logistics.delivered_shipments),
                "in_transit_quantity": sum(
                    int(shipment["quantity"]) for shipment in self.logistics.shipments
                ),
                "holding_cost": (
                    sum(retailer.inventory for retailer in self.retailers)
                    * self.config.retailer_holding_cost_per_unit
                    + sum(warehouse.inventory for warehouse in self.warehouses)
                    * self.config.warehouse_holding_cost_per_unit
                ),
                "service_level": (
                    customer_fulfilled / customer_demand if customer_demand > 0 else 1.0
                ),
                "stockout_rate": (
                    customer_unfulfilled / customer_demand if customer_demand > 0 else 0.0
                ),
            }
        )

    def _customers_generate_demand(self) -> int:
        return sum(
            customer.generate_demand(
                current_step=self.current_step,
                rng=self.random,
                min_demand=self.config.customer_min_demand,
                max_demand=self.config.customer_max_demand,
            )
            for customer in self.customers
        )

    def _retailers_process_customer_orders(self) -> dict[str, int]:
        totals = {"requested": 0, "fulfilled": 0, "unfulfilled": 0}
        for retailer in self.retailers:
            result = retailer.process_customer_orders()
            totals["requested"] += result["requested"]
            totals["fulfilled"] += result["fulfilled"]
            totals["unfulfilled"] += result["unfulfilled"]
        return totals

    def _retailers_place_replenishment_orders(self) -> int:
        warehouse = self.warehouses[0]
        return sum(
            retailer.place_replenishment_order(
                warehouse=warehouse,
                current_step=self.current_step,
                policy=self.config.inventory_policy,
                expected_lead_time=self.config.retailer_lead_time,
                safety_stock=self.config.safety_stock,
                forecasting_window=self.config.forecasting_window,
            )
            for retailer in self.retailers
        )

    def _warehouses_process_retailer_orders(self) -> dict[str, int]:
        totals = {"requested": 0, "shipped": 0, "unfilled": 0}
        for warehouse in self.warehouses:
            result = warehouse.process_retailer_orders(
                logistics=self.logistics,
                current_step=self.current_step,
                lead_time=self.config.retailer_lead_time,
            )
            totals["requested"] += result["requested"]
            totals["shipped"] += result["shipped"]
            totals["unfilled"] += result["unfilled"]
        return totals

    def _warehouses_place_manufacturer_orders(self) -> int:
        manufacturer = self.manufacturers[0]
        return sum(
            warehouse.place_manufacturer_order(
                manufacturer=manufacturer,
                current_step=self.current_step,
                policy=self.config.inventory_policy,
                expected_lead_time=self.config.warehouse_lead_time,
                safety_stock=self.config.safety_stock,
                forecasting_window=self.config.forecasting_window,
            )
            for warehouse in self.warehouses
        )

    def _manufacturers_produce(self) -> dict[str, int]:
        totals = {"produced": 0, "backlog": 0}
        for manufacturer in self.manufacturers:
            result = manufacturer.produce(
                logistics=self.logistics,
                current_step=self.current_step,
                lead_time=self.config.warehouse_lead_time,
            )
            totals["produced"] += result["produced"]
            totals["backlog"] += result["backlog"]
        return totals

    def _logistics_update_shipments(self) -> list[dict]:
        return self.logistics.update_shipments(current_step=self.current_step)

    def _deliveries_increase_inventory(self, due_shipments: list[dict]) -> int:
        return self.logistics.deliver(due_shipments)
