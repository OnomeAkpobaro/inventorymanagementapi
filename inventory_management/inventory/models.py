from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

#Get the active User model as specified in settings.py
User = get_user_model()


class Supplier(models.Model):
    """
    Represents product suppliers with contact details and status tracking.

    Relationships:
    - Created by a User (ForeignKey)
    - Has many InventoryItems
    """
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    """
    Product categories for organizing inventory item

    Relationship:
    - Has many inventoryItems

    Meta:
    - Sets plural name to "Categories" for admin interface
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
class InventoryItem(models.Model):
    """
    Core inventory item representing products in stock.

    Relationship:
    - Belongs to a Category (ForeignKey)
    - Created by a User (ForeignKey)
    - Supplied by a Supplier (ForeignKey)
    - Has many InventoryChanges
    - Associated with multiple stores through StoreInventory
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='items')
    # barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)

    
    def __str__(self):
        return f"{self.name} - Qty: {self.quantity}"

class InventoryChange(models.Model):
    """
    Tracks all changes to inventory item quantities

    Relationship:
    - Belongs to an InventoryItem (ForeignKey)
    - Changed by a User (ForeignKey)
    """
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
    

    
class Store(models.Model):
    """
    Represents physical store locations

    Relationship:
    - Created by a User (ForeginKey)
    - Has many InventoryItems through StoreInventory
    - Has many InventoryAlerts
    """
    name = models.CharField(max_length=200)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name
    
        
    
class StoreInventory(models.Model):
    """
    Manages inventory levels for items at specific stores.
    Includes stock monitoring and reordering Logic

    Relationship:
    - Belongs to a store (ForeignKey)
    - References a InventoryItem (ForeignKey)

    Properties:
    - is_low_stock: Returnsn True if quantity less than or equal to low_stock_threshold
    - needs_reorder: Returns Ture if quantity less than or equal to reorder_point

    Meta:
    - Ensures unique conbination of store and item
    - Sets plural name for admin interface

    """
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    reorder_point = models.IntegerField(default=20)
    reorder_quantity = models.IntegerField(default=50)

    class Meta:
        unique_together = ['store', 'item']
        verbose_name_plural = 'Store Inventories'

    def __str__(self):
            return f"{self.store.name} - {self.item.name}"
    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold
    @property
    def needs_reorder(self):
        return self.quantity <= self.reorder_point
    
    
class InventoryAlert(models.Model):
    """
    Manages inventory-related alerts for stores.

    Relationship:
    - Belongs to a store (ForeginKey)
    - References an InventoryItem (ForeignKey)

    Meta: 
    - Orders alerts by created_at in desending order
    """
    ALERT_TYPES = (
        ('LOW_STOCK', 'Low Stock Alert'),
        ('REORDER','Reorder Suggestion'),
        ('EXPIRY', 'Expiry Alert'),
    )


    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.alert_type} - {self.item.name} at {self.store.name}"
    


