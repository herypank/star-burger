from django.http import JsonResponse
from django.templatetags.static import static
import json

from .models import Product
from .models import Order
from .models import Products_In_Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    decoded_order = json.loads(request.body.decode())
    order = Order.objects.get_or_create(
        delivery_address=decoded_order['address'],
        first_name=decoded_order['firstname'],
        last_name=decoded_order['lastname'],
        phone_number=decoded_order["phonenumber"],
        )[0]
    for product in decoded_order['products']:
        Products_In_Order.objects.create(
            product=Product.objects.get(pk=product['product']),
            order=order,
            quantity=product['quantity'],
        )
    return JsonResponse({})
