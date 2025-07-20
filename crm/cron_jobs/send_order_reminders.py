#!/usr/bin/env python3

import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from pathlib import Path

# Define GraphQL client
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date 7 days ago
seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).date()

# GraphQL query for recent orders
query = gql(
    """
    query GetRecentOrders($fromDate: Date!) {
      orders(orderDate_Gte: $fromDate) {
        id
        customer {
          email
        }
      }
    }
    """
)

variables = {"fromDate": str(seven_days_ago)}

try:
    response = client.execute(query, variable_values=variables)
    orders = response.get("orders", [])

    log_file = Path("/tmp/order_reminders_log.txt")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with log_file.open("a") as f:
        for order in orders:
            log_line = f"{timestamp} - Order ID: {order['id']}, Customer Email: {order['customer']['email']}"
            print(log_line)
            f.write(log_line + "\n")

    print("Order reminders processed!")

except Exception as e:
    print(f"Failed to fetch or log orders: {e}")
