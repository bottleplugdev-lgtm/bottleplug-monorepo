#!/usr/bin/env python
"""
Test script for the overdue invoice management command
This script helps verify that the check_overdue_invoices command works correctly
"""

import os
import sys
import django
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanna_backend.settings')
django.setup()

from orders.models import Invoice
from payments.models import PaymentTransaction
from decimal import Decimal


def test_overdue_invoice_logic():
    """Test the logic for determining overdue invoices"""
    print("🧪 Testing overdue invoice logic...")
    
    # Get current date
    current_date = timezone.now()
    
    # Find invoices that are not paid and have due dates in the past
    overdue_candidates = Invoice.objects.filter(
        status__in=['draft', 'sent'],
        due_date__lt=current_date,
    ).select_related('order')
    
    print(f"Found {overdue_candidates.count()} invoices with due dates in the past")
    
    for invoice in overdue_candidates:
        print(f"\n📄 Invoice: {invoice.invoice_number}")
        print(f"   Status: {invoice.status}")
        print(f"   Due Date: {invoice.due_date}")
        
        order = invoice.order
        if order:
            print(f"   Order: {order.order_number}")
            print(f"   Order Total: ${order.total_amount}")
            
            # Calculate total paid for this order
            total_paid = PaymentTransaction.objects.filter(
                order=order,
                status='successful'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            print(f"   Total Paid: ${total_paid}")
            
            is_fully_paid = total_paid >= order.total_amount
            print(f"   Fully Paid: {is_fully_paid}")
            
            if not is_fully_paid:
                print("   ➡️  Would be marked as OVERDUE")
            else:
                print("   ➡️  Would be SKIPPED (order fully paid)")
        else:
            print("   ➡️  Would be SKIPPED (no order attached)")
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_overdue_invoice_logic() 