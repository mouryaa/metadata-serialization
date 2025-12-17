"""
Custom Faker provider for Schema.org/Order properties.
Generates realistic data for e-commerce orders.
"""

from faker import Faker
from faker.providers import BaseProvider
from .base_provider import BaseSchemaOrgProvider
from datetime import datetime, timedelta
import random


class SchemaOrgOrderProvider(BaseSchemaOrgProvider):
    """Provider for Schema.org/Order properties."""
    
    # Order-specific data
    ORDER_STATUSES = [
        "OrderProblem",
        "OrderProcessing",
        "OrderInTransit",
        "OrderDelivered",
        "OrderPickupAvailable",
        "OrderReturned",
        "OrderCancelled"
    ]
    
    PAYMENT_METHODS = [
        "Credit Card",
        "Debit Card",
        "PayPal",
        "Bank Transfer",
        "Cash on Delivery",
        "Apple Pay",
        "Google Pay",
        "Amazon Pay",
        "Cryptocurrency"
    ]
    
    PAYMENT_STATUSES = [
        "PaymentAutomaticallyApplied",
        "PaymentComplete",
        "PaymentDeclined",
        "PaymentDue",
        "PaymentPastDue"
    ]
    
    DELIVERY_METHODS = [
        "Standard Shipping",
        "Express Shipping",
        "Overnight Shipping",
        "International Shipping",
        "In-Store Pickup",
        "Curbside Pickup",
        "Same Day Delivery"
    ]
    
    PRODUCT_CATEGORIES = [
        "Electronics", "Clothing", "Books", "Home & Garden", "Toys",
        "Sports Equipment", "Jewelry", "Automotive", "Beauty Products",
        "Food & Beverages", "Office Supplies", "Pet Supplies", "Health"
    ]
    
    def order_identifier(self):
        """Order identifier/number."""
        prefix = random.choice(["ORD", "PO", "INV"])
        number = random.randint(100000, 999999)
        return f"{prefix}-{number}"
    
    def order_confirmation_number(self):
        """Order confirmation number."""
        return f"CONF-{random.randint(1000000, 9999999)}"
    
    def order_status(self):
        """Order status."""
        return random.choice(self.ORDER_STATUSES)
    
    def order_date(self):
        """Date order was placed."""
        start_date = datetime.now() - timedelta(days=365)
        end_date = datetime.now()
        date = self.fake.date_between(start_date=start_date, end_date=end_date)
        return date.isoformat()
    
    def order_delivery_date(self, order_date_str=None):
        """Expected or actual delivery date."""
        if order_date_str:
            try:
                order_date = datetime.fromisoformat(order_date_str)
                # Delivery 1-30 days after order
                delivery_date = order_date + timedelta(days=random.randint(1, 30))
                return delivery_date.isoformat()
            except:
                pass
        
        # Fallback
        start_date = datetime.now() - timedelta(days=300)
        end_date = datetime.now() + timedelta(days=30)
        date = self.fake.date_between(start_date=start_date, end_date=end_date)
        return date.isoformat()
    
    def order_customer_name(self):
        """Customer name."""
        return self.fake.name()
    
    def order_customer_email(self):
        """Customer email."""
        return self.common_email()
    
    def order_customer_telephone(self):
        """Customer telephone."""
        return self.common_telephone()
    
    def order_billing_address(self):
        """Billing address."""
        return self.common_address()
    
    def order_shipping_address(self):
        """Shipping address."""
        # 70% same as billing, 30% different
        if random.random() < 0.7:
            return self.common_address()
        else:
            return self.common_address()
    
    def order_item_name(self):
        """Name of ordered item."""
        category = random.choice(self.PRODUCT_CATEGORIES)
        adjectives = self.fake.words(nb=2)
        return f"{' '.join(adjectives).title()} {category[:-1]}"
    
    def order_item_quantity(self):
        """Quantity of item."""
        # Most orders have 1-5 items
        weights = [0.4, 0.3, 0.15, 0.1, 0.05]
        quantities = [1, 2, 3, 4, 5]
        return random.choices(quantities, weights=weights)[0]
    
    def order_item_price(self):
        """Price per item."""
        return self.common_price(min_value=5, max_value=500)
    
    def order_subtotal(self):
        """Order subtotal (before tax and shipping)."""
        return self.common_price(min_value=10, max_value=2000)
    
    def order_tax(self, subtotal=None):
        """Tax amount."""
        if subtotal:
            tax_rate = random.uniform(0.05, 0.12)  # 5-12% tax
            return round(subtotal * tax_rate, 2)
        return self.common_price(min_value=1, max_value=200)
    
    def order_shipping_cost(self):
        """Shipping cost."""
        costs = [0, 4.99, 7.99, 9.99, 12.99, 15.99, 19.99, 25.00]
        return random.choice(costs)
    
    def order_discount(self):
        """Discount amount."""
        # Many orders have no discount
        if random.random() < 0.7:
            return 0
        return self.common_price(min_value=5, max_value=100)
    
    def order_total(self):
        """Order total amount."""
        return self.common_price(min_value=15, max_value=2500)
    
    def order_currency(self):
        """Currency code."""
        return self.common_currency_code()
    
    def order_payment_method(self):
        """Payment method used."""
        return random.choice(self.PAYMENT_METHODS)
    
    def order_payment_status(self):
        """Payment status."""
        return random.choice(self.PAYMENT_STATUSES)
    
    def order_delivery_method(self):
        """Delivery/shipping method."""
        return random.choice(self.DELIVERY_METHODS)
    
    def order_tracking_number(self):
        """Shipping tracking number."""
        carriers = ["1Z", "92", "94"]  # UPS, USPS, FedEx prefixes
        prefix = random.choice(carriers)
        number = ''.join(random.choices('0123456789', k=16))
        return f"{prefix}{number}"
    
    def order_merchant(self):
        """Merchant/seller name."""
        return self.fake.company()
    
    def order_merchant_url(self):
        """Merchant website."""
        return self.common_url()


