import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from tqdm import tqdm

from archiv.models import Collection, TextSnippet


class Command(BaseCommand):
    help = "import JAD sentences"

    def handle(self, *args, **options):
        start_time = time.time()
        col, _ = Collection.objects.get_or_create(title="JAD sentences")
        items = TextSnippet.objects.filter(collection__title="JAD sentences")
        for item in tqdm(items, total=len(items)):
            try:
                item.embedd_content()
            except Exception as e:
                print(f"failed to enrich {item.text_id} due to {e}")
        duration = time.time() - start_time
        print(f"done in {timedelta(seconds=int(duration))}")
