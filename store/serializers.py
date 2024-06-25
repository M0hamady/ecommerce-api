from rest_framework import serializers
from django.contrib.auth.models import User
from .models import KeyFeature, Product, Basket, BasketItem, Order, OrderItem, Coupon


class KeyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeyFeature
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    effective_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_effective_price(self, obj):
        return obj.get_effective_price()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Example: You can add more fields or manipulate existing ones here
        data['key_features'] = KeyFeatureSerializer(instance.key_features.all(), many=True).data
        return data

class BasketItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItem
        fields = ['product', 'quantity']

class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)

    class Meta:
        model = Basket
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user', 'total_amount']
