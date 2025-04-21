from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Customer, Product, Order, OrderItem
from .serializers import CustomerSerializer, ProductSerializer, OrderSerializer, OrderItemSerializer
from django.db.models import Q
from rest_framework.parsers import JSONParser
import datetime


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):  
    serializer_class = OrderSerializer
    parser_classes = [JSONParser]

    def get_queryset(self):
        queryset = Order.objects.all().prefetch_related('order_items', 'order_items__product')
        
        # Filter by customer name
        customer = self.request.query_params.get('customer', None)
        if customer:
            queryset = queryset.filter(customer__name__icontains=customer)
            
        # Filter by products (comma-separated list)
        products = self.request.query_params.get('products', None)
        if products:
            product_names = [name.strip() for name in products.split(',')]
            for product_name in product_names:
                queryset = queryset.filter(order_items__product__name__icontains=product_name)
                
        return queryset
    
    def create(self, request, *args, **kwargs):
        # Parse date in DD/MM/YYYY format if provided
        data = request.data.copy()
        if isinstance(data.get('order_date'), str) and '/' in data.get('order_date', ''):
            try:
                day, month, year = data['order_date'].split('/')
                data['order_date'] = f"{year}-{month}-{day}"
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        # Parse date in DD/MM/YYYY format if provided
        data = request.data.copy()
        if isinstance(data.get('order_date'), str) and '/' in data.get('order_date', ''):
            try:
                day, month, year = data['order_date'].split('/')
                data['order_date'] = f"{year}-{month}-{day}"
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