def create_order_data(num_entities=10, seed=None):
    """
    Generate order data using the custom provider.
    
    Args:
        num_entities: Number of order entities to generate
        seed: Random seed for reproducibility
    
    Returns:
        List of dictionaries containing order data
    """
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    
    fake = Faker()
    fake.add_provider(SchemaOrgOrderProvider)
    
    orders = []
    
    for i in range(num_entities):
        order_date = fake.order_date()
        subtotal = fake.order_subtotal()
        tax = fake.order_tax(subtotal)
        shipping = fake.order_shipping_cost()
        discount = fake.order_discount()
        total = round(subtotal + tax + shipping - discount, 2)
        
        order = {
            "@type": "Order",
            "orderNumber": fake.order_identifier(),
            "orderStatus": fake.order_status(),
            "orderDate": order_date,
        }
        
        # Optional properties
        if random.random() < 0.8:
            order["confirmationNumber"] = fake.order_confirmation_number()
        
        if random.random() < 0.7:
            order["orderDelivery"] = {
                "expectedArrivalFrom": fake.order_delivery_date(order_date),
                "deliveryMethod": fake.order_delivery_method()
            }
        
        # Customer information
        order["customer"] = {
            "name": fake.order_customer_name(),
            "email": fake.order_customer_email()
        }
        
        if random.random() < 0.6:
            order["customer"]["telephone"] = fake.order_customer_telephone()
        
        # Addresses
        if random.random() < 0.9:
            order["billingAddress"] = fake.order_billing_address()
        
        if random.random() < 0.8:
            order["shippingAddress"] = fake.order_shipping_address()
        
        # Order items (simplified - 1-3 items)
        num_items = random.randint(1, 3)
        order["orderedItems"] = []
        for _ in range(num_items):
            item = {
                "name": fake.order_item_name(),
                "quantity": fake.order_item_quantity(),
                "price": fake.order_item_price()
            }
            order["orderedItems"].append(item)
        
        # Financial details
        order["priceSpecification"] = {
            "subtotal": subtotal,
            "tax": tax,
            "shippingCost": shipping,
            "total": total,
            "currency": fake.order_currency()
        }
        
        if discount > 0:
            order["priceSpecification"]["discount"] = discount
        
        # Payment
        order["paymentMethod"] = fake.order_payment_method()
        
        if random.random() < 0.8:
            order["paymentStatus"] = fake.order_payment_status()
        
        # Shipping
        if random.random() < 0.6:
            order["trackingNumber"] = fake.order_tracking_number()
        
        # Merchant
        if random.random() < 0.7:
            order["merchant"] = fake.order_merchant()
        
        if random.random() < 0.5:
            order["merchantUrl"] = fake.order_merchant_url()
        
        orders.append(order)
    
    return orders


if __name__ == "__main__":
    # Test the provider
    print("Testing Schema.org Order Provider\n")
    print("=" * 80)
    
    orders = create_order_data(num_entities=3, seed=42)
    
    for i, order in enumerate(orders, 1):
        print(f"\nOrder {i}:")
        print("-" * 80)
        for key, value in order.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    if isinstance(v, dict):
                        print(f"    {k}:")
                        for k2, v2 in v.items():
                            print(f"      {k2}: {v2}")
                    else:
                        print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    if isinstance(item, dict):
                        print(f"    - {item}")
                    else:
                        print(f"    - {item}")
            else:
                print(f"  {key}: {value}")



