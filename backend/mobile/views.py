from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product
from orders.models import Order
from products.serializers import ProductSerializer
from orders.serializers import OrderSerializer

class MobileProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(status='active')
    serializer_class = ProductSerializer
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_products = self.queryset.filter(is_featured=True)[:10]
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)

class MobileOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

class MobileAppConfigView(APIView):
    def get(self, request):
        config = {
            'app_version': '1.0.0',
            'force_update': False,
            'maintenance_mode': False,
            'features': {
                'push_notifications': True,
                'location_tracking': True,
                'payment_methods': ['card', 'mobile_money', 'cash']
            }
        }
        return Response(config)

class PushTokenView(APIView):
    def post(self, request):
        token = request.data.get('token')
        platform = request.data.get('platform', 'android')
        
        # Save push token to user profile
        request.user.push_token = token
        request.user.platform = platform
        request.user.save()
        
        return Response({'status': 'success'})