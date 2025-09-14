#!/usr/bin/env python3

"""
Production Migration Conflict Resolver
Automatically detects and resolves Django migration conflicts
"""

import os
import sys
import subprocess
import re
from typing import List, Optional

class MigrationResolver:
    def __init__(self, manage_py_path: str = "manage.py"):
        self.manage_py_path = manage_py_path
        self.known_conflicts = [
            "users.0003_alter_user_options_user_date_of_birth_user_platform_and_more",
            "users.0004_user_is_worker_alter_user_is_staff", 
            "users.0005_alter_usersession_session_token",
            "users.0006_add_is_admin_field",
            "users.0007_alter_user_profile_image",
        ]
    
    def run_command(self, cmd: List[str]) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def django_command(self, *args) -> tuple[int, str, str]:
        """Run a Django management command"""
        cmd = ["python", self.manage_py_path] + list(args)
        return self.run_command(cmd)
    
    def get_unapplied_migrations(self) -> List[str]:
        """Get list of unapplied migrations"""
        exit_code, stdout, stderr = self.django_command("showmigrations", "--plan")
        if exit_code != 0:
            print(f"⚠️ Could not get migration status: {stderr}")
            return []
        
        unapplied = []
        for line in stdout.split('\n'):
            if '[ ]' in line:  # Unapplied migration
                match = re.search(r'[ ]*\[ \] (.+)', line)
                if match:
                    unapplied.append(match.group(1))
        
        return unapplied
    
    def fake_migration(self, migration_name: str) -> bool:
        """Fake a specific migration"""
        print(f"🎭 Faking migration: {migration_name}")
        exit_code, stdout, stderr = self.django_command("migrate", "--fake", migration_name)
        
        if exit_code == 0:
            print(f"✅ Successfully faked: {migration_name}")
            return True
        else:
            print(f"⚠️ Failed to fake {migration_name}: {stderr}")
            # Try alternative approach - fake with --fake-initial
            print(f"🔄 Trying alternative fake approach for {migration_name}")
            exit_code2, stdout2, stderr2 = self.django_command("migrate", "--fake-initial", migration_name)
            if exit_code2 == 0:
                print(f"✅ Successfully faked with --fake-initial: {migration_name}")
                return True
            else:
                print(f"❌ Both fake attempts failed for {migration_name}")
                return False
    
    def try_migrate(self) -> tuple[bool, str]:
        """Try to run migrations, return success status and error message"""
        print("🔄 Running migrations...")
        exit_code, stdout, stderr = self.django_command("migrate", "--noinput")
        
        if exit_code == 0:
            print("✅ Migrations completed successfully")
            return True, ""
        else:
            return False, stderr
    
    def extract_conflicting_migration(self, error_output: str) -> Optional[str]:
        """Extract the name of the conflicting migration from error output"""
        patterns = [
            r'Applying ([^.]+\.[^.]+[^.]*)',
            r'Migration ([^.]+\.[^.]+[^.]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_output)
            if match:
                return match.group(1)
        
        return None
    
    def resolve_conflicts(self) -> bool:
        """Main method to resolve migration conflicts"""
        print("🗄️ Starting automatic migration conflict resolution...")
        
        # Step 1: Try normal migration
        success, error = self.try_migrate()
        if success:
            return True
        
        # Step 2: Check if it's a column conflict
        if "already exists" not in error:
            print(f"❌ Migration failed with non-column error: {error}")
            return False
        
        print("⚠️ Column conflicts detected, resolving...")
        
        # Step 3: Fake known conflicting migrations
        unapplied = self.get_unapplied_migrations()
        faked_any = False
        
        for migration in self.known_conflicts:
            if migration in unapplied:
                if self.fake_migration(migration):
                    faked_any = True
        
        # Step 4: Try migration again
        if faked_any:
            success, error = self.try_migrate()
            if success:
                return True
        
        # Step 5: Auto-detect and fake remaining conflicts
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            success, error = self.try_migrate()
            
            if success:
                return True
            
            if "already exists" in error:
                conflicting_migration = self.extract_conflicting_migration(error)
                if conflicting_migration:
                    print(f"🔍 Detected conflicting migration: {conflicting_migration}")
                    if self.fake_migration(conflicting_migration):
                        continue  # Try again
                
            print(f"❌ Could not resolve conflicts after {attempt} attempts")
            print(f"Last error: {error}")
            break
        
        # Step 6: Last resort - fake ALL known problematic migrations aggressively
        print("🚨 Last resort: Aggressively faking ALL known problematic migrations...")
        for migration in self.known_conflicts:
            print(f"🎭 Force faking: {migration}")
            # Try multiple approaches
            self.django_command("migrate", "--fake", migration)
            self.django_command("migrate", "--fake-initial", migration)
        
        # Final attempt
        success, error = self.try_migrate()
        if success:
            return True
        
        return False
    
    def show_final_status(self):
        """Show final migration status"""
        print("\n📊 Final migration status:")
        exit_code, stdout, stderr = self.django_command("showmigrations", "--verbosity=1")
        if stdout:
            print(stdout)

def main():
    resolver = MigrationResolver()
    
    if resolver.resolve_conflicts():
        print("🎉 All migration conflicts resolved successfully!")
        resolver.show_final_status()
        sys.exit(0)
    else:
        print("❌ Failed to resolve all migration conflicts")
        resolver.show_final_status()
        sys.exit(1)

if __name__ == "__main__":
    main()
