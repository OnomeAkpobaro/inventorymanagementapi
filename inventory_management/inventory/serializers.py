from rest_framework import serializers
from .models import Category, InventoryChange, InventoryItem, Supplier, Store, InventoryAlert, StoreInventory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_username = serializers.CharField(read_only=True)

    class Meta:
        model = InventoryItem
        fields = "__all__"
        read_only_fields = ['created_by', 'date_added', 'last_updated']

class InventoryChangeSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = InventoryChange
        fields = "__all__"
        read_only_fields = ['changed_by', 'timestamp']
        
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_by']

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'contact_number', 'email', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_by']

class StoreInventorySerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = StoreInventory
        fields = ['id', 'store', 'store_name', 'item', 'item_name',
                  'quantity', 'low_stock_threshold', 'reorder_point', 'reorder_quantity', 'needs_reorder']
        
class InventoryAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAlert
        fields = ['id', 'store', 'item', 'alert_type', 'message', 'is_resolved', 'created_at', 'resolved_at']











