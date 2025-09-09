from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from math import radians, cos, sin, asin, sqrt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import DeliveryRequest, DriverLocation, DeliveryZone, DriverSchedule, DeliveryRating
from .serializers import (
    DeliveryRequestSerializer, DeliveryRequestDetailSerializer, DeliveryRequestCreateSerializer,
    DeliveryRequestUpdateSerializer, DriverLocationSerializer, DriverLocationCreateSerializer,
    DeliveryZoneSerializer, DriverScheduleSerializer, DriverScheduleCreateSerializer,
    DeliveryRatingSerializer, DeliveryRatingCreateSerializer, DeliveryRequestFilterSerializer,
    DeliveryStatsSerializer, DeliveryZoneCheckSerializer, DeliveryFeeCalculatorSerializer
)


class DeliveryRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for delivery request management
    """
    queryset = DeliveryRequest.objects.all()
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['deliveries'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryRequestCreateSerializer
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return DeliveryRequestDetailSerializer
        return DeliveryRequestSerializer
    
    def get_queryset(self):
        """
        Filter delivery requests based on user type
        """
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return DeliveryRequest.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return DeliveryRequest.objects.none()
            
        if user.is_customer:
            return DeliveryRequest.objects.filter(customer=user)
        elif user.is_driver:
            return DeliveryRequest.objects.filter(driver=user)
        elif user.is_admin:
            return DeliveryRequest.objects.all()
        else:
            return DeliveryRequest.objects.none()
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Get current user's delivery requests"
    )
    @action(detail=False, methods=['get'])
    def my_deliveries(self, request):
        """Get current user's delivery requests"""
        if request.user.is_customer:
            deliveries = DeliveryRequest.objects.filter(customer=request.user)
        elif request.user.is_driver:
            deliveries = DeliveryRequest.objects.filter(driver=request.user)
        else:
            deliveries = DeliveryRequest.objects.all()
        
        deliveries = deliveries.order_by('-created_at')
        serializer = DeliveryRequestSerializer(deliveries, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Accept a delivery request (driver only)"
    )
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a delivery request (driver only)"""
        if not request.user.is_driver:
            return Response(
                {'error': 'Driver access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        delivery = self.get_object()
        
        if delivery.status != 'pending':
            return Response(
                {'error': 'Delivery request is not pending'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        delivery.driver = request.user
        delivery.status = 'accepted'
        delivery.accepted_at = timezone.now()
        delivery.save()
        
        return Response({'message': 'Delivery request accepted successfully'})
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Mark delivery as picked up (driver only)"
    )
    @action(detail=True, methods=['post'])
    def pickup(self, request, pk=None):
        """Mark delivery as picked up (driver only)"""
        if not request.user.is_driver:
            return Response(
                {'error': 'Driver access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        delivery = self.get_object()
        
        if delivery.driver != request.user:
            return Response(
                {'error': 'You can only update your own deliveries'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if delivery.status != 'accepted':
            return Response(
                {'error': 'Delivery must be accepted first'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        delivery.status = 'picked_up'
        delivery.picked_up_at = timezone.now()
        delivery.save()
        
        return Response({'message': 'Delivery marked as picked up'})
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Mark delivery as delivered (driver only)"
    )
    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Mark delivery as delivered (driver only)"""
        if not request.user.is_driver:
            return Response(
                {'error': 'Driver access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        delivery = self.get_object()
        
        if delivery.driver != request.user:
            return Response(
                {'error': 'You can only update your own deliveries'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if delivery.status != 'picked_up':
            return Response(
                {'error': 'Delivery must be picked up first'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        delivery.status = 'delivered'
        delivery.delivered_at = timezone.now()
        delivery.save()
        
        return Response({'message': 'Delivery marked as delivered'})
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Cancel a delivery request"
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a delivery request"""
        delivery = self.get_object()
        
        if delivery.status not in ['pending', 'accepted']:
            return Response(
                {'error': 'Delivery cannot be cancelled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cancel_reason = request.data.get('reason', 'Cancelled by user')
        delivery.status = 'cancelled'
        delivery.cancel_reason = cancel_reason
        delivery.cancelled_at = timezone.now()
        delivery.save()
        
        return Response({'message': 'Delivery cancelled successfully'})
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Get delivery statistics"
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get delivery statistics"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get delivery counts
        total_deliveries = DeliveryRequest.objects.count()
        pending_deliveries = DeliveryRequest.objects.filter(status='pending').count()
        completed_deliveries = DeliveryRequest.objects.filter(status='delivered').count()
        cancelled_deliveries = DeliveryRequest.objects.filter(status='cancelled').count()
        
        # Get delivery fees
        total_delivery_fees = DeliveryRequest.objects.filter(
            status='delivered'
        ).aggregate(total=Sum('delivery_fee'))['total'] or 0
        
        # Get average delivery time
        avg_delivery_time = DeliveryRequest.objects.filter(
            status='delivered',
            actual_time__isnull=False
        ).aggregate(avg=Avg('actual_time'))['avg'] or 0
        
        # Get average delivery distance
        avg_delivery_distance = DeliveryRequest.objects.filter(
            distance__isnull=False
        ).aggregate(avg=Avg('distance'))['avg'] or 0
        
        # Get active drivers
        from users.models import User
        active_drivers = User.objects.filter(
            user_type='driver',
            is_available=True
        ).count()
        
        # Get average driver rating
        avg_driver_rating = User.objects.filter(
            user_type='driver',
            rating__isnull=False
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        
        stats = {
            'total_deliveries': total_deliveries,
            'pending_deliveries': pending_deliveries,
            'completed_deliveries': completed_deliveries,
            'cancelled_deliveries': cancelled_deliveries,
            'total_delivery_fees': total_delivery_fees,
            'avg_delivery_time': avg_delivery_time,
            'avg_delivery_distance': avg_delivery_distance,
            'active_drivers': active_drivers,
            'avg_driver_rating': avg_driver_rating,
        }
        
        serializer = DeliveryStatsSerializer(stats)
        return Response(serializer.data)


class DriverLocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for driver location tracking
    """
    serializer_class = DriverLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['deliveries'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DriverLocationCreateSerializer
        return DriverLocationSerializer
    
    def get_queryset(self):
        """
        Filter driver locations based on user type
        """
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return DriverLocation.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return DriverLocation.objects.none()
            
        if user.is_driver:
            return DriverLocation.objects.filter(driver=user)
        elif user.is_admin:
            return DriverLocation.objects.all()
        else:
            return DriverLocation.objects.none()
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Update driver location"
    )
    @action(detail=False, methods=['post'])
    def update_location(self, request):
        """Update driver location"""
        if not request.user.is_driver:
            return Response(
                {'error': 'Driver access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = DriverLocationCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            location = serializer.save()
            return Response(DriverLocationSerializer(location).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Get current driver location"
    )
    @action(detail=False, methods=['get'])
    def current_location(self, request):
        """Get current driver location"""
        if not request.user.is_driver:
            return Response(
                {'error': 'Driver access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        latest_location = DriverLocation.objects.filter(
            driver=request.user
        ).order_by('-timestamp').first()
        
        if latest_location:
            serializer = DriverLocationSerializer(latest_location)
            return Response(serializer.data)
        else:
            return Response({'error': 'No location data available'}, status=status.HTTP_404_NOT_FOUND)


class DeliveryZoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for delivery zone management
    """
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['deliveries'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = DeliveryZone.objects.all()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Check if address is in delivery zone"
    )
    @action(detail=False, methods=['post'])
    def check_zone(self, request):
        """Check if coordinates are within a delivery zone"""
        serializer = DeliveryZoneCheckSerializer(data=request.data)
        if serializer.is_valid():
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            order_amount = serializer.validated_data.get('order_amount', 0)
            
            # Find matching zones
            matching_zones = []
            for zone in DeliveryZone.objects.filter(is_active=True):
                if zone.is_within_zone(latitude, longitude):
                    # Check minimum order amount
                    if order_amount >= zone.minimum_order_amount:
                        matching_zones.append({
                            'zone': DeliveryZoneSerializer(zone).data,
                            'delivery_fee': zone.base_delivery_fee
                        })
            
            return Response({
                'is_deliverable': len(matching_zones) > 0,
                'matching_zones': matching_zones
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Calculate delivery fee for address"
    )
    @action(detail=False, methods=['post'])
    def calculate_fee(self, request):
        """Calculate delivery fee based on coordinates"""
        serializer = DeliveryFeeCalculatorSerializer(data=request.data)
        if serializer.is_valid():
            pickup_lat = serializer.validated_data['pickup_latitude']
            pickup_lng = serializer.validated_data['pickup_longitude']
            delivery_lat = serializer.validated_data['delivery_latitude']
            delivery_lng = serializer.validated_data['delivery_longitude']
            order_amount = serializer.validated_data.get('order_amount', 0)
            
            # Calculate distance
            lat1, lon1 = radians(pickup_lat), radians(pickup_lng)
            lat2, lon2 = radians(delivery_lat), radians(delivery_lng)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance = 6371 * c  # Earth's radius in km
            
            # Find applicable zone
            applicable_zone = None
            for zone in DeliveryZone.objects.filter(is_active=True):
                if zone.is_within_zone(delivery_lat, delivery_lng):
                    if order_amount >= zone.minimum_order_amount:
                        applicable_zone = zone
                        break
            
            if applicable_zone:
                delivery_fee = applicable_zone.calculate_delivery_fee(distance)
            else:
                delivery_fee = 0
            
            return Response({
                'distance_km': round(distance, 2),
                'delivery_fee': delivery_fee,
                'applicable_zone': DeliveryZoneSerializer(applicable_zone).data if applicable_zone else None
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for driver schedule management
    """
    serializer_class = DriverScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['deliveries'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DriverScheduleCreateSerializer
        return DriverScheduleSerializer
    
    def get_queryset(self):
        """
        Filter driver schedules based on user type
        """
        # For drf_yasg schema generation
        if getattr(self, 'swagger_fake_view', False):
            return DriverSchedule.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return DriverSchedule.objects.none()
            
        if user.is_driver:
            return DriverSchedule.objects.filter(driver=user)
        elif user.is_admin:
            return DriverSchedule.objects.all()
        else:
            return DriverSchedule.objects.none()
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Get available drivers"
    )
    @action(detail=False, methods=['get'])
    def available_drivers(self, request):
        """Get available drivers for a specific time"""
        date = request.query_params.get('date')
        time = request.query_params.get('time')
        
        if not date or not time:
            return Response(
                {'error': 'Date and time parameters required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from users.models import User
        available_drivers = User.objects.filter(
            user_type='driver',
            is_available=True,
            schedules__date=date,
            schedules__start_time__lte=time,
            schedules__end_time__gte=time,
            schedules__is_available=True
        ).distinct()
        
        from users.serializers import UserSerializer
        serializer = UserSerializer(available_drivers, many=True)
        return Response(serializer.data)


class DeliveryRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for delivery ratings
    """
    queryset = DeliveryRating.objects.all()
    serializer_class = DeliveryRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags=['deliveries'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['deliveries'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryRatingCreateSerializer
        return DeliveryRatingSerializer
    
    def get_queryset(self):
        queryset = DeliveryRating.objects.select_related('customer', 'driver', 'delivery_request')
        
        # Filter by driver
        driver = self.request.query_params.get('driver', None)
        if driver:
            queryset = queryset.filter(driver_id=driver)
        
        # Filter by rating
        min_rating = self.request.query_params.get('min_rating', None)
        max_rating = self.request.query_params.get('max_rating', None)
        if min_rating:
            queryset = queryset.filter(rating__gte=min_rating)
        if max_rating:
            queryset = queryset.filter(rating__lte=max_rating)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a delivery rating"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check if customer already rated this delivery
            existing_rating = DeliveryRating.objects.filter(
                customer=request.user,
                delivery_request=serializer.validated_data['delivery_request']
            ).first()
            
            if existing_rating:
                return Response(
                    {'error': 'You have already rated this delivery'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            rating = serializer.save()
            return Response(DeliveryRatingSerializer(rating).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['deliveries'],
        operation_description="Get current user's delivery ratings"
    )
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """Get current user's ratings"""
        if request.user.is_customer:
            ratings = DeliveryRating.objects.filter(customer=request.user)
        elif request.user.is_driver:
            ratings = DeliveryRating.objects.filter(driver=request.user)
        else:
            ratings = DeliveryRating.objects.all()
        
        ratings = ratings.order_by('-created_at')
        serializer = DeliveryRatingSerializer(ratings, many=True)
        return Response(serializer.data)
