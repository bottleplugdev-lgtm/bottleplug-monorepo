#!/usr/bin/env python3

"""
Simple Migration Fix - Uses Django's built-in --fake-initial flag
This is a simpler approach that leverages Django's built-in migration handling
"""

import os
import sys
import subprocess
import time
from typing import List, Tuple

class SimpleMigrationFix:
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
    
    def run_fake_initial_migrations(self) -> bool:
        """Run migrations with --fake-initial flag"""
        print("🔄 Running migrations with --fake-initial flag...")
        
        exit_code, stdout, stderr = self.django_command("migrate", "--fake-initial", "--noinput")
        
        if exit_code == 0:
            print("✅ Fake-initial migrations completed successfully")
            return True
        else:
            print(f"⚠️ Fake-initial migrations failed: {stderr}")
            return False
    
    def run_normal_migrations(self) -> bool:
        """Run normal migrations"""
        print("🔄 Running normal migrations...")
        
        exit_code, stdout, stderr = self.django_command("migrate", "--noinput")
        
        if exit_code == 0:
            print("✅ Normal migrations completed successfully")
            return True
        else:
            print(f"❌ Normal migrations failed: {stderr}")
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
    
    def perform_simple_migration_fix(self) -> bool:
        """Perform simple migration fix using --fake-initial"""
        print("🚀 Starting simple migration fix process...")
        
        # Step 1: Check database connection
        if not self.check_database_connection():
            print("❌ Database connection failed")
            return False
        
        # Step 2: Try fake-initial migrations first
        if self.run_fake_initial_migrations():
            print("✅ Fake-initial migrations succeeded")
        else:
            print("⚠️ Fake-initial migrations failed, trying normal migrations...")
        
        # Step 3: Run normal migrations
        if not self.run_normal_migrations():
            print("❌ Normal migrations failed")
            return False
        
        # Step 4: Create superuser
        self.create_superuser()
        
        # Step 5: Show final status
        self.show_migration_status()
        
        print("🎉 Simple migration fix completed!")
        return True

def main():
    print("🔧 Simple Migration Fix - Using Django's --fake-initial")
    print("This uses Django's built-in migration handling with --fake-initial flag.")
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(3)
    
    fixer = SimpleMigrationFix()
    
    if fixer.perform_simple_migration_fix():
        print("🎉 Migration fix completed successfully!")
        print("📝 The database should now be in a consistent state.")
        sys.exit(0)
    else:
        print("❌ Migration fix failed")
        print("📋 Check the logs above for specific error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
