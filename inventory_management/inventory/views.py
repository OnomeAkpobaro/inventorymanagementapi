from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, InventoryItem, InventoryChange, Supplier, Store, StoreInventory, InventoryAlert
from .serializers import CategorySerializer, InventoryItemSerializer, InventoryChangeSerializer, SupplierSerializer, StoreSerializer, StoreInventorySerializer, InventoryAlertSerializer
from django_filters import FilterSet, BooleanFilter
from django.db import models
from rest_framework.views import APIView
from .reports import InventoryReport
from datetime import datetime
# Create your views here.

#Custom pagination class that sets default page size and limits
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size' #Allow client to override page size
    max_page_size = 1000        

#ViewSet for managing Categeory model objects
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()           #Get all categories
    serializer_class = CategorySerializer          #Defines how category data is serialized
    permission_classes = [IsAuthenticated]          #Requires authentication
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]    #Enalbe search and ordering
    search_fields = ['name', 'description']     #fields that can be searched
    ordering_fields = ['name', 'created_at']      #fieklds that can be ordered by
    pagination_class = StandardResultsSetPagination     #Use custom pagination

    #CRUD operations with standardized responses 
    def list(self, request):
        """
        List all categories with optional filtering and search
        Includes the count of items in each category
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response ({
            "status": "success",
            "count": queryset.count(),
            "result": serializer.data
        })


    def create(self, request):
        """
        creates a new category with validation for duplicate names
        """
        name = request.data.get('name', '').strip()
        #check for existing category with same name (case-insensitive)
        if Category.objects.filter(name__iexact=name).exists():
            return Response({
                'status': 'error',
                'message': 'A category with the name already exist.'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'status': 'success',
            'message': 'Category created successfully.'
        }, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request):
        """
        Retrieve a category with its related name
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # Get and serialize related items
        items = instance.items.all()
        item_serializer = InventoryItemSerializer(items, many=True)

        return Response({
            'status': 'success',
            'data': {
                'category': serializer.data,
                'items': item_serializer.data
            }
        })
    def update(self, request, pk=None):
        """
        Updatwe a category with duplicate name validation
        """
        instance = self.get_object()
        name = request.data.get('name', '').strip()

        #check for existing category with same name, excluding current instance
        if Category.objects.filter(name__iexact=name).exclude(pk=pk).exists():
            return Response({
                "status": "error",
                "message": "A category with this name already exists."
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "message": "Category updated successfully",
            "data": serializer.data
        })
    def destroy(self, request):
        """
        Delete a category only if it has no items
        """
        instance =self.get_object()
        item_count = instance.items.count()

        #Prevent deletion if category has items
        if item_count > 0:
            return Response({
                'status': 'error',
                'message': f'Cannot delete category . It has {items_count} items attached to it.'
            }, status=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "message": "Category deleted successfully."
        }, status=status.HTTP_200_OK)

#Viewset for managing in ventoryItem model objects  
class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'quantity', 'price', 'date_added']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        #Get items created by current user with using category 
        queryset = InventoryItem.objects.select_related('category').filter(created_by=self.request.user)
        return self._apply_filters(queryset)

    def _apply_filters(self, queryset):
        #method to apply price range and stock level filters
        #Filter by price range if specified
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
                                                                                                                                                            
        #Filter low stock items if threshold specified
        low_stock = self.request.query_params.get('low_stock')
        if low_stock:
            threshold = int(low_stock)
            queryset = queryset.filter(quantity__lte=threshold)
        return queryset
    #CRUD operations with Standardized responses
    def list(self, request):
        """
        Lists inventory items with counts
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "count": queryset.count(),
            "results": serializer.data,
        })
    def create(self, request):
        """
        Create a new inventory item
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            "status": "success",
            "message": "Inventory item successfully created.",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        #Set created_by foield when creating itemn
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, pk=None):
        """
        Retrieve an inventory item
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            "status": "success",
            "data": serializer.data
        }) 
    def update(self, request, pk=None):
        """
        Update an inventory
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "status": "success",
            "message": "Inventory item successfully updated",
            "data": serializer.data
        })
    def destroy(self, request, pk=None):
        """
        Delete an inventory item
        """
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "status": "success",
            "message": "Inventory item successfully deleted."
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """
        Custom endpoint to adjust the stock quantity of an item
        """
        item = self.get_object()
        quantity_change = request.data.get('quantity_change', 0)
        notes = request.data.get('notes', '')

        if quantity_change == 0:
            return Response({'error': 'Quantity change cannot be zero'}, status=status.HTTP_400_BAD_REQUEST)
            
        #Calculate new quantity and validate
        previous_quantity = item.quantity
        new_quantity = previous_quantity + quantity_change

        if new_quantity < 0:
            return Response({
                "status": "error",
                "message": "Insufficient stock"
            }, status=status.HTTP_400_BAD_REQUEST)
        
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

        #Update item quantity
        item.quantity = new_quantity
        item.save()

        return Response({
            "status": "success",
            "message": "Stock adjusted successfully",
            "data": self.get_serializer(item).data
        })
