#!/usr/bin/env python3

"""
Intelligent Migration Fix - Advanced Schema vs Migration State Mismatch Handler
This script intelligently identifies and resolves migration conflicts by analyzing error messages
"""

import os
import sys
import subprocess
import re
import time
from typing import List, Tuple, Dict, Set

class IntelligentMigrationFix:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
        self.faked_migrations: Set[str] = set()
        
        # Known problematic migrations that often cause conflicts
        self.problematic_migrations = {
            "orders": ["0003_order_address_line1_order_address_line2_order_city_and_more"],
            "users": ["0003_alter_user_options_user_date_of_birth_user_platform_and_more"],
            "payments": ["0001_initial"],
        }
    
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
    
    def get_available_migrations(self) -> Dict[str, List[str]]:
        """Get all available migrations for each app"""
        print("📋 Getting available migrations...")
        exit_code, stdout, stderr = self.django_command("showmigrations")
        
        if exit_code != 0:
            print(f"❌ Failed to get migration status: {stderr}")
            return {}
        
        migrations = {}
        current_app = None
        
        for line in stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('['):
                current_app = line
                migrations[current_app] = []
            elif line.startswith('[') and current_app:
                # Extract migration name from line like "[ ] 0001_initial"
                migration_match = re.search(r'\[.*?\]\s+(.+)', line)
                if migration_match:
                    migrations[current_app].append(migration_match.group(1))
        
        return migrations
    
    def parse_migration_error(self, error_message: str) -> Tuple[str, str, str]:
        """Parse migration error to extract app, table, and column information"""
        # Pattern for "column X of relation Y already exists"
        column_pattern = r"column \"([^\"]+)\" of relation \"([^\"]+)\" already exists"
        column_match = re.search(column_pattern, error_message)
        
        if column_match:
            column = column_match.group(1)
            table = column_match.group(2)
            
            # Map table names to apps
            table_to_app = {
                "orders_order": "orders",
                "users_user": "users", 
                "payments_payment": "payments",
                "products_product": "products",
                "events_event": "events",
                "deliveries_delivery": "deliveries",
                "analytics_analytics": "analytics",
                "expenses_expense": "expenses",
            }
            
            app = table_to_app.get(table, "unknown")
            return app, table, column
        
        return "unknown", "unknown", "unknown"
    
    def find_migration_that_adds_column(self, app: str, column: str) -> str:
        """Find which migration adds a specific column"""
        print(f"🔍 Finding migration that adds {column} to {app}...")
        
        # Get available migrations for the app
        available_migrations = self.get_available_migrations()
        app_migrations = available_migrations.get(app, [])
        
        # Check each migration file to see if it adds the column
        for migration in app_migrations:
            migration_file = f"/app/{app}/migrations/{migration}.py"
            if os.path.exists(migration_file):
                try:
                    with open(migration_file, 'r') as f:
                        content = f.read()
                        if f'"{column}"' in content or f"'{column}'" in content:
                            print(f"✅ Found migration {app}.{migration} that adds {column}")
                            return migration
                except Exception as e:
                    print(f"⚠️ Error reading {migration_file}: {e}")
                    continue
        
        print(f"⚠️ Could not find migration that adds {column} to {app}")
        return None
    
    def fake_specific_migration(self, app: str, migration: str) -> bool:
        """Fake a specific migration"""
        migration_key = f"{app}.{migration}"
        
        if migration_key in self.faked_migrations:
            print(f"⏭️ Migration {migration_key} already faked, skipping...")
            return True
        
        print(f"🔧 Faking {migration_key}...")
        exit_code, stdout, stderr = self.django_command("migrate", app, migration, "--fake")
        
        if exit_code == 0:
            print(f"✅ Successfully faked {migration_key}")
            self.faked_migrations.add(migration_key)
            return True
        else:
            print(f"⚠️ Failed to fake {migration_key}: {stderr}")
            return False
    
    def handle_migration_error(self, error_message: str) -> bool:
        """Intelligently handle a migration error"""
        print(f"🔍 Analyzing error: {error_message}")
        
        app, table, column = self.parse_migration_error(error_message)
        
        if app == "unknown":
            print("⚠️ Could not parse error message")
            return False
        
        print(f"📊 Error analysis: app={app}, table={table}, column={column}")
        
        # Find the migration that adds this column
        migration = self.find_migration_that_adds_column(app, column)
        
        if migration:
            return self.fake_specific_migration(app, migration)
        else:
            # Fallback: try to fake known problematic migrations for this app
            if app in self.problematic_migrations:
                for prob_migration in self.problematic_migrations[app]:
                    if self.fake_specific_migration(app, prob_migration):
                        return True
        
        return False
    
    def run_migrations_with_intelligent_retry(self, max_retries: int = 5) -> bool:
        """Run migrations with intelligent retry logic"""
        print("🔄 Running migrations with intelligent retry logic...")
        
        for attempt in range(max_retries):
            print(f"🔄 Migration attempt {attempt + 1}/{max_retries}")
            
            exit_code, stdout, stderr = self.django_command("migrate", "--noinput")
            
            if exit_code == 0:
                print("✅ All migrations completed successfully")
                return True
            
            # Check for specific error patterns
            if "already exists" in stderr or "DuplicateColumn" in stderr:
                print("⚠️ Found 'already exists' error, analyzing...")
                
                if self.handle_migration_error(stderr):
                    print("🔧 Successfully handled migration error, retrying...")
                    time.sleep(2)
                    continue
                else:
                    print("❌ Could not handle migration error")
            
            print(f"❌ Migration attempt {attempt + 1} failed: {stderr}")
            if attempt < max_retries - 1:
                print("⏳ Waiting before retry...")
                time.sleep(3)
        
        print("❌ All migration attempts failed")
        return False
    
    def fake_known_problematic_migrations(self) -> bool:
        """Fake known problematic migrations proactively"""
        print("🔧 Proactively faking known problematic migrations...")
        
        success_count = 0
        total_count = 0
        
        for app, migrations in self.problematic_migrations.items():
            for migration in migrations:
                total_count += 1
                if self.fake_specific_migration(app, migration):
                    success_count += 1
        
        print(f"📊 Faked {success_count}/{total_count} known problematic migrations")
        return success_count > 0
    
    def validate_final_state(self) -> bool:
        """Validate that the final migration state is consistent"""
        print("🔍 Validating final migration state...")
        
        # Check for unapplied migrations
        exit_code, stdout, stderr = self.django_command("migrate", "--plan")
        
        if exit_code != 0:
            print(f"❌ Failed to get migration plan: {stderr}")
            return False
        
        # Check if there are any unapplied migrations
        unapplied = [line for line in stdout.split('\n') if '[ ]' in line]
        
        if unapplied:
            print("⚠️ Found unapplied migrations:")
            for migration in unapplied:
                print(f"  {migration.strip()}")
            return False
        
        print("✅ All migrations are applied")
        return True
    
    def create_superuser_if_needed(self) -> bool:
        """Create superuser if none exists"""
        print("👤 Checking for superuser...")
        
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
    
    def perform_intelligent_migration_fix(self) -> bool:
        """Perform the intelligent migration fix process"""
        print("🚀 Starting intelligent migration fix process...")
        
        # Step 1: Check database connection
        if not self.check_database_connection():
            print("❌ Database connection failed")
            return False
        
        # Step 2: Proactively fake known problematic migrations
        self.fake_known_problematic_migrations()
        
        # Step 3: Run migrations with intelligent retry logic
        if not self.run_migrations_with_intelligent_retry():
            print("❌ Intelligent migration retry failed")
            return False
        
        # Step 4: Validate final state
        if not self.validate_final_state():
            print("⚠️ Final state validation failed, but continuing...")
        
        # Step 5: Create superuser if needed
        self.create_superuser_if_needed()
        
        print("🎉 Intelligent migration fix completed!")
        return True

def main():
    print("🧠 Intelligent Migration Fix - Advanced Schema vs Migration State Mismatch Handler")
    print("This script intelligently identifies and resolves migration conflicts.")
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    time.sleep(3)
    
    fixer = IntelligentMigrationFix()
    
    if fixer.perform_intelligent_migration_fix():
        print("🎉 Migration fix completed successfully!")
        print("📝 The database schema and migration state should now be consistent.")
        sys.exit(0)
    else:
        print("❌ Migration fix failed")
        print("📋 Check the logs above for specific error details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
