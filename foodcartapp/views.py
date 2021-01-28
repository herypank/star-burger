from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.postgres.fields import ArrayField

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.serializers import Serializer
from rest_framework.serializers import CharField, ListField

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


class ApplicationSerializer(Serializer):
    firstname = CharField()
    lastname = CharField()
    phonenumber = CharField()
    products = ListField()

    def validate_products(self, value):
        try:
            for product in value:
                    Product.objects.get(pk=product['product'])
        except (ObjectDoesNotExist, ValueError):
            raise ValidationError('Error Cannot found product, invalid id.')
        return value


@api_view(['POST'])
def register_order(request):
    order_serialized = request.data
    serializer = ApplicationSerializer(data=order_serialized)
    serializer.is_valid(raise_exception=True)  # выкинет ValidationError

    order = Order.objects.get_or_create(
        delivery_address=order_serialized['address'],
        first_name=order_serialized['firstname'],
        last_name=order_serialized['lastname'],
        phone_number=order_serialized['phonenumber'],
        )[0]
    for product in order_serialized['products']:
        Products_In_Order.objects.create(
            product=Product.objects.get(pk=product['product']),
            order=order,
            quantity=product['quantity'],
        )
    print(order_serialized)
    return Response(order_serialized)
