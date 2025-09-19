from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import EmptyPage, PageNotAnInteger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Category, Product, ProductVariant, ProductImage, InventoryLog, ProductMeasurement
from .serializers import (
    CategorySerializer, CategoryCreateSerializer, ProductSerializer, ProductDetailSerializer,
    ProductCreateSerializer, ProductUpdateSerializer, ProductVariantSerializer,
    ProductImageSerializer, InventoryLogSerializer, ProductSearchSerializer,
    ProductFilterSerializer, StockUpdateSerializer, ProductStatsSerializer,
    ProductMeasurementSerializer, ProductMeasurementCreateSerializer
)
from utils.image_utils import validate_image_file, resize_image
from utils.pagination import PreserveStatePagination
import json


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for category management
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = PreserveStatePagination
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            # Allow public access for listing and retrieving categories
            permission_classes = []
        else:
            # Require authentication for create, update, delete operations
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    

    
    @swagger_auto_schema(tags=['products'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CategoryCreateSerializer
        return CategorySerializer
    
    def create(self, request, *args, **kwargs):
        """Custom create method to handle FormData and image uploads"""
        # Debug: Log incoming data
        print("Category create - Raw request data:", request.data)
        print("Category create - Files:", request.FILES)
        
        # Process request data
        data = request.data.copy()
        
        # Handle parent field - set to None if not provided or empty
        if 'parent' not in data or data['parent'] == '':
            data['parent'] = None
        
        # Handle sort_order - convert to integer
        if 'sort_order' in data:
            try:
                data['sort_order'] = int(data['sort_order'])
            except (ValueError, TypeError):
                data['sort_order'] = 0
        
        print("Category create - Processed data:", data)
        
        # Create serializer with processed data
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print("Category create - Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        
        # Process image if uploaded
        if 'image' in request.FILES:
            category = serializer.instance
            image_file = request.FILES['image']
            
            # Validate the image file
            is_valid, message = validate_image_file(image_file)
            if not is_valid:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the image to the category
            category.image = image_file
            category.save()
            
            # Resize the image if needed
            if category.image:
                resize_image(category.image.path)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        queryset = Category.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by parent
        parent = self.request.query_params.get('parent', None)
        if parent is not None:
            if parent == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent)
        
        return queryset.order_by('sort_order', 'name')
    
    @swagger_auto_schema(
        tags=['products'],
        operation_description="Get category tree structure"
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure"""
        categories = Category.objects.filter(parent__isnull=True, is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['products'],
        operation_description="Get products in a specific category"
    )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products in a category"""
        category = self.get_object()
        products = Product.objects.filter(category=category, status='active')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['products'],
        operation_description="Upload image for a category"
    )
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload an image for a category"""
        category = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validate the image file
        is_valid, message = validate_image_file(image_file)
        if not is_valid:
            return Response(
                {'error': message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the image to the category
        category.image = image_file
        category.save()
        
        # Resize the image if needed
        if category.image:
            resize_image(category.image.path)
        
        return Response({
            'message': 'Image uploaded successfully',
            'image_url': category.image.url if category.image else None
        })
    
    def destroy(self, request, *args, **kwargs):
        """Custom destroy method that preserves pagination state"""
        instance = self.get_object()
        
        # Get current pagination state before deletion
        paginator = self.paginator
        current_page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', self.paginator.page_size)
        
        # Delete the instance
        instance.delete()
        
        # Get the updated queryset for the same page
        queryset = self.get_queryset()
        
        # Paginate the updated queryset
        try:
            page = paginator.paginate_queryset(queryset, request)
        except (EmptyPage, PageNotAnInteger):
            # If the current page no longer exists, get the last page
            paginator.page_size = page_size
            page = paginator.paginate_queryset(queryset, request)
        
        # Serialize the results
        serializer = self.get_serializer(page, many=True)
        
        # Return response with preserved pagination state
        return paginator.get_paginated_response(serializer.data, deleted_count=1)
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Bulk delete categories while preserving pagination state"""
        category_ids = request.data.get('ids', [])
        if not category_ids:
            return Response(
                {'error': 'No category IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get current pagination state before deletion
        paginator = self.paginator
        current_page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', self.paginator.page_size)
        
        # Delete the categories
        deleted_count = Category.objects.filter(id__in=category_ids).delete()[0]
        
        # Get the updated queryset for the same page
        queryset = self.get_queryset()
        
        # Paginate the updated queryset
        try:
            page = paginator.paginate_queryset(queryset, request)
        except (EmptyPage, PageNotAnInteger):
            # If the current page no longer exists, get the last page
            paginator.page_size = page_size
            page = paginator.paginate_queryset(queryset, request)
        
        # Serialize the results
        serializer = self.get_serializer(page, many=True)
        
        # Return response with preserved pagination state
        return paginator.get_paginated_response(serializer.data, deleted_count=deleted_count)

    @swagger_auto_schema(
        tags=['products'],
        operation_description="Bulk delete categories"
    )
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Bulk delete categories while preserving pagination state"""
        category_ids = request.data.get('ids', [])
        if not category_ids:
            return Response(
                {'error': 'No category IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get current pagination state before deletion
        paginator = self.paginator
        current_page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', self.paginator.page_size)
        
        # Delete the categories
        deleted_count = Category.objects.filter(id__in=category_ids).delete()[0]
        
        # Get the updated queryset for the same page
        queryset = self.get_queryset()
        
        # Paginate the updated queryset
        try:
            page = paginator.paginate_queryset(queryset, request)
        except (EmptyPage, PageNotAnInteger):
            # If the current page no longer exists, get the last page
            paginator.page_size = page_size
            page = paginator.paginate_queryset(queryset, request)
        
        # Serialize the results
        serializer = self.get_serializer(page, many=True)
        
        # Return response with preserved pagination state
        return paginator.get_paginated_response(serializer.data, deleted_count=deleted_count)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product management
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = PreserveStatePagination
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'featured', 'new', 'on_sale', 'search', 'category']:
            # Allow public access for listing, retrieving, and browsing products
            permission_classes = []
        else:
            # Require authentication for create, update, delete operations
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    

    
    @swagger_auto_schema(tags=['products'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['products'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return ProductDetailSerializer
        return ProductSerializer
    
    def create(self, request, *args, **kwargs):
        """Custom create method to handle FormData and JSON fields"""
        # Handle JSON fields that come as strings from FormData
        data = request.data.copy()
        
        # Parse JSON fields if they come as strings
        json_fields = ['tags', 'pairings', 'awards', 'bulk_pricing']
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = []
        
        # Handle category ID - convert to integer if provided
        if 'category' in data and data['category']:
            try:
                data['category'] = int(data['category'])
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid category ID'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create serializer with processed data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Process image if uploaded
        if 'image' in request.FILES:
            product = serializer.instance
            image_file = request.FILES['image']
            
            # Validate the image file
            is_valid, message = validate_image_file(image_file)
            if not is_valid:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the image to the product
            product.image = image_file
            product.save()
            
            # Resize the image if needed
            if product.image:
                resize_image(product.image.path)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """Custom update method to handle FormData and JSON fields"""
        # Handle JSON fields that come as strings from FormData
        data = request.data.copy()
        
        # Parse JSON fields if they come as strings
        json_fields = ['tags', 'pairings', 'awards', 'bulk_pricing']
        for field in json_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = []
        
        # Handle category ID - convert to integer if provided
        if 'category' in data and data['category']:
            try:
                data['category'] = int(data['category'])
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid category ID'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get the product instance
        instance = self.get_object()
        
        # Create serializer with processed data
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Process image if uploaded
        if 'image' in request.FILES:
            product = serializer.instance
            image_file = request.FILES['image']
            
            # Validate the image file
            is_valid, message = validate_image_file(image_file)
            if not is_valid:
                return Response(
                    {'error': message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the image to the product
            product.image = image_file
            product.save()
            
            # Resize the image if needed
            if product.image:
                resize_image(product.image.path)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Custom destroy method that preserves pagination state"""
        instance = self.get_object()
        
        # Get current pagination state before deletion
        paginator = self.paginator
        current_page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', self.paginator.page_size)
        
        # Delete the instance
        instance.delete()
        
        # Get the updated queryset for the same page
        queryset = self.get_queryset()
        
        # Paginate the updated queryset
        try:
            page = paginator.paginate_queryset(queryset, request)
        except (EmptyPage, PageNotAnInteger):
            # If the current page no longer exists, get the last page
            paginator.page_size = page_size
            page = paginator.paginate_queryset(queryset, request)
        
        # Serialize the results
        serializer = self.get_serializer(page, many=True)
        
        # Return response with preserved pagination state
        return paginator.get_paginated_response(serializer.data, deleted_count=1)
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Bulk delete products while preserving pagination state"""
        product_ids = request.data.get('ids', [])
        if not product_ids:
            return Response(
                {'error': 'No product IDs provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get current pagination state before deletion
        paginator = self.paginator
        current_page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', self.paginator.page_size)
        
        # Delete the products
        deleted_count = Product.objects.filter(id__in=product_ids).delete()[0]
        
        # Get the updated queryset for the same page
        queryset = self.get_queryset()
        
        # Paginate the updated queryset
        try:
            page = paginator.paginate_queryset(queryset, request)
        except (EmptyPage, PageNotAnInteger):
            # If the current page no longer exists, get the last page
            paginator.page_size = page_size
            page = paginator.paginate_queryset(queryset, request)
        
        # Serialize the results
        serializer = self.get_serializer(page, many=True)
        
        # Return response with preserved pagination state
        return paginator.get_paginated_response(serializer.data, deleted_count=deleted_count)
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related('variants', 'product_images')
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by availability
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock is not None:
            if in_stock.lower() == 'true':
                queryset = queryset.filter(stock__gt=0)
            else:
                queryset = queryset.filter(stock=0)
        
        # Filter by stock status
        stock_status = self.request.query_params.get('stock_status', None)
        if stock_status:
            if stock_status == 'in_stock':
                queryset = queryset.filter(stock__gt=10)
            elif stock_status == 'low_stock':
                queryset = queryset.filter(stock__lte=10, stock__gt=0)
            elif stock_status == 'out_of_stock':
                queryset = queryset.filter(stock=0)
        
        # Filter by features
        is_featured = self.request.query_params.get('is_featured', None)
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        
        is_new = self.request.query_params.get('is_new', None)
        if is_new is not None:
            queryset = queryset.filter(is_new=is_new.lower() == 'true')
        
        is_on_sale = self.request.query_params.get('is_on_sale', None)
        if is_on_sale is not None:
            queryset = queryset.filter(is_on_sale=is_on_sale.lower() == 'true')
        
        # Price range filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Search by name or description
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(sku__icontains=search)
            )
        
        # Sort by
        sort_by = self.request.query_params.get('sort_by', 'created_at')
        if sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == 'stock':
            queryset = queryset.order_by('stock')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Advanced product search"""
        serializer = ProductSearchSerializer(data=request.data)
        if serializer.is_valid():
            queryset = Product.objects.select_related('category').prefetch_related('variants', 'product_images')
            
            # Apply search filters
            if serializer.validated_data.get('query'):
                query = serializer.validated_data['query']
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(sku__icontains=query) |
                    Q(tags__contains=[query])
                )
            
            if serializer.validated_data.get('category'):
                queryset = queryset.filter(category__name=serializer.validated_data['category'])
            
            if serializer.validated_data.get('min_price'):
                queryset = queryset.filter(price__gte=serializer.validated_data['min_price'])
            
            if serializer.validated_data.get('max_price'):
                queryset = queryset.filter(price__lte=serializer.validated_data['max_price'])
            
            if serializer.validated_data.get('status'):
                queryset = queryset.filter(status=serializer.validated_data['status'])
            
            if serializer.validated_data.get('unit'):
                queryset = queryset.filter(unit=serializer.validated_data['unit'])
            
            if serializer.validated_data.get('is_featured'):
                queryset = queryset.filter(is_featured=True)
            
            if serializer.validated_data.get('is_new'):
                queryset = queryset.filter(is_new=True)
            
            if serializer.validated_data.get('is_on_sale'):
                queryset = queryset.filter(is_on_sale=True)
            
            # Sort results
            sort_by = serializer.validated_data.get('sort_by', 'created_at')
            if sort_by == 'name':
                queryset = queryset.order_by('name')
            elif sort_by == 'price':
                queryset = queryset.order_by('price')
            elif sort_by == 'rating':
                queryset = queryset.order_by('-average_rating')
            else:
                queryset = queryset.order_by('-created_at')
            
            serializer_result = ProductSerializer(queryset, many=True)
            return Response(serializer_result.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products with pagination - Accessible with web token or Firebase auth"""
        products = Product.objects.select_related('category').prefetch_related('variants', 'product_images').filter(is_featured=True, status='active')
        
        # Apply additional filters if provided
        category = request.query_params.get('category', None)
        if category:
            products = products.filter(category_id=category)
        
        # Apply sorting
        sort_by = request.query_params.get('sort_by', 'created_at')
        if sort_by == 'name':
            products = products.order_by('name')
        elif sort_by == 'price':
            products = products.order_by('price')
        elif sort_by == 'rating':
            products = products.order_by('-average_rating')
        else:
            products = products.order_by('-created_at')
        
        # Paginate the queryset
        paginator = self.paginator
        page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new(self, request):
        """Get new products with pagination - Accessible with web token or Firebase auth"""
        products = Product.objects.select_related('category').prefetch_related('variants', 'product_images').filter(is_new=True, status='active')
        
        # Apply additional filters if provided
        category = request.query_params.get('category', None)
        if category:
            products = products.filter(category_id=category)
        
        # Apply sorting
        sort_by = request.query_params.get('sort_by', 'created_at')
        if sort_by == 'name':
            products = products.order_by('name')
        elif sort_by == 'price':
            products = products.order_by('price')
        elif sort_by == 'rating':
            products = products.order_by('-average_rating')
        else:
            products = products.order_by('-created_at')
        
        # Paginate the queryset
        paginator = self.paginator
        page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products on sale with pagination - Accessible with web token or Firebase auth"""
        products = Product.objects.select_related('category').prefetch_related('variants', 'product_images').filter(is_on_sale=True, status='active')
        
        # Apply additional filters if provided
        category = request.query_params.get('category', None)
        if category:
            products = products.filter(category_id=category)
        
        # Apply sorting
        sort_by = request.query_params.get('sort_by', 'created_at')
        if sort_by == 'name':
            products = products.order_by('name')
        elif sort_by == 'price':
            products = products.order_by('price')
        elif sort_by == 'rating':
            products = products.order_by('-average_rating')
        else:
            products = products.order_by('-created_at')
        
        # Paginate the queryset
        paginator = self.paginator
        page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """Return dynamic filter options for products page"""
        categories_qs = Category.objects.filter(is_active=True).values('id', 'name').order_by('name')
        categories = list(categories_qs)

        regions = list(
            Product.objects.exclude(region__isnull=True)
            .exclude(region__exact='')
            .values_list('region', flat=True)
            .distinct()
            .order_by('region')
        )
        vintages = list(
            Product.objects.exclude(vintage__isnull=True)
            .exclude(vintage__exact='')
            .values_list('vintage', flat=True)
            .distinct()
            .order_by('vintage')
        )

        price_ranges = [
            { 'label': 'Under $25', 'min': 0, 'max': 25 },
            { 'label': '$25 - $50', 'min': 25, 'max': 50 },
            { 'label': '$50 - $100', 'min': 50, 'max': 100 },
            { 'label': '$100 - $250', 'min': 100, 'max': 250 },
            { 'label': '$250 - $500', 'min': 250, 'max': 500 },
            { 'label': '$500+', 'min': 500, 'max': 1000000 },
        ]

        return Response({
            'categories': categories,
            'brands': [],
            'alcohol_types': [],
            'countries': [],
            'regions': regions,
            'vintages': vintages,
            'price_ranges': price_ranges,
        })

    @swagger_auto_schema(
        tags=['stock'],
        operation_description="Get products with low stock levels"
    )
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock"""
        products = Product.objects.select_related('category').prefetch_related('variants', 'product_images').filter(
            stock__lte=F('min_stock_level'),
            stock__gt=0
        )
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get product statistics"""
        stats = {
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(status='active').count(),
            'out_of_stock_products': Product.objects.filter(status='out_of_stock').count(),
            'featured_products': Product.objects.filter(is_featured=True).count(),
            'new_products': Product.objects.filter(is_new=True).count(),
            'on_sale_products': Product.objects.filter(is_on_sale=True).count(),
            'total_categories': Category.objects.count(),
            'low_stock_products': Product.objects.filter(
                stock__lte=F('min_stock_level'),
                stock__gt=0
            ).count(),
        }
        
        serializer = ProductStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Upload an image for a product"""
        product = self.get_object()
        
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validate the image file
        is_valid, message = validate_image_file(image_file)
        if not is_valid:
            return Response(
                {'error': message}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the image to the product
        product.image = image_file
        product.save()
        
        # Resize the image if needed
        if product.image:
            resize_image(product.image.path)
        
        return Response({
            'message': 'Image uploaded successfully',
            'image_url': product.image.url if product.image else None
        })
    
    @swagger_auto_schema(
        tags=['products'],
        operation_description="Get category information for a specific product"
    )
    @action(detail=True, methods=['get'], permission_classes=[])
    def category(self, request, pk=None):
        """Get category information for a product - Lightweight endpoint for category data only - Accessible with web token or Firebase auth"""
        # Custom permission check to allow both web token and Firebase auth
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Response(
                {'detail': 'Authentication credentials were not provided.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = auth_header.split(' ')[1]
        # Allow web token or any valid token (Firebase tokens will be validated by the backend)
        if token not in ['bottleplug-web-token-2024'] and not token.startswith('eyJ'):
            return Response(
                {'detail': 'Invalid authentication credentials.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            product = self.get_object()
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not product.category:
            return Response({
                'product_id': product.id,
                'product_name': product.name,
                'category': None,
                'category_name': None
            })
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
                'description': product.category.description,
                'is_active': product.category.is_active
            },
            'category_name': product.category.name
        })
    
    @swagger_auto_schema(
        tags=['stock'],
        operation_description="Update product stock levels"
    )
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update product stock"""
        product = self.get_object()
        serializer = StockUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            log_type = serializer.validated_data['log_type']
            reference = serializer.validated_data.get('reference', '')
            notes = serializer.validated_data.get('notes', '')
            
            # Record previous stock
            previous_stock = product.stock
            
            # Update stock
            product.update_stock(quantity)
            
            # Create inventory log
            InventoryLog.objects.create(
                product=product,
                log_type=log_type,
                quantity=quantity,
                previous_stock=previous_stock,
                new_stock=product.stock,
                reference=reference,
                notes=notes,
                created_by=request.user
            )
            
            return Response({
                'message': 'Stock updated successfully',
                'new_stock': product.stock
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product variants
    """
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ProductVariant.objects.all()
        
        # Filter by product
        product = self.request.query_params.get('product', None)
        if product:
            queryset = queryset.filter(product_id=product)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for inventory logs (read-only)
    """
    queryset = InventoryLog.objects.all()
    serializer_class = InventoryLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['stock'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['stock'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = InventoryLog.objects.select_related('product', 'created_by')
        
        # Filter by product
        product = self.request.query_params.get('product', None)
        if product:
            queryset = queryset.filter(product_id=product)
        
        # Filter by log type
        log_type = self.request.query_params.get('log_type', None)
        if log_type:
            queryset = queryset.filter(log_type=log_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        
        return queryset.order_by('-created_at')


class ProductMeasurementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product measurements
    """
    queryset = ProductMeasurement.objects.all()
    serializer_class = ProductMeasurementSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    @swagger_auto_schema(tags=['stock'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['stock'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['stock'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['stock'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['stock'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['stock'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductMeasurementCreateSerializer
        return ProductMeasurementSerializer
    
    def get_queryset(self):
        queryset = ProductMeasurement.objects.select_related('product')
        
        # Filter by product
        product = self.request.query_params.get('product', None)
        if product:
            queryset = queryset.filter(product_id=product)
        
        # Filter by measurement type
        measurement = self.request.query_params.get('measurement', None)
        if measurement:
            queryset = queryset.filter(measurement=measurement)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by default status
        is_default = self.request.query_params.get('is_default', None)
        if is_default is not None:
            queryset = queryset.filter(is_default=is_default.lower() == 'true')
        
        return queryset.order_by('sort_order', 'price')
    
    def create(self, request, *args, **kwargs):
        """Create a new product measurement"""
        print(f"DEBUG: Request data: {request.data}")
        print(f"DEBUG: Request content type: {request.content_type}")
        serializer = self.get_serializer(data=request.data)
        print(f"DEBUG: Serializer valid: {serializer.is_valid()}")
        if not serializer.is_valid():
            print(f"DEBUG: Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the product from the request data
        product_id = request.data.get('product')
        if not product_id:
            return Response(
                {'error': 'Product ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create the measurement with the product context
        measurement = serializer.save(product=product)
        
        return Response(
            ProductMeasurementSerializer(measurement).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Update a product measurement"""
        print(f"DEBUG UPDATE: Request data: {request.data}")
        measurement = self.get_object()
        print(f"DEBUG UPDATE: Measurement ID: {measurement.id}")
        
        # Remove product field from data if present (shouldn't be updated)
        data = request.data.copy()
        if 'product' in data:
            del data['product']
        
        serializer = self.get_serializer(measurement, data=data, partial=True)
        print(f"DEBUG UPDATE: Serializer valid: {serializer.is_valid()}")
        
        if not serializer.is_valid():
            print(f"DEBUG UPDATE: Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the measurement
        updated_measurement = serializer.save()
        
        return Response(ProductMeasurementSerializer(updated_measurement).data)
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """Update stock for a specific measurement - DEPRECATED: Stock is now managed at product level"""
        return Response({
            'error': 'Stock updates for measurements are no longer supported. Please update stock at the product level.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def measurements_list(self, request):
        """Get list of available measurement types"""
        measurements = ProductMeasurement.MEASUREMENT_CHOICES
        return Response({
            'measurements': [
                {'value': choice[0], 'label': choice[1]} 
                for choice in measurements
            ]
        })