#ViewSet for viewing inventory change history
class InventoryChangeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InventoryChangeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'change_type']                      #Allow filtering by item and change type
    ordering_fields = ['timestamp']                                 #Allow ordering by timestamp
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        #Gets chasnges for items created by current user with select_related for optimization
        return InventoryChange.objects.filter(item__created_by=self.request.user).select_related('item', 'changed_by')
    
    def list(self, request):
        """
        List inventory changes with pagination
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "message": "Inventory changes retrieved successfully",
            "count": queryset.count(),
            "results": serializer.data
        })
    
    def retrieve(self, request, pk=None):
        """
        Retrieve an inventory change record
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response({
            "status": "success",
            "message": "Inventory change record retrieved successfully.",
            "data": serializer.data
        })
    
#Viewset for mamnaging sup[plier model objects
#provides CRUD operations for supplier with authentication and filtering
class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'contact_person', 'email']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        """
        Reeturns supplier created by the current user only
        """
        return Supplier.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        #Automatically sets the created_by field to current user when creating a supplier
        serializer.save(created_by=self.request.user)

#Viewset for  managing store model objects 
class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address', 'email']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        #Returns stores created by the current user only 
        return Store.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        #Sets created_by fields to curreent user when creating a store 
        serializer.save(created_by=self.request.user)

#Custom FilterSet for StoreInventory filtering
#Adds additional filtering capabilities for inventory items
class StoreInventoryFilterSet(FilterSet):
    is_low_stock = BooleanFilter(method='filter_is_low_stock')
    

    class Meta:
        model = StoreInventory
        fields = ['store', 'item']

    def filter_is_low_stock(self, queryset, name, value):
        """
        If true, returns items where quantity is less than or equal to low_stock_threshold
        """
        if value:
            return queryset.filter(quantity__lte=models.F('low_stock_threshold'))
        return queryset
    

#ViewSet for managing StoreInventory model objects
class StoreInventoryViewSet(viewsets.ModelViewSet):
    serializer_class = StoreInventorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = StoreInventoryFilterSet       #Uses custom filter set defined above
    ordering_fields = ['quantity', 'store_name', 'item_name']

    def get_queryset(self):
        #Returns inventory items for stores created by current user
        #Uses select_related to optimize database queries
        return StoreInventory.objects.filter(store__created_by=self.request.user).select_related('store', 'item')
    
#View for generating stock reports
class StockReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            #Extract and parse date parameters from requests
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            store_id = request.query_params.get('store_id')

            #Convert string dates to datetime objects if provided
            start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
            end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None


            #Generate  and return the stock report
            report = InventoryReport(user=request.user, start_date=start_date, end_date=end_date, store=store_id)

            report_data = report.generate_stock_report()
            return Response(report_data)
        
        except ValueError as e:
            """
            Handles invalid date fiormat errors
            """
            return Response(
                {"error": "Invalid date format. Format must be YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            """
            Handles other unexpected errors
            """
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
#Viewset for managing inventory alerts
class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['store', 'item', 'alert_type']      #Fields that can be filtered
    ordering_fields = ['created_at', 'resolved_at']         #Fields that can be ordered

    def get_queryset(self):
        #Returns alerts for stores created by cureent user
        #Uses select_related for optimisation
        return InventoryAlert.objects.filter(store__created_by=self.request.user).select_related('store', 'item')
    @action(detail=True, methods=['post'])
    def resolve_alert(self, request, pk=None):
        #Custom action to mark an alert as resolved
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        return Response(self.serializer_class(alert).data)
    


