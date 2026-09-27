import secrets
import string
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates or updates the admin user with a strong random password.'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = 'admin@gmail.com'
        
        # Generate a strong 16-character password (letters and digits only)
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(16))
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
            }
        )
        
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f'{action} admin user: {email}'))
        self.stdout.write(self.style.WARNING(f'Admin Password: {password}'))
        self.stdout.write(self.style.WARNING('Please copy and save this password immediately. It is not stored anywhere else.'))
