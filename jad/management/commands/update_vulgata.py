import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from openai import BadRequestError, InternalServerError, OpenAI
from tqdm import tqdm

from archiv.models import TextSnippet
from archiv.utils import vectorize


class Command(BaseCommand):
    help = "update vulgata vectors"

    def handle(self, *args, **options):
        start_time = time.time()
        # client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="llama-ccp")
        items = TextSnippet.objects.filter(collection__title="Vulgata")
        for item in tqdm(items, total=len(items)):
            try:
                vectorize(client, item, update=False)
            except (BadRequestError, InternalServerError) as e:
                print(
                    f"failed to process {item.text_id}, with text {len(item.content)} due to {e}"
                )
        duration = time.time() - start_time
        print(f"done in {timedelta(seconds=int(duration))}")
