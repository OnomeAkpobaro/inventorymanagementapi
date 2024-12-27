from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
# Create your models here.
User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
class InventoryItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - Qty: {self.quantity}"

class InventoryChange(models.Model):
    TYPES = (
        ('ADD', 'Stock Added'),
        ('REMOVE', 'Stock Removed'),
        ('ADJUST', 'Stock Adjusted'),
    )

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='changes')
    change_type = models.CharField(max_length=6, choices=TYPES)
    quantity_change = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.item.name} - {self.change_type}: {self.quantity_change}"
