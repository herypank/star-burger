from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist 

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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


@api_view(['POST'])
def register_order(request):
    order_serialized = request.data

    products_serialized = order_serialized.get('products', None)
    if isinstance(products_serialized, str) or not products_serialized:
        content = {'Error': 'invalid products. HTTP_400_BAD_REQUEST'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    products = []
    try:
        for product in products_serialized:
            products.append({
                'product': Product.objects.get(pk=product['product']),
                'quantity': product['quantity']
                })
    except (ObjectDoesNotExist, ValueError):
        content = {
            'Error': 'Cannot found product, invalid id. HTTP_400_BAD_REQUEST'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    first_name = order_serialized.get('firstname', None)
    if isinstance(first_name, list) or not first_name:
        content = {'Error': 'invalid firstname. HTTP_400_BAD_REQUEST'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    last_name = order_serialized.get('lastname', None)
    if isinstance(last_name, list) or not last_name:
        content = {'Error': 'invalid lastname. HTTP_400_BAD_REQUEST'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    phone_number = order_serialized.get('phonenumber', None)
    if isinstance(phone_number, list) or not phone_number:
        content = {'Error': 'invalid phonenumber. HTTP_400_BAD_REQUEST'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    order = Order.objects.get_or_create(
        delivery_address=order_serialized['address'],
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        )[0]
    for product in products:
        Products_In_Order.objects.create(
            product=product['product'],
            order=order,
            quantity=product['quantity'],
        )
    print(order_serialized)
    return Response(order_serialized)

