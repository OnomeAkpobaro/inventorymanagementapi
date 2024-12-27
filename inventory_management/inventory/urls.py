from django.urls import path, include
from rest_framework.routers import DefaultRouter
from  .models import Category, InventoryItem, InventoryChange
from .views import CategoryViewSet, InventoryItemViewSet, InventoryChangeViewSet

router = DefaultRouter()

router.register(r'categories', CategoryViewSet)
router.register(r'inventory', InventoryItemViewSet, basename='inventory')
router.register(r'inventory-changes', InventoryChangeViewSet, basename='inventory-changes')

urlpatterns = [
    path('', include(router.urls)),
]

