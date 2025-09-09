from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from products.models import Category
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

CATEGORY_EMOJI = {
    'Red Wine': '🍷',
    'White Wine': '🍾',
    'Champagne': '🥂',
    'Whisky': '🥃',
    'Vodka': '🍸',
    'Gin': '🍸',
    'Rum': '🥃',
    'Rosé': '🍷',
    'Beer': '🍺',
}

BACKGROUND_COLORS = {
    'Red Wine': (190, 0, 60),
    'White Wine': (230, 230, 210),
    'Champagne': (220, 200, 140),
    'Whisky': (120, 70, 20),
    'Vodka': (200, 220, 240),
    'Gin': (180, 220, 200),
    'Rum': (140, 90, 30),
    'Rosé': (245, 200, 210),
    'Beer': (240, 200, 80),
}

class Command(BaseCommand):
    help = 'Generate and assign icon images to categories'

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true', help='Regenerate and replace existing images')

    def handle(self, *args, **options):
        overwrite = options.get('overwrite', False)
        categories = Category.objects.all()
        if not categories.exists():
            self.stdout.write(self.style.WARNING('No categories found. Seed categories first.'))
            return

        updated = 0
        skipped = 0

        for category in categories:
            if category.image and not overwrite:
                skipped += 1
                continue
            try:
                img = self._make_icon_image(category.name)
                image_io = BytesIO()
                img.save(image_io, format='PNG')
                image_io.seek(0)
                file_name = f"{category.name.lower().replace(' ', '_')}_icon.png"
                category.image.save(file_name, ContentFile(image_io.read()), save=True)
                updated += 1
                self.stdout.write(self.style.SUCCESS(f"Assigned icon for {category.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to assign icon for {category.name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Done. Updated={updated}, Skipped={skipped}"))

    def _make_icon_image(self, name: str) -> Image.Image:
        width, height = 512, 512
        bg = BACKGROUND_COLORS.get(name, (230, 230, 230))
        fg = (20, 20, 20)
        accent = (255, 255, 255)

        img = Image.new('RGB', (width, height), color=bg)
        draw = ImageDraw.Draw(img)

        # Try to render emoji as large glyph, fallback to initial
        emoji = CATEGORY_EMOJI.get(name, '')
        try:
            font_emoji = ImageFont.truetype('DejaVuSans.ttf', 200)
        except Exception:
            font_emoji = ImageFont.load_default()

        center_y = height // 2 - 40
        if emoji and hasattr(draw, 'text'):
            tw, th = draw.textsize(emoji, font=font_emoji)
            draw.text(((width - tw) / 2, center_y - th // 2), emoji, fill=accent, font=font_emoji)
        else:
            # Draw initial letter
            initial = name[:1].upper()
            try:
                font_initial = ImageFont.truetype('DejaVuSans-Bold.ttf', 220)
            except Exception:
                font_initial = ImageFont.load_default()
            itw, ith = draw.textsize(initial, font=font_initial)
            draw.text(((width - itw) / 2, center_y - ith // 2), initial, fill=accent, font=font_initial)

        # Draw name banner at bottom
        banner_h = 90
        draw.rectangle([(0, height - banner_h), (width, height)], fill=(0, 0, 0, 160))
        try:
            font_name = ImageFont.truetype('DejaVuSans-Bold.ttf', 36)
        except Exception:
            font_name = ImageFont.load_default()
        label = name
        lw, lh = draw.textsize(label, font=font_name)
        draw.text(((width - lw) / 2, height - banner_h + (banner_h - lh) / 2), label, fill=(255, 255, 255), font=font_name)

        return img