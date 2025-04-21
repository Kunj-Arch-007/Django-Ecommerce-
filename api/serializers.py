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
        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'weight']

    def validate_name(self, value):
        return value

    def validate_weight(self, value):
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
        if value < date.today():
            raise serializers.ValidationError("Order date cannot be in the past.")
        return value

    def validate(self, data):
        if self.instance:
            order_items = data.get('order_item', [])
        else:
            order_items = data.get('order_item', [])
            if not order_items:
                raise serializers.ValidationError({"order_item": "At least one product is required."})

        total_weight = Decimal('0.0')
        products = []

        for item in order_items:
            product = item['product']
            quantity = item['quantity']
            
            if product in products:
                raise serializers.ValidationError({"order_item": f"Product '{product.name}' appears multiple times. Please consolidate quantities."})
            products.append(product)
            
            total_weight += product.weight * Decimal(str(quantity))

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
        instance.customer = validated_data.get('customer', instance.customer)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        if 'order_item' in validated_data:
            instance.order_items.all().delete()
            
            for item_data in validated_data.get('order_item'):
                OrderItem.objects.create(order=instance, **item_data)

        return instance 