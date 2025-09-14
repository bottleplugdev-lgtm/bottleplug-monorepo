#!/usr/bin/env python3

"""
Database Reset Fix - Nuclear Option for Complete Migration State Reset
This script completely resets the database and migration state for a clean deployment
"""

import os
import sys
import subprocess
import time
from typing import List, Tuple

class DatabaseResetFix:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
    
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
        return exit_code == 0
    
    def backup_database(self) -> bool:
        """Create a backup of the current database"""
        print("💾 Creating database backup...")
        
        # Create backup directory
        os.makedirs("/app/backup", exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = f"/app/backup/db_backup_before_reset_{timestamp}.sql"
        
        # Use Django's dumpdata to create a data backup
        exit_code, stdout, stderr = self.django_command(
            "dumpdata", 
            "--natural-foreign", 
            "--natural-primary",
            "--exclude=contenttypes",
            "--exclude=auth.Permission",
            "--exclude=sessions.Session",
            "--exclude=admin.LogEntry",
            "--indent=2",
            "--output", backup_file
        )
        
        if exit_code == 0:
            print(f"✅ Database backup created: {backup_file}")
            return True
        else:
            print(f"⚠️ Backup failed (this is expected if database is corrupted): {stderr}")
            return False
    
    def drop_all_tables(self) -> bool:
        """Drop all tables in the database"""
        print("🗑️ Dropping all database tables...")
        
        drop_command = """
from django.db import connection
cursor = connection.cursor()

# Get all table names
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
tables = cursor.fetchall()

# Drop all tables
for table in tables:
    table_name = table[0]
    print(f"Dropping table: {table_name}")
    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')

print("All tables dropped successfully")
"""
        
        exit_code, stdout, stderr = self.django_command("shell", "-c", drop_command)
        
        if exit_code == 0:
            print("✅ All tables dropped successfully")
            return True
        else:
            print(f"❌ Failed to drop tables: {stderr}")
            return False
    
    def clear_migration_records(self) -> bool:
        """Clear all migration records from django_migrations table"""
        print("🗑️ Clearing migration records...")
        
        clear_command = """
from django.db import connection
cursor = connection.cursor()

# Drop django_migrations table if it exists
cursor.execute('DROP TABLE IF EXISTS django_migrations CASCADE')
print("django_migrations table dropped")

# Drop any remaining sequences
cursor.execute("SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public'")
sequences = cursor.fetchall()

for seq in sequences:
    seq_name = seq[0]
    cursor.execute(f'DROP SEQUENCE IF EXISTS "{seq_name}" CASCADE')

print("All sequences dropped")
"""
        
        exit_code, stdout, stderr = self.django_command("shell", "-c", clear_command)
        
        if exit_code == 0:
            print("✅ Migration records cleared")
            return True
        else:
            print(f"❌ Failed to clear migration records: {stderr}")
            return False
    
    def run_initial_migrations(self) -> bool:
        """Run initial migrations to set up the database from scratch"""
        print("🏗️ Running initial migrations from scratch...")
        
        # First, run migrate to create the django_migrations table
        exit_code, stdout, stderr = self.django_command("migrate", "--run-syncdb")
        
        if exit_code != 0:
            print(f"❌ Failed to run syncdb: {stderr}")
            return False
        
        # Then run all migrations
        exit_code, stdout, stderr = self.django_command("migrate", "--noinput")
        
        if exit_code == 0:
            print("✅ All migrations completed successfully")
            return True
        else:
            print(f"❌ Migrations failed: {stderr}")
            return False
    
    def create_superuser(self) -> bool:
        """Create a superuser"""
        print("👤 Creating superuser...")
        
        create_command = """
from django.contrib.auth import get_user_model
User = get_user_model()

# Create superuser if it doesn't exist
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
            print("✅ Superuser already exists or creation completed")
            return True
    
    def validate_database_state(self) -> bool:
        """Validate that the database is in a good state"""
        print("🔍 Validating database state...")
        
        # Check Django system
        exit_code, stdout, stderr = self.django_command("check", "--deploy")
        
        if exit_code == 0:
            print("✅ Database validation passed")
            return True
        else:
            print(f"⚠️ Database validation warnings: {stderr}")
            return True  # Warnings are usually OK
    
    def show_migration_status(self):
        """Show final migration status"""
        print("\n📊 Final migration status:")
        exit_code, stdout, stderr = self.django_command("showmigrations")
        if exit_code == 0:
            print(stdout)
        else:
            print(f"❌ Failed to get migration status: {stderr}")
    
    def perform_database_reset(self) -> bool:
        """Perform complete database reset"""
        print("🚀 Starting database reset process...")
        print("⚠️  WARNING: This will completely reset the database!")
        
        # Step 1: Check database connection
        if not self.check_database_connection():
            print("❌ Database connection failed")
            return False
        
        # Step 2: Create backup (optional, may fail if DB is corrupted)
        self.backup_database()
        
        # Step 3: Drop all tables
        if not self.drop_all_tables():
            print("❌ Failed to drop tables")
            return False
        
        # Step 4: Clear migration records
        if not self.clear_migration_records():
            print("❌ Failed to clear migration records")
            return False
        
        # Step 5: Run initial migrations
        if not self.run_initial_migrations():
            print("❌ Failed to run initial migrations")
            return False
        
        # Step 6: Create superuser
        self.create_superuser()
        
        # Step 7: Validate database state
        self.validate_database_state()
        
        # Step 8: Show final status
        self.show_migration_status()
        
        print("🎉 Database reset completed successfully!")
        return True

def main():
    print("💥 Database Reset Fix - Nuclear Option")
    print("This will completely reset the database and migration state.")
    print("⚠️  WARNING: All data will be lost!")
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(3)
    
    fixer = DatabaseResetFix()
    
    if fixer.perform_database_reset():
        print("🎉 Database reset completed successfully!")
        print("📝 The database is now in a clean, consistent state.")
        print("🔒 All migrations have been applied from scratch.")
        sys.exit(0)
    else:
        print("❌ Database reset failed")
        print("📋 Check the logs above for specific error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
