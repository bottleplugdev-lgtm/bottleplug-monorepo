# Overdue Invoice Background Task

This document describes the background task that automatically checks for overdue invoices and updates their status.

## Overview

The system includes a Django management command that runs daily at 00:00 to check all invoices and update their status to "overdue" if they meet specific criteria.

## Criteria for Marking Invoices as Overdue

An invoice is marked as "overdue" if **ALL** of the following conditions are met:

1. **Status is not "paid"** - Only invoices with status `draft` or `sent` are considered
2. **Due date is in the past** - The invoice's `due_date` is before the current date
3. **Order is not fully paid** - The total amount paid for the attached order is less than the order's total amount

## Files Created

### 1. Management Command
- **File**: `orders/management/commands/check_overdue_invoices.py`
- **Purpose**: Main command that performs the overdue invoice check
- **Usage**: `python manage.py check_overdue_invoices`

### 2. Setup Script
- **File**: `scripts/setup_overdue_invoice_cron.sh`
- **Purpose**: Helps configure the cron job to run daily at 00:00
- **Usage**: `./scripts/setup_overdue_invoice_cron.sh`

### 3. Test Script
- **File**: `scripts/test_overdue_invoices.py`
- **Purpose**: Test the overdue invoice logic without making changes
- **Usage**: `python scripts/test_overdue_invoices.py`

## Setup Instructions

### 1. Test the Command Manually

First, test the command to ensure it works correctly:

```bash
cd /path/to/your/django/project
source venv/bin/activate

# Test with dry-run (no changes made)
python manage.py check_overdue_invoices --dry-run --verbose

# Test with actual changes
python manage.py check_overdue_invoices --verbose
```

### 2. Set Up the Cron Job

Run the setup script to configure the cron job:

```bash
cd /path/to/your/django/project
chmod +x scripts/setup_overdue_invoice_cron.sh
./scripts/setup_overdue_invoice_cron.sh
```

### 3. Verify the Cron Job

Check that the cron job was added correctly:

```bash
crontab -l
```

You should see an entry like:
```
0 0 * * * cd /path/to/your/django/project && source venv/bin/activate && python manage.py check_overdue_invoices >> logs/overdue_invoices.log 2>&1
```

### 4. Create Logs Directory

Ensure the logs directory exists:

```bash
mkdir -p logs
```

## Command Options

The `check_overdue_invoices` command supports the following options:

- `--dry-run`: Show what would be updated without making changes
- `--verbose`: Show detailed output for each invoice processed

## Monitoring

### View Logs
```bash
tail -f logs/overdue_invoices.log
```

### Check Cron Job Status
```bash
crontab -l
```

### Manual Testing
```bash
python scripts/test_overdue_invoices.py
```

## Logic Details

### Invoice Selection
The command selects invoices that:
- Have status `draft` or `sent` (not `paid`, `overdue`, `cancelled`, etc.)
- Have a `due_date` that is in the past

### Payment Verification
For each selected invoice, the command:
1. Gets the attached order
2. Calculates total successful payments for that order
3. Compares total paid vs order total
4. Only marks as overdue if the order is NOT fully paid

### Safety Features
- **Dry-run mode**: Test without making changes
- **Error handling**: Logs errors and continues processing other invoices
- **Detailed logging**: Records all actions for audit purposes
- **Verbose output**: Shows detailed information for debugging

## Example Output

```
Starting overdue invoice check...
Found 5 invoices with due dates in the past

Invoice INV-20250101-ABC123: Order total: $1000.00, Total paid: $500.00, Fully paid: False
✅ Invoice INV-20250101-ABC123 marked as overdue (Order ORD-20250101-123: $500.00/$1000.00)

Invoice INV-20250101-DEF456: Order total: $500.00, Total paid: $500.00, Fully paid: True
⏭️  Invoice INV-20250101-DEF456: Order fully paid, skipping

==================================================
OVERDUE INVOICE CHECK SUMMARY
==================================================
Total invoices checked: 5
Invoices marked as overdue: 1
Invoices skipped: 4
✅ Overdue invoice check completed successfully
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Make sure the script is executable
   ```bash
   chmod +x scripts/setup_overdue_invoice_cron.sh
   ```

2. **Virtual environment not found**: Update the cron job path to match your venv location

3. **Logs not being written**: Ensure the logs directory exists and is writable

4. **Command not found**: Make sure you're in the correct Django project directory

### Manual Cron Job Setup

If the setup script doesn't work, you can manually add the cron job:

```bash
crontab -e
```

Add this line:
```
0 0 * * * cd /path/to/your/django/project && source venv/bin/activate && python manage.py check_overdue_invoices >> logs/overdue_invoices.log 2>&1
```

## Security Considerations

- The command only reads and updates invoice status
- No sensitive data is logged
- All actions are logged for audit purposes
- The command is idempotent (safe to run multiple times)

## Performance Considerations

- Uses database aggregation for efficient payment calculations
- Processes invoices in batches to avoid memory issues
- Includes error handling to prevent crashes
- Logs are rotated to prevent disk space issues 