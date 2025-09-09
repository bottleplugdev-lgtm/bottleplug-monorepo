from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q, F, OuterRef, Subquery, Value
from django.db.models import DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    AnalyticsEvent, UserMetrics, ProductMetrics, OrderMetrics,
    DeliveryMetrics, RevenueMetrics, SearchAnalytics
)
from .serializers import (
    AnalyticsEventSerializer, UserMetricsSerializer, ProductMetricsSerializer,
    OrderMetricsSerializer, DeliveryMetricsSerializer, RevenueMetricsSerializer,
    SearchAnalyticsSerializer, AnalyticsFilterSerializer, DashboardStatsSerializer,
    RevenueChartSerializer, ProductPerformanceSerializer, TopSearchTermsSerializer,
    EventTrackingSerializer
)


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking analytics events
    """
    queryset = AnalyticsEvent.objects.all()
    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter analytics events by various criteria
        """
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return AnalyticsEvent.objects.none()
            
        queryset = AnalyticsEvent.objects.all()
        
        # Filter by event type
        event_type = self.request.query_params.get('event_type', None)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by user
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Track a new analytics event"
    )
    @action(detail=False, methods=['post'])
    def track_event(self, request):
        """
        Track a new analytics event
        """
        serializer = EventTrackingSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            return Response(
                AnalyticsEventSerializer(event).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get summary of events by type"
    )
    @action(detail=False, methods=['get'])
    def event_summary(self, request):
        """
        Get summary of events by type
        """
        events = AnalyticsEvent.objects.all()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        if start_date:
            events = events.filter(created_at__gte=start_date)
        if end_date:
            events = events.filter(created_at__lte=end_date)
        
        summary = events.values('event_type').annotate(
            count=Count('id'),
            unique_users=Count('user', distinct=True)
        ).order_by('-count')
        
        return Response(summary)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get user activity analytics"
    )
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """
        Get user activity analytics
        """
        user_id = request.query_params.get('user_id', None)
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        events = AnalyticsEvent.objects.filter(user_id=user_id)
        
        # Get events from last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_events = events.filter(created_at__gte=thirty_days_ago)
        
        activity_summary = {
            'total_events': events.count(),
            'recent_events': recent_events.count(),
            'event_types': list(recent_events.values_list('event_type', flat=True).distinct()),
            'last_activity': events.order_by('-created_at').first().created_at if events.exists() else None
        }
        
        return Response(activity_summary)


class UserMetricsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user metrics
    """
    queryset = UserMetrics.objects.all()
    serializer_class = UserMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get user statistics"
    )
    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        """
        Get comprehensive user statistics
        """
        from users.models import User
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users_today = User.objects.filter(
            date_joined__date=timezone.now().date()
        ).count()
        new_users_week = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # User types breakdown
        customers = User.objects.filter(user_type='customer').count()
        drivers = User.objects.filter(user_type='driver').count()
        admins = User.objects.filter(user_type='admin').count()
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'user_types': {
                'customers': customers,
                'drivers': drivers,
                'admins': admins
            }
        }
        
        return Response(stats)


class ProductMetricsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product metrics
    """
    queryset = ProductMetrics.objects.all()
    serializer_class = ProductMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get product performance metrics"
    )
    @action(detail=False, methods=['get'])
    def product_performance(self, request):
        """
        Get product performance metrics
        """
        from products.models import Product
        from orders.models import OrderItem
        
        # Get top selling products
        top_products = OrderItem.objects.values('product__name').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_quantity')[:10]
        
        # Get low stock products
        low_stock_products = Product.objects.filter(stock__lt=10).count()
        
        # Get product categories performance
        category_performance = OrderItem.objects.values(
            'product__category__name'
        ).annotate(
            total_orders=Count('order', distinct=True),
            total_revenue=Sum('total_price')
        ).order_by('-total_revenue')
        
        performance_data = {
            'top_products': list(top_products),
            'low_stock_count': low_stock_products,
            'category_performance': list(category_performance)
        }
        
        return Response(performance_data)


class OrderMetricsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for order metrics
    """
    queryset = OrderMetrics.objects.all()
    serializer_class = OrderMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get order statistics"
    )
    @action(detail=False, methods=['get'])
    def order_stats(self, request):
        """
        Get order statistics
        """
        from orders.models import Order
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        orders = Order.objects.filter(created_at__gte=start_date)
        
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Status breakdown
        status_breakdown = orders.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Daily orders for chart
        daily_orders = orders.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            count=Count('id'),
            revenue=Sum('total_amount')
        ).order_by('day')
        
        stats = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'status_breakdown': list(status_breakdown),
            'daily_orders': list(daily_orders)
        }
        
        return Response(stats)


class DeliveryMetricsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for delivery metrics
    """
    queryset = DeliveryMetrics.objects.all()
    serializer_class = DeliveryMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get delivery statistics"
    )
    @action(detail=False, methods=['get'])
    def delivery_stats(self, request):
        """
        Get delivery statistics
        """
        from deliveries.models import DeliveryRequest
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        deliveries = DeliveryRequest.objects.filter(created_at__gte=start_date)
        
        total_deliveries = deliveries.count()
        completed_deliveries = deliveries.filter(status='completed').count()
        avg_delivery_time = deliveries.filter(
            status='completed',
            completed_at__isnull=False
        ).aggregate(
            avg_time=Avg('completed_at' - 'created_at')
        )['avg_time']
        
        # Status breakdown
        status_breakdown = deliveries.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Driver performance
        driver_performance = deliveries.values('driver__first_name').annotate(
            total_deliveries=Count('id'),
            completed_deliveries=Count('id', filter=Q(status='completed')),
            avg_rating=Avg('rating__rating')
        ).order_by('-completed_deliveries')
        
        stats = {
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed_deliveries,
            'completion_rate': (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
            'avg_delivery_time': avg_delivery_time,
            'status_breakdown': list(status_breakdown),
            'driver_performance': list(driver_performance)
        }
        
        return Response(stats)


class RevenueMetricsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for revenue metrics
    """
    queryset = RevenueMetrics.objects.all()
    serializer_class = RevenueMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get revenue chart data"
    )
    @action(detail=False, methods=['get'])
    def revenue_chart(self, request):
        """
        Get revenue data for charts
        """
        from orders.models import Order
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Daily revenue
        daily_revenue = Order.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('day')
        
        # Monthly revenue
        monthly_revenue = Order.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).extra(
            select={'month': 'date_trunc(\'month\', created_at)'}
        ).values('month').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('month')
        
        # Revenue by payment method
        payment_method_revenue = Order.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).values('payment_method').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('-revenue')
        
        chart_data = {
            'daily_revenue': list(daily_revenue),
            'monthly_revenue': list(monthly_revenue),
            'payment_method_revenue': list(payment_method_revenue)
        }
        
        return Response(chart_data)


class SearchAnalyticsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for search analytics
    """
    queryset = SearchAnalytics.objects.all()
    serializer_class = SearchAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['analytics'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get top search terms"
    )
    @action(detail=False, methods=['get'])
    def top_search_terms(self, request):
        """
        Get top search terms
        """
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        searches = SearchAnalytics.objects.filter(
            timestamp__gte=start_date
        )
        
        # Top search terms
        top_terms = searches.values('search_term').annotate(
            count=Count('id'),
            unique_users=Count('user', distinct=True)
        ).order_by('-count')[:20]
        
        # Search trends (daily)
        daily_searches = searches.extra(
            select={'day': 'date(timestamp)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        # Failed searches (no results)
        failed_searches = searches.filter(results_count=0).values('search_term').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        search_data = {
            'top_terms': list(top_terms),
            'daily_searches': list(daily_searches),
            'failed_searches': list(failed_searches)
        }
        
        return Response(search_data)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Track search analytics"
    )
    @action(detail=False, methods=['post'])
    def track_search(self, request):
        """
        Track a search event
        """
        serializer = SearchAnalyticsSerializer(data=request.data)
        if serializer.is_valid():
            search = serializer.save()
            return Response(
                SearchAnalyticsSerializer(search).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard analytics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['analytics'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get dashboard statistics"
    )
    @action(detail=False, methods=['get'])
    
    def stats(self, request):
        """
        Get comprehensive dashboard statistics
        """
        from users.models import User
        from products.models import Product
        from orders.models import Order
        from deliveries.models import DeliveryRequest
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # User stats
        total_users = User.objects.count()
        new_users = User.objects.filter(date_joined__gte=start_date).count()
        
        # Product stats
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(stock__lt=10).count()
        
        # Order stats
        orders = Order.objects.filter(created_at__gte=start_date)
        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Delivery stats
        deliveries = DeliveryRequest.objects.filter(created_at__gte=start_date)
        total_deliveries = deliveries.count()
        completed_deliveries = deliveries.filter(status='completed').count()
        
        # Recent activity
        recent_orders = Order.objects.order_by('-created_at')[:5]
        recent_deliveries = DeliveryRequest.objects.order_by('-created_at')[:5]
        
        from orders.serializers import OrderSerializer
        from deliveries.serializers import DeliveryRequestSerializer
        
        dashboard_stats = {
            'users': {
                'total': total_users,
                'new': new_users
            },
            'products': {
                'total': total_products,
                'low_stock': low_stock_products
            },
            'orders': {
                'total': total_orders,
                'revenue': total_revenue,
                'avg_value': avg_order_value
            },
            'deliveries': {
                'total': total_deliveries,
                'completed': completed_deliveries,
                'completion_rate': (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
            },
            'recent_activity': {
                'orders': OrderSerializer(recent_orders, many=True).data,
                'deliveries': DeliveryRequestSerializer(recent_deliveries, many=True).data
            }
        }
        
        return Response(dashboard_stats)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get dashboard charts data"
    )
    @action(detail=False, methods=['get'])
    
    def charts(self, request):
        """
        Get data for dashboard charts
        """
        from orders.models import Order
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Consider orders as paid if:
        # 1) payment_status='paid' OR
        # 2) status indicates completion (delivered) OR
        # 3) sum of successful/paid/done transactions >= order total (in case status hasn't synced yet)
        from payments.models import PaymentTransaction
        paid_sum_subquery = PaymentTransaction.objects.filter(
            order_id=OuterRef('pk'),
            status__in=['successful', 'paid', 'done']
        ).values('order').annotate(
            s=Coalesce(
                Sum('amount'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).values('s')[:1]

        paid_orders = (
            Order.objects
            .filter(created_at__gte=start_date)
            .annotate(
                paid_total=Coalesce(
                    Subquery(
                        paid_sum_subquery,
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    ),
                    Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .filter(
                Q(payment_status__in=['paid', 'completed', 'done']) |
                Q(paid_total__gte=F('total_amount'))
            )
        )

        # Revenue chart data from paid orders
        revenue_data = paid_orders.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('day')
        
        # Order status chart
        order_status_data = Order.objects.filter(
            created_at__gte=start_date
        ).values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Product category performance
        category_data = Order.objects.filter(
            created_at__gte=start_date,
            status='completed'
        ).values(
            'items__product__category__name'
        ).annotate(
            revenue=Sum('items__total_price'),
            orders=Count('id', distinct=True)
        ).order_by('-revenue')
        
        charts_data = {
            'revenue': list(revenue_data),
            'order_status': list(order_status_data),
            'categories': list(category_data)
        }
        
        return Response(charts_data)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get geographic revenue and order distribution"
    )
    @action(detail=False, methods=['get'])
    
    def geographic(self, request):
        """
        Group orders by city and compute revenue, order counts, and share
        """
        from orders.models import Order

        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        qs = (
            Order.objects.filter(created_at__gte=start_date)
            .values('city')
            .annotate(
                orders=Count('id'),
                revenue=Coalesce(Sum('total_amount'), Value(0))
            )
            .order_by('-revenue')
        )

        total_revenue = sum(float(r['revenue']) for r in qs) or 0.0
        results = []
        for r in qs:
            name = r['city'] or 'Unknown'
            revenue = float(r['revenue'] or 0)
            percentage = (revenue / total_revenue * 100.0) if total_revenue > 0 else 0.0
            results.append({
                'name': name,
                'orders': r['orders'],
                'revenue': revenue,
                'percentage': percentage,
            })
        return Response({'results': results})

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Customer segment metrics (vip/regular/new) and retention rate"
    )
    @action(detail=False, methods=['get'])
    
    def customer_segments(self, request):
        from orders.models import Order
        from users.models import User

        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        orders = Order.objects.filter(created_at__gte=start_date)
        # Returning customers = customers with >= 2 orders in the period
        customer_order_counts = orders.values('customer').annotate(c=Count('id'))
        returning_ids = [x['customer'] for x in customer_order_counts if x['c'] >= 2]

        total_customers = orders.values('customer').distinct().count()
        returning_customers = len(returning_ids)
        retention_rate = (returning_customers / total_customers * 100.0) if total_customers > 0 else 0.0

        # VIP = >= 3 orders in the period
        vip_ids = [x['customer'] for x in customer_order_counts if x['c'] >= 3]
        new_ids = list(
            User.objects.filter(date_joined__gte=start_date).values_list('id', flat=True)
        )

        def revenue_for(ids):
            return float(orders.filter(customer_id__in=ids).aggregate(s=Coalesce(Sum('total_amount'), Value(0)))['s'] or 0)

        data = {
            'vip': {
                'count': len(vip_ids),
                'revenue': revenue_for(vip_ids),
            },
            'regular': {
                'count': max(total_customers - len(vip_ids) - len(new_ids), 0),
                'revenue': revenue_for(list(set(orders.values_list('customer_id', flat=True)) - set(vip_ids) - set(new_ids))),
            },
            'new': {
                'count': len(new_ids),
                'revenue': revenue_for(new_ids),
            },
            'retention_rate': retention_rate,
        }

        return Response(data)

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Operational performance metrics"
    )
    @action(detail=False, methods=['get'])
    
    def performance(self, request):
        from orders.models import Order

        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)

        delivered = Order.objects.filter(created_at__gte=start_date, status='delivered', actual_delivery_time__isnull=False)

        # Average processing time in hours
        diffs = delivered.values_list('created_at', 'actual_delivery_time')
        if diffs:
            import math
            total_hours = 0.0
            for created, delivered_at in diffs:
                delta = delivered_at - created
                total_hours += (delta.total_seconds() / 3600.0)
            avg_hours = total_hours / len(diffs)
            processing_time = f"{avg_hours:.1f} hrs"
        else:
            processing_time = 'N/A'

        # Placeholders for satisfaction and website metrics (not tracked here)
        data = {
            'processing_time': processing_time,
            'processing_time_change': '0%',
            'satisfaction': 'N/A',
            'satisfaction_change': '0%',
            'website_performance': 'N/A',
            'website_performance_change': '0%'
        }
        return Response(data)
    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get sales analytics"
    )
    @action(detail=False, methods=['get'])
    
    def sales(self, request):
        """
        Get sales data for dashboard
        """
        from orders.models import Order
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Build paid orders queryset for this window
        from payments.models import PaymentTransaction
        paid_sum_subquery = PaymentTransaction.objects.filter(
            order_id=OuterRef('pk'),
            status__in=['successful', 'paid', 'done']
        ).values('order').annotate(
            s=Coalesce(
                Sum('amount'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).values('s')[:1]

        paid_orders = (
            Order.objects
            .filter(created_at__gte=start_date)
            .annotate(
                paid_total=Coalesce(
                    Subquery(
                        paid_sum_subquery,
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    ),
                    Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .filter(
                Q(payment_status__in=['paid', 'completed', 'done']) |
                Q(paid_total__gte=F('total_amount'))
            )
        )

        # Sales data by date for paid orders
        sales_data = paid_orders.extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            amount=Sum('total_amount'),
            count=Count('id')
        ).order_by('date')
        
        # Convert to list format expected by frontend
        sales_list = []
        for item in sales_data:
            sales_list.append({
                'date': item['date'],
                'amount': float(item['amount']),
                'count': item['count']
            })
        
        return Response({'results': sales_list})

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get order status analytics"
    )
    @action(detail=False, methods=['get'])
    
    def order_status(self, request):
        """
        Get order status data for dashboard
        """
        from orders.models import Order
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Order status data
        order_status_data = Order.objects.filter(
            created_at__gte=start_date
        ).values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Convert to list format expected by frontend
        status_list = []
        for item in order_status_data:
            status_list.append({
                'status': item['status'],
                'count': item['count']
            })
        
        return Response({'results': status_list})

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get revenue analytics"
    )
    @action(detail=False, methods=['get'])
    
    def revenue(self, request):
        """
        Get revenue data for dashboard
        """
        from orders.models import Order
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Build paid orders queryset for this window
        from payments.models import PaymentTransaction
        paid_sum_subquery = PaymentTransaction.objects.filter(
            order_id=OuterRef('pk'),
            status__in=['successful', 'paid', 'done']
        ).values('order').annotate(
            s=Coalesce(
                Sum('amount'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).values('s')[:1]

        paid_orders = (
            Order.objects
            .filter(created_at__gte=start_date)
            .annotate(
                paid_total=Coalesce(
                    Subquery(
                        paid_sum_subquery,
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    ),
                    Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .filter(
                Q(payment_status='paid') |
                Q(status='delivered') |
                Q(paid_total__gte=F('total_amount'))
            )
        )

        # Revenue aggregates from paid orders
        revenue_data = paid_orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
            avg_order_value=Avg('total_amount')
        )
        
        return Response({
            'total_revenue': float(revenue_data['total_revenue'] or 0),
            'total_orders': revenue_data['total_orders'] or 0,
            'avg_order_value': float(revenue_data['avg_order_value'] or 0)
        })

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get top products analytics"
    )
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """
        Get top performing products for dashboard
        """
        from orders.models import Order, OrderItem
        from products.models import Product
        
        # Get date range
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Build paid orders queryset for this window
        from payments.models import PaymentTransaction
        paid_sum_subquery = PaymentTransaction.objects.filter(
            order_id=OuterRef('pk'),
            status__in=['successful', 'paid', 'done']
        ).values('order').annotate(
            s=Coalesce(
                Sum('amount'),
                Value(0),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        ).values('s')[:1]

        paid_orders = (
            Order.objects
            .filter(created_at__gte=start_date)
            .annotate(
                paid_total=Coalesce(
                    Subquery(
                        paid_sum_subquery,
                        output_field=DecimalField(max_digits=12, decimal_places=2)
                    ),
                    Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
            .filter(
                Q(payment_status='paid') |
                Q(status='delivered') |
                Q(paid_total__gte=F('total_amount'))
            )
        )

        # Top products by sales from paid orders
        top_products = OrderItem.objects.filter(
            order__in=paid_orders
        ).values(
            'product__name',
            'product__id'
        ).annotate(
            total_sales=Sum('total_price'),
            total_quantity=Sum('quantity')
        ).order_by('-total_sales')[:10]
        
        # Convert to list format
        products_list = []
        for item in top_products:
            products_list.append({
                'product_id': item['product__id'],
                'product_name': item['product__name'],
                'total_sales': float(item['total_sales']),
                'total_quantity': item['total_quantity']
            })
        
        return Response({'results': products_list})

    @swagger_auto_schema(
        tags=['analytics'],
        operation_description="Get recent orders analytics"
    )
    @action(detail=False, methods=['get'])
    def recent_orders(self, request):
        """
        Get recent orders for dashboard
        """
        from orders.models import Order
        
        # Get recent orders
        recent_orders = Order.objects.order_by('-created_at')[:10]
        
        # Convert to list format
        orders_list = []
        for order in recent_orders:
            orders_list.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_name': order.customer_name,
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat()
            })
        
        return Response({'results': orders_list})
