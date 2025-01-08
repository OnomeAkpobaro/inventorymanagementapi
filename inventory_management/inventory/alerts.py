from .models import InventoryAlert

class AlertManager:
    @staticmethod
    def check_low_stock(store_inventory):
        if store_inventory.is_low_stock:
            InventoryAlert.objects.get_or_create(
                store=store_inventory.store,
                item=store_inventory.item,
                alert_type='LOW_STOCK',
                is_resolved=False,
                defaults={
                    "message": f"Low stock alert for {store_inventory.iten.name}."
                                f"in {store_inventory.store.name}."
                                f"Current quantity: {store_inventory.quantity}"
                }

            )