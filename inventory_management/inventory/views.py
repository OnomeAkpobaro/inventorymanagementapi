from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, InventoryItem, InventoryChange
from .serializers import CategorySerializer, InventoryItemSerializer, InventoryChangeSerializer

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'quantity', 'price', 'date_added']

    def get_queryset(self):
        queryset = InventoryItem.objects.all()

        #Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        #Filter low stock items
        low_stock = self.request.query_params.get('low_stock', None)
        if low_stock:
            threshold = int(low_stock)
            queryset = queryset.filter(quantity__lte=threshold)
        return queryset
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        item = self.get_object()
        quantity_change = request.data.get('quantity_change', 0)
        notes = request.data.get('notes', '')

        if quantity_change == 0:
            return Response({'error': 'Quantity change cannot be zero'}, status=status.HTTP_400_BAD_REQUEST)
            

        previous_quantity = item.quantity
        new_quantity = previous_quantity + quantity_change

        if new_quantity < 0:
            return Response({'error': 'Insufficient stock'}, status=status.HTTP_400_BAD_REQUEST)
        
        #create inventory change record
        change_type = 'ADD' if quantity_change > 0 else 'REMOVE'
        InventoryChange.objects.create(
            item=item,
            change_type=change_type,
            quantity_change=quantity_change,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            changed_by=request.user,
            notes=notes
        )
        item.quantity = new_quantity
        item.save()

        return Response(self.get_serializer(item).data)

class InventoryChangeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryChangeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'change_type']
    ordering_fields = ['timestamp']

    def get_queryset(self):
        return InventoryChange.objects.filter(item__created_by=self.request.user).select_related('item', 'changed_by')
    

