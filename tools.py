import csv

ORDERS_FILE = "orders.csv"


def get_order_status(order_id: str) -> str:
    """Look up a KartEase order by its ID (like KE1002) and return its product,
    status, date and payment method. Use this for questions about where an
    order is or what its current status is."""
    order_id = order_id.strip().upper()
    with open(ORDERS_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["order_id"].upper() == order_id:
                return (
                    f"Order {row['order_id']}: {row['product']} | "
                    f"Status: {row['status']} | "
                    f"Order date: {row['order_date']} | "
                    f"Expected/delivered date: {row['expected_or_delivered_date'] or 'N/A'} | "
                    f"Payment method: {row['payment_method']}"
                )
    return f"No order found with ID {order_id}."