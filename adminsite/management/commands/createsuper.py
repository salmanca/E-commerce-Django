from django.core.management.base import BaseCommand
from adminsite.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username="admin").exists():
            CustomUser.objects.create_superuser("admin", "admin@admin.com", "admin")