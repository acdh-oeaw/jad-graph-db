import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from tqdm import tqdm

from archiv.models import TextSnippet
from jad.models import JadRelation


class Command(BaseCommand):
    help = "create network graph"

    def handle(self, *args, **options):
        start_time = time.time()
        collection_title = "JAD sentences"
        vector_field = "embedding_nomic"
        amount = 3
        max_distance = 0.1
        items = TextSnippet.objects.filter(collection__title=collection_title)
        for x in tqdm(items, total=items.count()):
            source_id = x.text_id.split("-")[0]
            for y in x.find_similar(
                vector_field=vector_field,
                collection_title=collection_title,
                amount=amount,
            ):
                try:
                    if y.distance < max_distance and y.text_id != x.text_id:
                        target_id = y.text_id.split("-")[0]
                        JadRelation.objects.get_or_create(
                            source_id=source_id,
                            target_id=target_id,
                            distance=max_distance,
                        )
                except Exception as e:
                    print(f"failed to process {x.text_id} due to {e}")

        duration = time.time() - start_time
        print(f"done in {timedelta(seconds=int(duration))}")
