#!/usr/bin/env python3

"""
SQL Migration Fix - Direct SQL Approach
Uses raw SQL to directly insert migration records into the database
"""

import os
import sys
import subprocess
from typing import List

class SQLMigrationFix:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
        
        # Migrations that need to be force-marked as applied
        self.problematic_migrations = [
            ("users", "0003_alter_user_options_user_date_of_birth_user_platform_and_more"),
            ("users", "0004_user_is_worker_alter_user_is_staff"),
            ("users", "0005_alter_usersession_session_token"),
            ("users", "0006_add_is_admin_field"),
            ("users", "0007_alter_user_profile_image"),
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
    
    def insert_migration_record(self, app_name: str, migration_name: str) -> bool:
        """Insert migration record directly using SQL"""
        print(f"🔧 Inserting migration record: {app_name}.{migration_name}")
        
        # SQL command to insert migration record
        command = f"""
from django.db import connection
import datetime

try:
    cursor = connection.cursor()
    # Check if migration already exists
    cursor.execute("SELECT id FROM django_migrations WHERE app = %s AND name = %s", [app_name, migration_name])
    if cursor.fetchone():
        print("ALREADY_EXISTS")
    else:
        # Insert migration record
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            [app_name, migration_name, datetime.datetime.now()]
        )
        print("SUCCESS")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
        
        exit_code, stdout, stderr = self.run_django_shell_command(command)
        
        if exit_code == 0:
            if "SUCCESS" in stdout:
                print(f"✅ Successfully inserted {app_name}.{migration_name}")
                return True
            elif "ALREADY_EXISTS" in stdout:
                print(f"✅ {app_name}.{migration_name} already exists")
                return True
            else:
                print(f"⚠️ Unexpected output: {stdout}")
                return False
        else:
            print(f"⚠️ Failed to insert {app_name}.{migration_name}: {stderr}")
            return False
    
    def fix_all_migrations(self) -> bool:
        """Fix all problematic migrations"""
        print("🚨 Starting SQL migration fix...")
        
        success_count = 0
        for app_name, migration_name in self.problematic_migrations:
            if self.insert_migration_record(app_name, migration_name):
                success_count += 1
        
        print(f"📊 Successfully fixed {success_count}/{len(self.problematic_migrations)} migrations")
        return success_count == len(self.problematic_migrations)
    
    def run_migrations_after_fix(self) -> bool:
        """Run migrations after SQL fix"""
        print("🔄 Running migrations after SQL fix...")
        
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
    print("🔧 SQL Migration Fix - Direct SQL Approach")
    
    fixer = SQLMigrationFix()
    
    # Step 1: Insert migration records directly
    if not fixer.fix_all_migrations():
        print("⚠️ Some migrations could not be fixed")
    
    # Step 2: Try running migrations
    if fixer.run_migrations_after_fix():
        print("🎉 SQL migration fix completed successfully!")
        fixer.show_final_status()
        sys.exit(0)
    else:
        print("❌ SQL migration fix failed")
        fixer.show_final_status()
        sys.exit(1)

if __name__ == "__main__":
    main()
