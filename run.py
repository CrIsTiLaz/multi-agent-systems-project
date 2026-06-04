"""Run the supply chain simulation."""

from analysis import run_baseline, run_experiments, write_report
from visualization import generate_plots


def main() -> None:
    metrics, baseline_summary = run_baseline()
    experiment_summaries = run_experiments()
    write_report(baseline_summary, experiment_summaries)
    generated_plots = generate_plots(metrics)
    final_metrics = metrics[-1] if metrics else {}

    print("Supply chain simulation")
    print(f"Steps run: {final_metrics.get('step', 0)}")
    print(f"Customers: {final_metrics.get('customers', 0)}")
    print(f"Retailers: {final_metrics.get('retailers', 0)}")
    print(f"Warehouses: {final_metrics.get('warehouses', 0)}")
    print(f"Manufacturers: {final_metrics.get('manufacturers', 0)}")
    print(f"Final step customer demand: {final_metrics.get('customer_demand', 0)}")
    print(f"Final step fulfilled demand: {final_metrics.get('customer_fulfilled', 0)}")
    print(f"Final step unfulfilled demand: {final_metrics.get('customer_unfulfilled', 0)}")
    print(f"Retailer inventory: {final_metrics.get('retailer_inventory', 0)}")
    print(f"Retailer stockouts: {final_metrics.get('retailer_stockouts', 0)}")
    print(f"Warehouse inventory: {final_metrics.get('warehouse_inventory', 0)}")
    print(
        "Final step retailer replenishment order quantity: "
        f"{final_metrics.get('retailer_replenishment_order_quantity', 0)}"
    )
    print(f"Final step warehouse shipments to retailers: {final_metrics.get('warehouse_retailer_shipments', 0)}")
    print(
        "Final step warehouse order to manufacturer: "
        f"{final_metrics.get('warehouse_manufacturer_order_quantity', 0)}"
    )
    print(f"Final step manufacturer production: {final_metrics.get('manufacturer_production_quantity', 0)}")
    print(f"Manufacturer backlog: {final_metrics.get('manufacturer_backlog', 0)}")
    print(f"In-transit shipments: {final_metrics.get('in_transit_shipments', 0)}")
    print(f"In-transit quantity: {final_metrics.get('in_transit_quantity', 0)}")
    print(f"Delivered quantity this step: {final_metrics.get('delivered_quantity', 0)}")
    print(f"Pending customer orders: {final_metrics.get('pending_customer_orders', 0)}")
    print(
        "Warehouse incoming retailer orders: "
        f"{final_metrics.get('warehouse_incoming_retailer_orders', 0)}"
    )
    print(f"Service level: {baseline_summary.get('service_level', 0):.3f}")
    print(f"Stockout rate: {baseline_summary.get('stockout_rate', 0):.3f}")
    print(f"Retailer bullwhip ratio: {baseline_summary.get('retailer_bullwhip_ratio', 0):.3f}")
    print(f"Warehouse bullwhip ratio: {baseline_summary.get('warehouse_bullwhip_ratio', 0):.3f}")
    print("Saved data: results/data/")
    print("Saved report: results/report.md")
    if generated_plots:
        print("Saved plots: results/plots/")
    else:
        print("Plots skipped: install matplotlib to generate PNG files.")
    print("Step order:")
    for index, action in enumerate(
        (
            "customers_generate_demand",
            "retailers_process_customer_orders",
            "retailers_place_replenishment_orders",
            "warehouses_process_retailer_orders",
            "warehouses_place_manufacturer_orders",
            "manufacturers_produce",
            "logistics_update_shipments",
            "deliveries_increase_inventory",
            "metrics_collected",
        ),
        start=1,
    ):
        print(f"{index}. {action}")


if __name__ == "__main__":
    main()
