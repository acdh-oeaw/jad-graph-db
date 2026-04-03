import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from openai import OpenAI
from tqdm import tqdm

from archiv.models import Collection, TextSnippet


class Command(BaseCommand):
    help = "update vulgata vectors"

    def handle(self, *args, **options):
        total_start = time.time()
        processed_count = 0
        processed_token_total = 0
        processed_time_total = 0.0
        col, _ = Collection.objects.get_or_create(title="jad-english")
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        jad_sentence_col = Collection.objects.get(title="JAD sentences")
        latin_items = TextSnippet.objects.filter(collection=jad_sentence_col)
        for x in tqdm(latin_items, total=latin_items.count()):
            if len(x.content) > 1000:
                continue
            item, _ = TextSnippet.objects.get_or_create(
                text_id=x.text_id, collection=col
            )
            if item.content:
                continue
            start_time = time.time()
            completion = client.chat.completions.create(
                model="model-identifier",
                messages=[
                    {
                        "role": "system",
                        "content": "Translate the provided latin sentence into english. Just return the translation!",
                    },
                    {"role": "user", "content": x.content},
                ],
                temperature=0.0,
            )
            item.content = completion.choices[0].message.content
            item.save()
            duration = time.time() - start_time
            processed_count += 1
            processed_token_total += len(x.content.split())
            processed_time_total += duration
        total_duration = time.time() - total_start
        print(f"done in {timedelta(seconds=int(total_duration))}")
        if processed_count > 0:
            avg_tokens = processed_token_total / processed_count
            avg_processing_time = processed_time_total / processed_count
            print(f"processed items: {processed_count}")
            print(f"avg input length (tokens): {avg_tokens:.2f}")
            print(f"avg processing time per item: {avg_processing_time:.2f}s")
        else:
            print("processed items: 0")
            print("avg input length (tokens): n/a")
            print("avg processing time per item: n/a")
