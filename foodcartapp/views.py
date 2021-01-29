from django.http import JsonResponse
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.serializers import CharField, IntegerField, ListField

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


class ProductsSerializer(Serializer):
    product = IntegerField(min_value=1)
    quantity = IntegerField(min_value=1)

    def validate_product(self, value):
        try:
            Product.objects.get(pk=value)
        except ObjectDoesNotExist:
            raise ValidationError('Error Cannot found product, invalid id.')
        return value


class ApplicationSerializer(ModelSerializer):
    products = ListField(
        child=ProductsSerializer()
    )

    class Meta:
        model = Order
        fields = [
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products'
            ]

    def validate_products(self, value):
        if not value:
            raise ValidationError('Ошибка пустой список продуктов')
        return value


@api_view(['POST'])
def register_order(request):
    serializer = ApplicationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    products = serializer.validated_data['products']
    order = Order.objects.get_or_create(
        address=serializer.validated_data['address'],
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        )[0]

    for product in products:
        Products_In_Order.objects.create(
            product=Product.objects.get(pk=product['product']),
            order=order,
            quantity=product['quantity'],
        )
    return Response(serializer.validated_data)
