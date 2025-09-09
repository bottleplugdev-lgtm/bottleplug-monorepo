from django.core.management.base import BaseCommand
from users.models import User
from django.db import transaction


class Command(BaseCommand):
    help = 'Create a test admin user for the dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@bottleplug.com',
            help='Email address for the admin user (default: admin@bottleplug.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Password for the admin user (default: admin123)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Admin User',
            help='Full name for the admin user (default: Admin User)'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']
        
        # Split name into first and last name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    existing_user = User.objects.get(email=email)
                    existing_user.is_staff = True
                    existing_user.is_admin = True
                    existing_user.is_superuser = True
                    existing_user.user_type = 'admin'
                    existing_user.set_password(password)
                    existing_user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated existing user: {email} with admin privileges'
                        )
                    )
                else:
                    # Create new admin user
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        is_staff=True,
                        is_admin=True,
                        is_superuser=True,
                        user_type='admin',
                        is_verified=True
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created admin user: {email}'
                        )
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nAdmin credentials:'
                        f'\nEmail: {email}'
                        f'\nPassword: {password}'
                        f'\n\nYou can now sign in to the dashboard at http://localhost:3001'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating admin user: {str(e)}'
                )
            )
            raise
