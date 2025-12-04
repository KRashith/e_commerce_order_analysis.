from django.db import models

class Order(models.Model):
    order_id = models.CharField(max_length=100)
    order_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    product = models.CharField(max_length=200, default="Unknown Product")
    payment = models.CharField(max_length=100, blank=True)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0.0)

    @property
    def total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.order_id} - {self.product or 'Product'}"
