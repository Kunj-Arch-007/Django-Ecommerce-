from rest_framework import serializers
from .models import Customer, Product, Order, OrderItem
from django.utils import timezone
from datetime import date
from decimal import Decimal


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'contact_number', 'email']

    def validate_name(self, value):
        # Name uniqueness is already enforced by the model
        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'weight']

    def validate_name(self, value):
        # Name uniqueness is already enforced by the model
        return value

    def validate_weight(self, value):
        # Weight validation is already enforced by the model validators
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, required=False, read_only=True)
    order_item = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'customer', 'order_date', 'address', 'order_items', 'order_item']
        read_only_fields = ['order_number']

    def validate_order_date(self, value):
        # Ensure order date is not in the past
        if value < date.today():
            raise serializers.ValidationError("Order date cannot be in the past.")
        return value

    def validate(self, data):
        # If we're updating an existing order
        if self.instance:
            order_items = data.get('order_item', [])
        else:
            # For new order creation
            order_items = data.get('order_item', [])
            if not order_items:
                raise serializers.ValidationError({"order_item": "At least one product is required."})

        # Calculate total weight
        total_weight = Decimal('0.0')
        products = []

        for item in order_items:
            product = item['product']
            quantity = item['quantity']
            
            # Check if this product is already in the order
            if product in products:
                raise serializers.ValidationError({"order_item": f"Product '{product.name}' appears multiple times. Please consolidate quantities."})
            products.append(product)
            
            # Add to total weight
            total_weight += product.weight * Decimal(str(quantity))

        # Check total weight limit (150kg)
        if total_weight > Decimal('150.0'):
            raise serializers.ValidationError({"order_item": f"Total order weight ({total_weight}kg) exceeds the limit of 150kg."})

        return data

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_item')
        order = Order.objects.create(**validated_data)

        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        # Update order fields
        instance.customer = validated_data.get('customer', instance.customer)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        # Handle order items if they are provided
        if 'order_item' in validated_data:
            # Clear existing items
            instance.order_items.all().delete()
            
            # Create new items
            for item_data in validated_data.get('order_item'):
                OrderItem.objects.create(order=instance, **item_data)

        return instance 