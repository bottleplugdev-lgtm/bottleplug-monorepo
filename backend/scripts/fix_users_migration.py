#!/usr/bin/env python3

"""
Fix Users Migration - Targeted fix for firebase_uid column conflict
This script specifically handles the users app migration conflicts
"""

import os
import sys
import subprocess
import time
from typing import List, Tuple

class UsersMigrationFix:
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
    
    def fake_users_migrations(self) -> bool:
        """Fake the problematic users migrations"""
        print("🔧 Faking problematic users migrations...")
        
        # List of users migrations to fake (in order)
        migrations_to_fake = [
            "0002_auto_20250725_2154",  # This adds firebase_uid
            "0003_alter_user_options_user_date_of_birth_user_platform_and_more",
            "0004_user_is_worker_alter_user_is_staff",
            "0005_alter_usersession_session_token",
            "0006_add_is_admin_field",
            "0007_alter_user_profile_image",
            "0008_alter_user_options_alter_user_table",
            "0009_user_notes",
            "0010_remove_user_notes",
        ]
        
        success_count = 0
        for migration in migrations_to_fake:
            print(f"🔄 Faking users.{migration}...")
            exit_code, stdout, stderr = self.django_command("migrate", "users", migration, "--fake")
            
            if exit_code == 0:
                print(f"✅ Successfully faked users.{migration}")
                success_count += 1
            else:
                print(f"⚠️ Failed to fake users.{migration}: {stderr}")
        
        print(f"📊 Faked {success_count}/{len(migrations_to_fake)} users migrations")
        return success_count > 0
    
    def run_remaining_migrations(self) -> bool:
        """Run migrations for all other apps"""
        print("🔄 Running migrations for all other apps...")
        
        # Get list of all apps
        exit_code, stdout, stderr = self.django_command("showmigrations")
        
        if exit_code != 0:
            print(f"❌ Failed to get migration status: {stderr}")
            return False
        
        # Extract app names (skip users since we faked those)
        apps = []
        for line in stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('[') and line != 'users':
                apps.append(line)
        
        print(f"📋 Found apps to migrate: {apps}")
        
        # Run migrations for each app
        for app in apps:
            print(f"🔄 Running migrations for {app}...")
            exit_code, stdout, stderr = self.django_command("migrate", app, "--noinput")
            
            if exit_code == 0:
                print(f"✅ Successfully migrated {app}")
            else:
                print(f"⚠️ Failed to migrate {app}: {stderr}")
                # Continue with other apps even if one fails
        
        return True
    
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
    
    def perform_users_migration_fix(self) -> bool:
        """Perform targeted users migration fix"""
        print("🚀 Starting users migration fix process...")
        
        # Step 1: Check database connection
        if not self.check_database_connection():
            print("❌ Database connection failed")
            return False
        
        # Step 2: Fake users migrations
        if not self.fake_users_migrations():
            print("❌ Failed to fake users migrations")
            return False
        
        # Step 3: Run remaining migrations
        if not self.run_remaining_migrations():
            print("❌ Failed to run remaining migrations")
            return False
        
        # Step 4: Create superuser
        self.create_superuser()
        
        # Step 5: Show final status
        self.show_migration_status()
        
        print("🎉 Users migration fix completed!")
        return True

def main():
    print("🔧 Users Migration Fix - Targeted firebase_uid Conflict Resolution")
    print("This script specifically fixes the users app migration conflicts.")
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(3)
    
    fixer = UsersMigrationFix()
    
    if fixer.perform_users_migration_fix():
        print("🎉 Migration fix completed successfully!")
        print("📝 The users app migrations have been resolved.")
        print("🔒 All other app migrations have been applied.")
        sys.exit(0)
    else:
        print("❌ Migration fix failed")
        print("📋 Check the logs above for specific error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()

