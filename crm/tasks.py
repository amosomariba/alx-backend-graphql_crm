from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(url='http://localhost:8000/graphql', verify=True, retries=3)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    query {
        customers { id }
        orders { id totalAmount }
    }
    """)
    response = client.execute(query)

    total_customers = len(response["customers"])
    total_orders = len(response["orders"])
    total_revenue = sum(order["totalAmount"] for order in response["orders"])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue"

    with open("/tmp/crm_report_log.txt", "a") as f:
        f.write(report + "\n")

    print("Weekly CRM Report Generated.")
