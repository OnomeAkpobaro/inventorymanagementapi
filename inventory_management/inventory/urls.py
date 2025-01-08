from django.urls import path, include
from rest_framework.routers import DefaultRouter
from  .models import Category, InventoryItem, InventoryChange
from .views import CategoryViewSet, InventoryItemViewSet, InventoryChangeViewSet, SupplierViewSet, StoreViewSet, StoreInventoryViewSet, StockReportView

router = DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'inventory-item', InventoryItemViewSet, basename='inventory-item')
router.register(r'inventory-changes', InventoryChangeViewSet, basename='inventory-changes')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'stores', StoreViewSet, basename='store')
router.register(r'store-inventory', StoreInventoryViewSet, basename='store-inventory')

urlpatterns = [
    path('', include(router.urls)),
    path('reports/stock/', StockReportView.as_view(), name='stock-report'),
]

