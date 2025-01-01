from rest_framework import serializers
from .models import Category, InventoryChange, InventoryItem

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
        
