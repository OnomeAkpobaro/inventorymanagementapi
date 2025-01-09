from .models import InventoryAlert, StoreInventory
from django.dispatch import receiver
from django.db.models.signals import post_save


class AlertManager:
    """
    Manages Inventory alerts by monitoring stock levels and creating alerts when necessary
    Provides methods to check for low stock conditions and reorder requirement
    """
    @staticmethod
    def check_low_stock(store_inventory):
        """
        Creates a low stock alert if inventory falls below threshold

        Args:
            store_inventory: StoreInventroy instance to check for low stock condition

        Alerts will only be created if one doesn't exist for this item or store
    
        """
        if store_inventory.is_low_stock:
            InventoryAlert.objects.get_or_create(
                store=store_inventory.store,
                item=store_inventory.item,
                alert_type='LOW_STOCK',
                is_resolved=False,
                defaults={
                    "message": f"Low stock alert for {store_inventory.item.name}."
                                f"in {store_inventory.store.name}."
                                f"Current quantity: {store_inventory.quantity}"

                }


            )
    @staticmethod
    def check_reorder(store_inventory):
        """
        Creates a reorder alert if inventory needs refill
        """
        if store_inventory.needs_reorder:
            InventoryAlert.objects.get_or_create(
                store=store_inventory.store,
                item=store_inventory.item,
                alert_type='REORDER',
                is_resolved=False,
                defaults={
                    "message": f"Reorder suggestion for {store_inventory.item.name} "
                                f"in {store_inventory.store.name}. "
                                f"Suggested quantity: {store_inventory.reorder_quantity}"
                }
            )        

@receiver(post_save, sender=StoreInventory)
def handle_inventory_changes(sender, instance):
    """
    SIgnal handler that triggers alert checks whenever inventory is updated.

    Args:
        sender: The model class that sent the signal
        instance: The StoreInventory instance that was saved
    """
    AlertManager.check_low_stock(instance)
    AlertManager.check_reorder(instance)