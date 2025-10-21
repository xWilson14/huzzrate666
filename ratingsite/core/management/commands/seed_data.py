from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Item, Token
from django.contrib.auth.models import User  # ADD THIS IMPORT
import os
import random

ITEM_NAMES = []

TOKEN_WORDS = ["Dragon", "Sofa", "Potato", "Cucumber", "Icecream", "Shampoo", "Titan", "Chair", "Amogus", "Blackie","Nigga", "SmallPenis", "BigPenis"]


class Command(BaseCommand):
    help = "Seed items and use existing images"

    def handle(self, *args, **options):
        # CREATE SUPERUSER FIRST - ADD THIS SECTION
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('✅ Superuser created: admin/admin123'))
        else:
            self.stdout.write('✅ Superuser already exists')

        # Delete existing data
        Item.objects.all().delete()
        Token.objects.all().delete()

        created_items = []

        for name in ITEM_NAMES:
            # Create filename to match your images
            filename = name.replace(' ', '_').replace('-', '_').lower()

            # Create the item
            item = Item.objects.create(name=name)

            # Check if image file exists, then assign it
            # Try different extensions
            for ext in ['.jpg', '.jpeg', '.png', '.gif']:
                image_path = f"items/{filename}{ext}"
                full_path = os.path.join(settings.MEDIA_ROOT, image_path)

                if os.path.exists(full_path):
                    item.image.name = image_path
                    item.save()
                    self.stdout.write(self.style.SUCCESS(f"Assigned image to {name}"))
                    break
            else:
                self.stdout.write(self.style.WARNING(f"No image found for {name}"))

            created_items.append(item)

        # Create tokens
        tokens = []
        selected_words = random.sample(TOKEN_WORDS, 10)

        for word in selected_words:
            token_value = f"{word}{random.randint(100, 999)}"
            token = Token.objects.create(value=token_value, active=True)
            tokens.append(token_value)

        self.stdout.write(self.style.SUCCESS(f"Created {len(created_items)} items!"))
        self.stdout.write(self.style.SUCCESS("TOKENS (use these to login):"))
        self.stdout.write(self.style.SUCCESS("=" * 40))
        for i, t in enumerate(tokens, 1):
            self.stdout.write(self.style.SQL_FIELD(f"  {i:2d}. {t}"))
        self.stdout.write(self.style.SUCCESS("=" * 40))
        self.stdout.write(self.style.NOTICE("✅ Seed data completed!"))
