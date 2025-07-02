import re
import graphene
from django.db import transaction
from graphql import GraphQLError
from .models import Customer, Product, Order
from .types import CustomerType, ProductType, OrderType
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            raise GraphQLError("Email already exists.")
        if phone and not re.match(r'^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$', phone):
            raise GraphQLError("Invalid phone format.")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        with transaction.atomic():
            for i, data in enumerate(input):
                try:
                    if Customer.objects.filter(email=data['email']).exists():
                        raise ValueError(f"{data['email']} already exists.")
                    if 'phone' in data and data['phone'] and not re.match(r'^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$', data['phone']):
                        raise ValueError(f"Invalid phone format: {data['phone']}")
                    customer = Customer(name=data['name'], email=data['email'], phone=data.get('phone'))
                    customer.save()
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Error in record {i+1}: {str(e)}")

        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int()

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise GraphQLError("Price must be positive.")
        if stock < 0:
            raise GraphQLError("Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except ObjectDoesNotExist:
            raise GraphQLError("Invalid customer ID.")

        if not product_ids:
            raise GraphQLError("At least one product must be selected.")

        products = []
        total_amount = 0
        for pid in product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
                total_amount += float(product.price)
            except Product.DoesNotExist:
                raise GraphQLError(f"Invalid product ID: {pid}")

        order = Order(customer=customer, total_amount=total_amount, order_date=order_date or timezone.now())
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
