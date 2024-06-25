from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Product, Basket, BasketItem, Order, OrderItem, Coupon
from .serializers import ProductSerializer, BasketSerializer, BasketItemSerializer, OrderSerializer, OrderItemSerializer, CouponSerializer, CreateOrderSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class BasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

    @action(detail=True, methods=['post'])
    def add_to_basket(self, request, pk=None):
        basket = self.get_object()
        product = get_object_or_404(Product, id=request.data['product_id'])
        quantity = request.data.get('quantity', 1)
        if product.inventory_count < quantity:
            return Response({'detail': 'Insufficient inventory'}, status=status.HTTP_400_BAD_REQUEST)
        basket_item, created = BasketItem.objects.get_or_create(
            basket=basket,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            basket_item.quantity += quantity
            basket_item.save()
        return Response({'detail': 'Item added to basket'})

    @action(detail=True, methods=['post'])
    def create_order(self, request, pk=None):
        basket = self.get_object()
        if basket.items.count() == 0:
            return Response({'detail': 'Basket is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        order_data = {
            'user': basket.user.id,
            'total_amount': basket.total_price()
        }
        order_serializer = CreateOrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order = order_serializer.save()
            for item in basket.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.get_effective_price(),
                    quantity=item.quantity
                )
            basket.items.all().delete()
            return Response(OrderSerializer(order).data)
        return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def apply_coupon(self, request, pk=None):
        order = self.get_object()
        code = request.data.get('code')
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.apply_coupon()
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        order = self.get_object()
        order.mark_as_paid()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_as_received(self, request, pk=None):
        order = self.get_object()
        order.mark_as_received()
        serializer = self.get_serializer(order)
        return Response(serializer.data)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
