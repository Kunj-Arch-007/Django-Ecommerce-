# E-Commerce API

A RESTful API for managing customers, products, and orders built with Django REST Framework.

## Features

- Customer management
- Product catalog with weight specifications
- Order management with automatic order number generation
- Validation for product weight and order total weight
- Filtering orders by customer name and products

## API Endpoints

### Customers
- List all customers: `GET /api/customers/`
- Create a new customer: `POST /api/customers/`
- Update existing customer: `PUT /api/customers/<id>/`

### Products
- List all products: `GET /api/products/`
- Create a new product: `POST /api/products/`

### Orders
- List all orders: `GET /api/orders/`
- Create a new order: `POST /api/orders/`
- Edit existing order: `PUT /api/orders/<id>/`
- Filter orders by products: `GET /api/orders/?products=Book,Pen`
- Filter orders by customer: `GET /api/orders/?customer=Sam`

## Installation & Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Start the development server: `python manage.py runserver`

## Usage Examples

### Creating a Customer
```json
POST /api/customers/
{
    "name": "John Doe",
    "contact_number": "+1234567890",
    "email": "john@example.com"
}
```

### Creating a Product
```json
POST /api/products/
{
    "name": "Laptop",
    "weight": 2.5
}
```

### Creating an Order
```json
POST /api/orders/
{
    "customer": 1,
    "order_date": "2023-12-31",
    "address": "123 Main St, Cityville",
    "order_item": [
        {
            "product": 1,
            "quantity": 2
        },
        {
            "product": 3,
            "quantity": 1
        }
    ]
}
``` 