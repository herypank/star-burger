from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

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


def validate(order_serialized):
    errors = []
    products = []
    products_serialized = order_serialized.get('products', None)

    if isinstance(products_serialized, str) or not products_serialized:
        errors.append('Error invalid products.')
    else:
        try:
            for product in products_serialized:
                products.append({
                    'product': Product.objects.get(pk=product['product']),
                    'quantity': product['quantity']
                    })
        except (ObjectDoesNotExist, ValueError):
            errors.append('Error Cannot found product, invalid id.')

    first_name = order_serialized.get('firstname', None)
    if isinstance(first_name, list) or not first_name:
        errors.append('Error invalid firstname.')

    last_name = order_serialized.get('lastname', None)
    if isinstance(last_name, list) or not last_name:
        errors.append('Error invalid lastname.')

    phone_number = order_serialized.get('phonenumber', None)
    if isinstance(phone_number, list) or not phone_number:
        errors.append('Error invalid phonenumber.')

    if errors:
        raise ValidationError(errors)

    return products, first_name, last_name, phone_number


@api_view(['POST'])
def register_order(request):
    order_serialized = request.data
    products, first_name, last_name, phone_number = validate(order_serialized)

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
