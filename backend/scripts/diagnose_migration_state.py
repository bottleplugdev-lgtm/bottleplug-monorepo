#!/usr/bin/env python3

"""
Migration State Diagnostic Script
Helps diagnose the current state of migrations vs database schema
"""

import os
import sys
import subprocess
from typing import Dict, List

class MigrationDiagnostic:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
    
    def run_command(self, cmd: List[str], timeout: int = 60) -> tuple:
        """Run a shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def django_command(self, *args) -> tuple:
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
    
    def get_migration_status(self) -> Dict[str, List[str]]:
        """Get detailed migration status"""
        print("📊 Getting migration status...")
        exit_code, stdout, stderr = self.django_command("showmigrations")
        
        if exit_code != 0:
            print(f"❌ Failed to get migration status: {stderr}")
            return {}
        
        status = {}
        current_app = None
        
        for line in stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('['):
                current_app = line
                status[current_app] = []
            elif line.startswith('[') and current_app:
                status[current_app].append(line)
        
        return status
    
    def get_migration_plan(self) -> List[str]:
        """Get migration plan"""
        print("📋 Getting migration plan...")
        exit_code, stdout, stderr = self.django_command("migrate", "--plan")
        
        if exit_code != 0:
            print(f"❌ Failed to get migration plan: {stderr}")
            return []
        
        return stdout.split('\n')
    
    def check_specific_tables(self) -> Dict[str, bool]:
        """Check if specific tables exist in the database"""
        print("🔍 Checking specific tables...")
        
        tables_to_check = [
            "orders_order",
            "users_user", 
            "payments_payment",
            "products_product",
            "django_migrations"
        ]
        
        table_status = {}
        
        for table in tables_to_check:
            check_command = f"""
from django.db import connection
cursor = connection.cursor()
try:
    cursor.execute("SELECT 1 FROM {table} LIMIT 1")
    print("EXISTS")
except Exception as e:
    print("NOT_EXISTS")
"""
            
            exit_code, stdout, stderr = self.django_command("shell", "-c", check_command)
            
            if "EXISTS" in stdout:
                table_status[table] = True
                print(f"✅ Table {table} exists")
            else:
                table_status[table] = True
                print(f"❌ Table {table} does not exist")
        
        return table_status
    
    def check_specific_columns(self) -> Dict[str, bool]:
        """Check if specific columns exist in the orders table"""
        print("🔍 Checking specific columns in orders table...")
        
        columns_to_check = [
            "address_line1",
            "address_line2", 
            "city",
            "country",
            "district"
        ]
        
        column_status = {}
        
        for column in columns_to_check:
            check_command = f"""
from django.db import connection
cursor = connection.cursor()
try:
    cursor.execute("SELECT {column} FROM orders_order LIMIT 1")
    print("EXISTS")
except Exception as e:
    print("NOT_EXISTS")
"""
            
            exit_code, stdout, stderr = self.django_command("shell", "-c", check_command)
            
            if "EXISTS" in stdout:
                column_status[column] = True
                print(f"✅ Column {column} exists in orders table")
            else:
                column_status[column] = False
                print(f"❌ Column {column} does not exist in orders table")
        
        return column_status
    
    def get_django_migrations_records(self) -> List[str]:
        """Get records from django_migrations table"""
        print("📋 Getting django_migrations records...")
        
        query_command = """
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY app, name")
records = cursor.fetchall()
for record in records:
    print(f"{record[0]}.{record[1]} - {record[2]}")
"""
        
        exit_code, stdout, stderr = self.django_command("shell", "-c", query_command)
        
        if exit_code == 0:
            return stdout.split('\n')
        else:
            print(f"❌ Failed to get migration records: {stderr}")
            return []
    
    def run_full_diagnostic(self) -> bool:
        """Run complete diagnostic"""
        print("🚀 Starting migration state diagnostic...")
        
        # Check database connection
        if not self.check_database_connection():
            return False
        
        # Get migration status
        status = self.get_migration_status()
        print("\n📊 Migration Status:")
        for app, migrations in status.items():
            print(f"\n{app}:")
            for migration in migrations:
                print(f"  {migration}")
        
        # Get migration plan
        plan = self.get_migration_plan()
        print("\n📋 Migration Plan:")
        for line in plan:
            if line.strip():
                print(f"  {line}")
        
        # Check specific tables
        table_status = self.check_specific_tables()
        print(f"\n🔍 Table Status: {table_status}")
        
        # Check specific columns
        column_status = self.check_specific_columns()
        print(f"\n🔍 Column Status: {column_status}")
        
        # Get migration records
        records = self.get_django_migrations_records()
        print("\n📋 Django Migration Records:")
        for record in records:
            if record.strip():
                print(f"  {record}")
        
        return True

def main():
    print("🔍 Migration State Diagnostic Tool")
    print("This tool helps diagnose the current state of migrations vs database schema.")
    
    diagnostic = MigrationDiagnostic()
    
    if diagnostic.run_full_diagnostic():
        print("\n🎉 Diagnostic completed successfully!")
        print("📝 Review the output above to understand the current state.")
    else:
        print("\n❌ Diagnostic failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
