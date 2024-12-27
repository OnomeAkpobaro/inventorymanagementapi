from rest_framework import serializers
from .models import Category, InventoryChange, InventoryItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by_username', read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'description', 'quantity', 'price',
            'category', 'category_name', 'created_by_usernmae',
            'date_added', 'last_updated'
        ]
        read_only_fields = ['created_by', 'date_added', 'last_updated']

class InventoryChangeSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = InventoryChange
        fields = [
            'id', 'item', 'item_name', 'change_type',
            'quantity_change', 'previous_quantity', 'new_quantity',
            'changed_by', 'changed_by_username', 'timestamp', 'notes'
        ]
        read_only_fields = ['changed_by', 'timestamp']
        
