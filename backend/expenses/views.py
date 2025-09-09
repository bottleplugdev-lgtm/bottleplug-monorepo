from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Expense
from .serializers import ExpenseSerializer, ExpenseSummarySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().select_related('created_by')
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        # Optional filters: category, date_from, date_to, search
        category = self.request.query_params.get('category')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        search = self.request.query_params.get('search')
        if category:
            qs = qs.filter(category=category)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if search:
            qs = qs.filter(description__icontains=search)
        return qs

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = self.get_queryset()
        agg = qs.aggregate(total_expenses=Sum('amount'), count=Count('id'))
        data = {
            'total_expenses': str(agg['total_expenses'] or 0),
            'count': int(agg['count'] or 0),
        }
        return Response(data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        items = [{'value': key, 'label': label} for key, label in Expense.CATEGORY_CHOICES]
        return Response({'results': items})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        by_category = (
            qs.values('category')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('category')
        )
        results = [
            {
                'category': row['category'],
                'total': str(row['total'] or 0),
                'count': int(row['count'] or 0)
            }
            for row in by_category
        ]
        return Response({'results': results})

