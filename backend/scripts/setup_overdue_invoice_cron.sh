#!/bin/bash

# Setup script for overdue invoice cron job
# This script helps configure a cron job to run the overdue invoice check daily at 00:00

echo "Setting up overdue invoice cron job..."

# Get the current directory (should be the Django project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Project directory: $PROJECT_DIR"

# Create the cron job entry
CRON_JOB="0 0 * * * cd $PROJECT_DIR && source venv/bin/activate && python manage.py check_overdue_invoices >> logs/overdue_invoices.log 2>&1"

echo "Cron job to be added:"
echo "$CRON_JOB"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "check_overdue_invoices"; then
    echo "⚠️  Cron job for check_overdue_invoices already exists!"
    echo "Current cron jobs:"
    crontab -l | grep "check_overdue_invoices" || echo "No matching cron jobs found"
    echo ""
    echo "To update the cron job, you can:"
    echo "1. Remove the existing job: crontab -e"
    echo "2. Add the new job manually"
    echo ""
    echo "Or run this command to add the new job:"
    echo "(crontab -l 2>/dev/null; echo \"$CRON_JOB\") | crontab -"
else
    echo "Adding cron job..."
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job added successfully!"
fi

echo ""
echo "📋 Manual Setup Instructions:"
echo "1. Ensure the logs directory exists: mkdir -p $PROJECT_DIR/logs"
echo "2. Make sure the script is executable: chmod +x $PROJECT_DIR/manage.py"
echo "3. Test the command manually:"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python manage.py check_overdue_invoices --dry-run --verbose"
echo ""
echo "4. To view cron logs: tail -f $PROJECT_DIR/logs/overdue_invoices.log"
echo ""
echo "5. To list all cron jobs: crontab -l"
echo ""
echo "6. To edit cron jobs manually: crontab -e" 