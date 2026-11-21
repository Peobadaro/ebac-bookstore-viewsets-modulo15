from django.contrib.auth.models import User
from rest_framework import serializers

from order.models import Order
from product.models import Product
from product.serializers import ProductSerializer


class OrderSerializer(serializers.ModelSerializer):
    # Leitura: os produtos aparecem completos (com as categorias).
    product = ProductSerializer(read_only=True, many=True)
    # Escrita: os produtos são informados pelos ids.
    products_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, many=True
    )
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "product", "products_id", "total"]

    def get_total(self, instance):
        return sum(product.price or 0 for product in instance.product.all())

    def validate_products_id(self, value):
        if not value:
            raise serializers.ValidationError("O pedido precisa ter pelo menos um produto.")
        return value

    def create(self, validated_data):
        products = validated_data.pop("products_id")
        order = Order.objects.create(**validated_data)
        order.product.set(products)
        return order
