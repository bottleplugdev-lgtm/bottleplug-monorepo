#!/usr/bin/env python3

"""
Force Migration Fix - Direct Database Approach
Manually marks problematic migrations as applied in the database
"""

import os
import sys
import subprocess
from typing import List

class ForceMigrationFix:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
        
        # Migrations that need to be force-marked as applied
        self.problematic_migrations = [
            "users.0003_alter_user_options_user_date_of_birth_user_platform_and_more",
            "users.0004_user_is_worker_alter_user_is_staff",
            "users.0005_alter_usersession_session_token",
            "users.0006_add_is_admin_field",
            "users.0007_alter_user_profile_image",
        ]
    
    def run_django_shell_command(self, command: str) -> tuple[int, str, str]:
        """Run a Django shell command"""
        cmd = ["python", self.manage_py_path, "shell", "-c", command]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def force_mark_migration_as_applied(self, migration_name: str) -> bool:
        """Force mark a migration as applied in the database"""
        print(f"🔧 Force marking migration as applied: {migration_name}")
        
        # Extract app name and migration number
        parts = migration_name.split('.')
        if len(parts) < 2:
            print(f"❌ Invalid migration name format: {migration_name}")
            return False
        
        app_name = parts[0]
        migration_number = parts[1]
        
        # Django shell command to manually insert migration record
        command = f"""
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

try:
    recorder = MigrationRecorder(connection)
    recorder.record_applied(app_name="{app_name}", name="{migration_number}")
    print("SUCCESS: Migration marked as applied")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        
        exit_code, stdout, stderr = self.run_django_shell_command(command)
        
        if exit_code == 0 and "SUCCESS" in stdout:
            print(f"✅ Successfully marked {migration_name} as applied")
            return True
        else:
            print(f"⚠️ Failed to mark {migration_name}: {stderr}")
            return False
    
    def check_migration_status(self, migration_name: str) -> bool:
        """Check if a migration is marked as applied"""
        parts = migration_name.split('.')
        if len(parts) < 2:
            return False
        
        app_name = parts[0]
        migration_number = parts[1]
        
        command = f"""
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

try:
    recorder = MigrationRecorder(connection)
    applied = recorder.migration_qs.filter(app=app_name, name="{migration_number}").exists()
    print("APPLIED" if applied else "NOT_APPLIED")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        
        exit_code, stdout, stderr = self.run_django_shell_command(command)
        return "APPLIED" in stdout if exit_code == 0 else False
    
    def force_fix_all_migrations(self) -> bool:
        """Force fix all problematic migrations"""
        print("🚨 Starting force migration fix...")
        
        success_count = 0
        for migration in self.problematic_migrations:
            # Check if already applied
            if self.check_migration_status(migration):
                print(f"✅ {migration} is already marked as applied")
                success_count += 1
                continue
            
            # Force mark as applied
            if self.force_mark_migration_as_applied(migration):
                success_count += 1
        
        print(f"📊 Successfully fixed {success_count}/{len(self.problematic_migrations)} migrations")
        return success_count == len(self.problematic_migrations)
    
    def run_migrations_after_fix(self) -> bool:
        """Run migrations after force fixing"""
        print("🔄 Running migrations after force fix...")
        
        cmd = ["python", self.manage_py_path, "migrate", "--noinput"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("✅ Migrations completed successfully")
                return True
            else:
                print(f"⚠️ Migrations failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("❌ Migration command timed out")
            return False
        except Exception as e:
            print(f"❌ Migration command failed: {e}")
            return False
    
    def show_final_status(self):
        """Show final migration status"""
        print("\n📊 Final migration status:")
        cmd = ["python", self.manage_py_path, "showmigrations", "users"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(result.stdout)
        except Exception as e:
            print(f"Could not show status: {e}")

def main():
    print("🔧 Force Migration Fix - Direct Database Approach")
    
    fixer = ForceMigrationFix()
    
    # Step 1: Force mark problematic migrations as applied
    if not fixer.force_fix_all_migrations():
        print("⚠️ Some migrations could not be force-fixed")
    
    # Step 2: Try running migrations
    if fixer.run_migrations_after_fix():
        print("🎉 Migration fix completed successfully!")
        fixer.show_final_status()
        sys.exit(0)
    else:
        print("❌ Migration fix failed")
        fixer.show_final_status()
        sys.exit(1)

if __name__ == "__main__":
    main()
