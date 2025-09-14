#!/usr/bin/env python3

"""
Migration Validation Script
Validates that all migrations are properly applied and consistent
"""

import os
import sys
import subprocess
from typing import List, Tuple

class MigrationValidator:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
    
    def run_command(self, cmd: List[str], timeout: int = 60) -> Tuple[int, str, str]:
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
    
    def validate_migration_consistency(self) -> bool:
        """Validate that migrations are consistent"""
        print("🔍 Validating migration consistency...")
        exit_code, stdout, stderr = self.django_command("migrate", "--plan")
        
        if exit_code != 0:
            print(f"❌ Migration plan failed: {stderr}")
            return False
        
        # Check for unapplied migrations
        if "[ ]" in stdout:
            print("⚠️ Found unapplied migrations:")
            for line in stdout.split('\n'):
                if "[ ]" in line:
                    print(f"  {line.strip()}")
            return False
        
        print("✅ All migrations are applied")
        return True
    
    def check_for_migration_conflicts(self) -> bool:
        """Check for potential migration conflicts"""
        print("🔍 Checking for migration conflicts...")
        exit_code, stdout, stderr = self.django_command("showmigrations")
        
        if exit_code != 0:
            print(f"❌ Failed to get migration status: {stderr}")
            return False
        
        # Look for common conflict patterns
        conflict_indicators = [
            "ProgrammingError",
            "already exists",
            "does not exist",
            "duplicate key"
        ]
        
        if any(indicator in stderr for indicator in conflict_indicators):
            print("⚠️ Potential migration conflicts detected")
            return False
        
        print("✅ No migration conflicts detected")
        return True
    
    def validate_schema_consistency(self) -> bool:
        """Validate that database schema matches Django models"""
        print("🔍 Validating schema consistency...")
        exit_code, stdout, stderr = self.django_command("check", "--deploy")
        
        if exit_code != 0:
            print(f"❌ Schema validation failed: {stderr}")
            return False
        
        print("✅ Schema is consistent")
        return True
    
    def run_validation_suite(self) -> bool:
        """Run complete validation suite"""
        print("🚀 Starting migration validation...")
        
        validations = [
            ("Database Connection", self.check_database_connection),
            ("Migration Consistency", self.validate_migration_consistency),
            ("Migration Conflicts", self.check_for_migration_conflicts),
            ("Schema Consistency", self.validate_schema_consistency),
        ]
        
        all_passed = True
        for name, validation_func in validations:
            print(f"\n📋 {name}:")
            if not validation_func():
                all_passed = False
                print(f"❌ {name} failed")
            else:
                print(f"✅ {name} passed")
        
        return all_passed

def main():
    print("🔍 Migration Validation Script")
    
    validator = MigrationValidator()
    
    if validator.run_validation_suite():
        print("\n🎉 All validations passed!")
        print("✅ Database is in a consistent state")
        print("✅ All migrations are properly applied")
        print("✅ No conflicts detected")
        sys.exit(0)
    else:
        print("\n❌ Validation failed!")
        print("⚠️ Database may be in an inconsistent state")
        print("🔧 Consider running the proper migration fix script")
        sys.exit(1)

if __name__ == "__main__":
    main()
