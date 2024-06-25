from django.db import models

from api.models import User


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    inventory_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_effective_price(self):
        return self.offer_price if self.offer_price else self.price

class KeyFeature(models.Model):
    product = models.ForeignKey(Product, related_name='key_features', on_delete=models.CASCADE)
    feature_text = models.CharField(max_length=255)

    def __str__(self):
        return self.feature_text

class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Basket {self.id} - {self.user.username}"

    def total_items(self):
        return self.items.count()  # Calculate total items in basket

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Basket {self.basket.id}"

    def subtotal(self):
        return self.product.get_effective_price() * self.quantity


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)  # Discount as a percentage
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    received = models.BooleanField(default=False)  # Track order received status
    payment_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def apply_coupon(self):
        if self.coupon and self.coupon.is_active:
            discount_amount = (self.total_amount * self.coupon.discount) / 100
            self.total_amount -= discount_amount
            self.save()

    def mark_as_paid(self):
        self.paid = True
        self.payment_status = 'completed'
        self.save()

    def mark_as_received(self):
        self.received = True
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def subtotal(self):
        return self.price * self.quantity

    def update_inventory(self):
        if self.product.inventory_count >= self.quantity:
            self.product.inventory_count -= self.quantity
            self.product.save()
        else:
            raise ValueError("Insufficient inventory for this order item")

    def save(self, *args, **kwargs):
        self.update_inventory()
        self.price = self.product.get_effective_price()
        super().save(*args, **kwargs)
