from .models import StoreInventory, Store
from django.db import models


class InventoryReport:
    """
    A class to generate inventory reports for stores.

    This class handles the generation of inventory reports includiing total items, value calculations, low stock alerts, 
    and each store break down of inventory status.

    Attributes:
        user: The user requesting the report (for filtering relevant stores)
        start_date: Optional start date for report period
        end_date: Optional end date for report period 
        store: Optional specific store to filter report data

    """

    def __init__(self, user, start_date=None, end_date=None, store=None):
        """
        Intialize the InventoryReport with filteriing parameters.

        Args:
            user: User ogject - The user requesting the report
            start_date (optional) : datetime - Stat date for report period
            end_date (optional): datetime - End date for report period
            store (optional): Store object - store to filter data for
        """
        self.user = user
        self.start_date = start_date
        self.end_date = end_date
        self.store = store

    def generate_stock_report(self):
        """
        Generate stock report for the specified parameters.

        This method queries the StoreInventory miodel to generate a detailed
        report including total items, value and low stock alerts.
        it can generate reports for all stores or a specific store belonging to the user

        Returns:
            dict: A dictionary containing 
                - total_items: Total number of inventory items
                - total_value: Total value of all inventory items
                - low_stock_items: Count of items below their low stock threshold
                - items_needing_reorder: Count of items at or below reorder point
                - store_breakdown: List of dictionaries containig each store statistics:
                        -  store_name: Name of the store
                        -  total_items: Total items in this store
                        -  total_value: Total inventory value in the store
                        -  low_stock_items: Count of low stock items in this store

    
        """

        #filter inventory items by user's stores
        queryset = StoreInventory.objects.filter(store__created_by=self.user)

        #Apply store filter if specified
        if self.store:
            queryset = queryset.filter(store=self.store)
        

        #calculate report data
        report_data = {
            'total_items': queryset.count(),
            'total_value': sum(item.quantity * item.item.price for item in queryset),
            'low_stock_items': queryset.filter(quantity__lte=models.F('low_stock_threshold')).count(),
            'items_needing_reorder': queryset.filter(quantity__lte=models.F('reorder_point')).count(),
            'store_breakdown': []
        }

        #Generate each store breakdown
        for store in Store.objects.filter(created_by=self.user):
            store_items = queryset.filter(store=store)
            report_data['store_breakdown'].append({
                'store_name': store.name,
                'total_items': store_items.count(),
                'total_value': sum(item.quantity * item.item.price for item in store_items),
                'low_stock_items': store_items.filter(
                    quantity__lte=models.F('low_stock_threshold')
                ).count()
            })
        return report_data

        