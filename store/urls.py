from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, BasketViewSet, OrderViewSet, OrderItemViewSet, CouponViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'baskets', BasketViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'coupons', CouponViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('baskets/<int:pk>/add-to-basket/', BasketViewSet.as_view({'post': 'add_to_basket'}), name='add-to-basket'),
    path('baskets/<int:pk>/create-order/', BasketViewSet.as_view({'post': 'create_order'}), name='create-order'),
    path('orders/<int:pk>/apply-coupon/', OrderViewSet.as_view({'post': 'apply_coupon'}), name='apply-coupon'),
    path('orders/<int:pk>/mark-as-paid/', OrderViewSet.as_view({'post': 'mark_as_paid'}), name='mark-as-paid'),
    path('orders/<int:pk>/mark-as-received/', OrderViewSet.as_view({'post': 'mark_as_received'}), name='mark-as-received'),
]
