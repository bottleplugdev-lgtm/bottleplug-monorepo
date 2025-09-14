#!/usr/bin/env python3

"""
Aggressive Database Reset - Complete Database Recreation
This script drops and recreates the entire database for a completely clean slate
"""

import os
import sys
import subprocess
import time
from typing import List, Tuple

class AggressiveDatabaseReset:
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
    
    def drop_and_recreate_database(self) -> bool:
        """Drop and recreate the entire database"""
        print("💥 Dropping and recreating entire database...")
        
        # Get database name from environment
        db_name = os.environ.get('POSTGRES_DB', 'bottleplug')
        db_user = os.environ.get('POSTGRES_USER', 'bottleplug')
        db_host = os.environ.get('POSTGRES_HOST', 'db')
        db_port = os.environ.get('POSTGRES_PORT', '5432')
        
        print(f"🗑️ Dropping database: {db_name}")
        
        # Connect to postgres database to drop the target database
        drop_command = f"""
import psycopg2
import os

# Connect to postgres database (not the target database)
conn = psycopg2.connect(
    host='{db_host}',
    port='{db_port}',
    user='{db_user}',
    password=os.environ.get('POSTGRES_PASSWORD', 'bottleplug123'),
    database='postgres'  # Connect to postgres database
)

conn.autocommit = True
cursor = conn.cursor()

# Terminate all connections to the target database
cursor.execute(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' AND pid <> pg_backend_pid()")

# Drop the database
cursor.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
print(f"Database {db_name} dropped")

# Create the database
cursor.execute(f'CREATE DATABASE "{db_name}"')
print(f"Database {db_name} created")

cursor.close()
conn.close()
print("Database recreation completed")
"""
        
        exit_code, stdout, stderr = self.django_command("shell", "-c", drop_command)
        
        if exit_code == 0:
            print("✅ Database dropped and recreated successfully")
            return True
        else:
            print(f"❌ Failed to recreate database: {stderr}")
            return False
    
    def run_migrations_from_scratch(self) -> bool:
        """Run migrations on the fresh database"""
        print("🏗️ Running migrations on fresh database...")
        
        # Run migrations
        exit_code, stdout, stderr = self.django_command("migrate", "--noinput")
        
        if exit_code == 0:
            print("✅ Migrations completed successfully")
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
        
        if "SUPERUSER_CREATED" in stdout or "SUPERUSER_ALREADY_EXISTS" in stdout:
            print("✅ Superuser creation completed")
            return True
        else:
            print("⚠️ Superuser creation had issues, but continuing...")
            return True
    
    def show_migration_status(self):
        """Show final migration status"""
        print("\n📊 Final migration status:")
        exit_code, stdout, stderr = self.django_command("showmigrations")
        if exit_code == 0:
            print(stdout)
        else:
            print(f"❌ Failed to get migration status: {stderr}")
    
    def perform_aggressive_reset(self) -> bool:
        """Perform aggressive database reset"""
        print("🚀 Starting aggressive database reset process...")
        print("⚠️  WARNING: This will completely recreate the database!")
        
        # Step 1: Check database connection
        if not self.check_database_connection():
            print("❌ Database connection failed")
            return False
        
        # Step 2: Drop and recreate database
        if not self.drop_and_recreate_database():
            print("❌ Failed to recreate database")
            return False
        
        # Step 3: Run migrations on fresh database
        if not self.run_migrations_from_scratch():
            print("❌ Failed to run migrations")
            return False
        
        # Step 4: Create superuser
        self.create_superuser()
        
        # Step 5: Show final status
        self.show_migration_status()
        
        print("🎉 Aggressive database reset completed successfully!")
        return True

def main():
    print("💥 Aggressive Database Reset - Complete Database Recreation")
    print("This will drop and recreate the entire database for a completely clean slate.")
    print("⚠️  WARNING: All data will be lost!")
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(3)
    
    resetter = AggressiveDatabaseReset()
    
    if resetter.perform_aggressive_reset():
        print("🎉 Database reset completed successfully!")
        print("📝 The database is now completely fresh and clean.")
        print("🔒 All migrations have been applied to a new database.")
        sys.exit(0)
    else:
        print("❌ Database reset failed")
        print("📋 Check the logs above for specific error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
