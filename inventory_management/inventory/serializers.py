from rest_framework import serializers
from .models import Category, InventoryChange, InventoryItem, Supplier, Store, InventoryAlert, StoreInventory


#Serializer for categories model - handles basic category information
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category    #Specifies which model to serialize
        fields = ['id', 'name', 'description', 'created_at']        #only these fields will be included in API responses

#Serializer for InventoryItem model - handles inventory item details
class InventoryItemSerializer(serializers.ModelSerializer):

    #adds extra fields that aren't directly in the model
    category_name = serializers.CharField(source='category.name', read_only=True)       #Gets category name from related category model
    created_by_username = serializers.CharField(read_only=True)         #shows who created the item

    class Meta:
        model = InventoryItem    
        fields = "__all__"      #Include all model fields in serialization
        read_only_fields = ['created_by', 'date_added', 'last_updated']   #These fields can't be modified through API

#Serializer for InventoryChange model - Tracks changes in inventory
class InventoryChangeSerializer(serializers.ModelSerializer):

    #Add extra fields that aren't directly in the model
    item_name = serializers.CharField(source='item.name', read_only=True)       #Gets item name from related item model
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True) #shows who made the change

    class Meta:
        model = InventoryChange
        fields = "__all__"
        read_only_fields = ['changed_by', 'timestamp']

#Serializer for supplier model - manages supplier information        
class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_by']
#Serializer for Store model - handles store location data
class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'contact_number', 'email', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_by']

#Serializer for StoreInventory model - manages inventory at specific stores
class StoreInventorySerializer(serializers.ModelSerializer):

    #Add readable names for store and item
    store_name = serializers.CharField(read_only=True)
    item_name = serializers.CharField(read_only=True)

    class Meta:
        model = StoreInventory
        fields = ['id', 'store', 'store_name', 'item', 'item_name',
                  'quantity', 'low_stock_threshold', 'reorder_point', 'reorder_quantity', 'needs_reorder']
        
    # Custom method to add store and item names to the output   
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['store_name'] = instance.store.name
        representation['item_name'] = instance.item.name
        return representation
    
#Serializer for the InventoryAlert model - handles inventory alerts/notifications        
class InventoryAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAlert
        fields = '__all__'      #Include all fields fromm the model










