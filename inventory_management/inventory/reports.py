from .models import StoreInventory, Store
from django.db import models


class InventoryReport:
    def __init__(self, user, start_date=None, end_date=None, store=None):
        self.user = user
        self.start_date = start_date
        self.end_date = end_date
        self.store = store

    def generate_stock_report(self):
        queryset = StoreInventory.objects.filter(store__created_by=self.user)

        if self.store:
            queryset = queryset.filter(store=self.store)

        report_data = {
            'total_items': queryset.count(),
            'total_value': sum(item.quantity * item.item.price for item in queryset),
            'low_stock_items': queryset.filter(quantity__lte=models.F('low_stock_threshold')).count(),
            'items_needing_reorder': queryset.filter(quantity__lte=models.F('reorder_point')).count(),
            'store_breakdown': []
        }

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

        