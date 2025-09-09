from django.core.management.base import BaseCommand
from django.db import transaction as db_transaction
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Remove orphan payment_receipts and create missing ones for successful payment transactions."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry_run', action='store_true', help='Show what would change without applying it'
        )

    def handle(self, *args, **options):
        from payments.models import PaymentReceipt, PaymentTransaction
        from payments.services import create_receipt_for_successful_payment

        dry_run = options.get('dry_run', False)

        # 1) Remove orphan payment_receipts (no linked transaction)
        # Note: model requires transaction, but guard anyway for historical rows
        orphans = PaymentReceipt.objects.filter(transaction__isnull=True)
        orphan_count = orphans.count()
        if dry_run:
            self.stdout.write(f"[DRY_RUN] Would delete {orphan_count} orphan payment_receipt(s)")
        else:
            deleted = orphans.delete()[0]
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} orphan payment_receipt(s)"))

        # 2) Create missing payment_receipts for successful transactions
        successful_statuses = ['successful', 'paid', 'done']
        candidates = (
            PaymentTransaction.objects
            .filter(status__in=successful_statuses)
            .select_related('order', 'invoice', 'event', 'payment_method')
        )

        created_count = 0
        skipped_count = 0
        for txn in candidates:
            # Check existing one_to_one relation
            if hasattr(txn, 'payment_receipt') and txn.payment_receipt is not None:
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(f"[DRY_RUN] Would create payment_receipt for transaction {txn.transaction_id}")
                created_count += 1
                continue

            with db_transaction.atomic():
                result = create_receipt_for_successful_payment(txn)
                if result.get('success') and result.get('receipt_created'):
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created payment_receipt {result.get('receipt_number')} for transaction {txn.transaction_id}"
                        )
                    )
                else:
                    skipped_count += 1
                    msg = result.get('message') or result.get('error') or 'unknown'
                    self.stdout.write(f"Skipped transaction {txn.transaction_id}: {msg}")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"payment_receipts created: {created_count}"))
        self.stdout.write(self.style.WARNING(f"payment_receipts skipped: {skipped_count}"))
