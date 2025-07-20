import datetime
from pathlib import Path
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    log_path = Path("/tmp/crm_heartbeat_log.txt")
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Optional: Ping the GraphQL hello query
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=False,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        query = gql("""query { hello }""")
        response = client.execute(query)
        message = response.get("hello", "GraphQL unreachable")
    except Exception:
        message = "GraphQL unreachable"

    with log_path.open("a") as log:
        log.write(f"{timestamp} CRM is alive - {message}\n")


def update_low_stock():
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
        mutation {
            updateLowStockProducts {
                updatedProducts {
                    name
                    stock
                }
                message
            }
        }
    """)

    response = client.execute(mutation)
    updated = response["updateLowStockProducts"]["updatedProducts"]
    message = response["updateLowStockProducts"]["message"]

    with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%d/%m/%Y-%H:%M:%S')} - {message}\n")
        for product in updated:
            log_file.write(f"Updated {product['name']} to stock {product['stock']}\n")