from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime


class Customer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(0.01, message="Weight must be positive"),
            MaxValueValidator(25.00, message="Weight cannot exceed 25kg")
        ]
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    order_number = models.CharField(max_length=10, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateField()
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate order number if it doesn't exist
        if not self.order_number:
            # Get the latest order number
            last_order = Order.objects.order_by('-id').first()
            if last_order:
                last_id = last_order.id
            else:
                last_id = 0
            # Create new order number
            self.order_number = f'ORD{(last_id + 1):05d}'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number
    
    @property
    def total_weight(self):
        total = 0
        for item in self.order_items.all():
            total += item.product.weight * item.quantity
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
