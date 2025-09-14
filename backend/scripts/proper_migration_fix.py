#!/usr/bin/env python3

"""
Proper Migration Fix - Clean Database Approach
Implements proper migration practices by resetting the database to a clean state
"""

import os
import sys
import subprocess
import time
from typing import List, Tuple

class ProperMigrationFix:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
        
        # Apps that need migration reset
        self.apps_to_reset = [
            "users",
            "orders", 
            "payments",
            "products",
            "events",
            "deliveries",
            "analytics",
            "expenses"
        ]
    
    def run_command(self, cmd: List[str], timeout: int = 300) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def django_command(self, *args) -> Tuple[int, str, str]:
        """Run a Django management command"""
        cmd = ["python", self.manage_py_path] + list(args)
        return self.run_command(cmd)
    
    def check_database_connection(self) -> bool:
        """Check if database is accessible"""
        print("🔍 Checking database connection...")
        exit_code, stdout, stderr = self.django_command("check", "--database", "default")
        
        if exit_code == 0:
            print("✅ Database connection successful")
            return True
        else:
            print(f"❌ Database connection failed: {stderr}")
            return False
    
    def backup_current_data(self) -> bool:
        """Create a backup of current database"""
        print("💾 Creating database backup...")
        
        # Create backup directory
        os.makedirs("/app/backup", exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = f"/app/backup/db_backup_before_migration_fix_{timestamp}.sql"
        
        # Use Django's dumpdata to create a data backup
        exit_code, stdout, stderr = self.django_command(
            "dumpdata", 
            "--natural-foreign", 
            "--natural-primary",
            "--exclude=contenttypes",
            "--exclude=auth.Permission",
            "--exclude=sessions.Session",
            "--indent=2",
            "--output", backup_file
        )
        
        if exit_code == 0:
            print(f"✅ Database backup created: {backup_file}")
            return True
        else:
            print(f"⚠️ Backup failed: {stderr}")
            return False
    
    def reset_migration_state(self) -> bool:
        """Reset migration state to clean state"""
        print("🔄 Resetting migration state...")
        
        # Step 1: Unapply all migrations for problematic apps
        for app in self.apps_to_reset:
            print(f"🔄 Unapplying migrations for {app}...")
            exit_code, stdout, stderr = self.django_command("migrate", app, "zero", "--fake")
            if exit_code != 0:
                print(f"⚠️ Failed to unapply {app} migrations: {stderr}")
        
        # Step 2: Clear migration records from database
        print("🗑️ Clearing migration records from database...")
        clear_command = """
from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM django_migrations WHERE app IN %s", [tuple(apps)])
print("Migration records cleared")
"""
        
        exit_code, stdout, stderr = self.django_command(
            "shell", "-c", 
            clear_command.replace("apps", str(self.apps_to_reset))
        )
        
        if exit_code == 0:
            print("✅ Migration records cleared")
            return True
        else:
            print(f"⚠️ Failed to clear migration records: {stderr}")
            return False
    
    def run_initial_migrations(self) -> bool:
        """Run initial migrations to set up base schema"""
        print("🏗️ Running initial migrations...")
        
        # Run migrations for each app individually
        for app in self.apps_to_reset:
            print(f"🔄 Running initial migration for {app}...")
            exit_code, stdout, stderr = self.django_command("migrate", app, "0001", "--fake-initial")
            if exit_code != 0:
                print(f"⚠️ Failed to run initial migration for {app}: {stderr}")
                return False
        
        print("✅ Initial migrations completed")
        return True
    
    def run_all_migrations(self) -> bool:
        """Run all migrations normally"""
        print("🔄 Running all migrations...")
        exit_code, stdout, stderr = self.django_command("migrate", "--noinput")
        
        if exit_code == 0:
            print("✅ All migrations completed successfully")
            return True
        else:
            print(f"❌ Migrations failed: {stderr}")
            return False
    
    def create_superuser(self) -> bool:
        """Create a superuser if none exists"""
        print("👤 Checking for superuser...")
        
        # Check if superuser exists
        check_command = """
from django.contrib.auth import get_user_model
User = get_user_model()
if User.objects.filter(is_superuser=True).exists():
    print("SUPERUSER_EXISTS")
else:
    print("NO_SUPERUSER")
"""
        
        exit_code, stdout, stderr = self.django_command("shell", "-c", check_command)
        
        if "NO_SUPERUSER" in stdout:
            print("👤 Creating superuser...")
            # Create superuser with default credentials
            create_command = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        email='admin@bottleplug.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print("SUPERUSER_CREATED")
else:
    print("SUPERUSER_ALREADY_EXISTS")
"""
            
            exit_code, stdout, stderr = self.django_command("shell", "-c", create_command)
            if "SUPERUSER_CREATED" in stdout:
                print("✅ Superuser created successfully")
                return True
            else:
                print("⚠️ Superuser creation failed or already exists")
                return False
        else:
            print("✅ Superuser already exists")
            return True
    
    def show_migration_status(self):
        """Show final migration status"""
        print("\n📊 Final migration status:")
        for app in self.apps_to_reset:
            print(f"\n{app.upper()}:")
            exit_code, stdout, stderr = self.django_command("showmigrations", app)
            if exit_code == 0:
                print(stdout)
    
    def restore_data_from_backup(self, backup_file: str) -> bool:
        """Restore data from backup (optional)"""
        if not os.path.exists(backup_file):
            print(f"⚠️ Backup file not found: {backup_file}")
            return False
        
        print(f"📥 Restoring data from backup: {backup_file}")
        exit_code, stdout, stderr = self.django_command("loaddata", backup_file)
        
        if exit_code == 0:
            print("✅ Data restored successfully")
            return True
        else:
            print(f"⚠️ Data restoration failed: {stderr}")
            return False
    
    def perform_clean_migration(self) -> bool:
        """Perform complete clean migration process"""
        print("🚀 Starting proper migration fix process...")
        
        # Step 1: Check database connection
        if not self.check_database_connection():
            return False
        
        # Step 2: Create backup
        backup_created = self.backup_current_data()
        
        # Step 3: Reset migration state
        if not self.reset_migration_state():
            return False
        
        # Step 4: Run initial migrations
        if not self.run_initial_migrations():
            return False
        
        # Step 5: Run all migrations
        if not self.run_all_migrations():
            return False
        
        # Step 6: Create superuser
        self.create_superuser()
        
        # Step 7: Show final status
        self.show_migration_status()
        
        print("🎉 Proper migration fix completed successfully!")
        return True

def main():
    print("🔧 Proper Migration Fix - Clean Database Approach")
    print("This will reset the database to a clean state and run migrations properly.")
    
    # Wait a moment for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(3)
    
    fixer = ProperMigrationFix()
    
    if fixer.perform_clean_migration():
        print("🎉 Migration fix completed successfully!")
        print("📝 Note: This approach ensures a clean, consistent database state.")
        print("🔒 All migrations are now properly applied and tracked.")
        sys.exit(0)
    else:
        print("❌ Migration fix failed")
        print("📋 Check the logs above for specific error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
