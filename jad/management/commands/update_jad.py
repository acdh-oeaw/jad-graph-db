import time
from datetime import timedelta

import requests
from django.core.management.base import BaseCommand
from openai import BadRequestError, InternalServerError, OpenAI
from tqdm import tqdm

from archiv.models import Collection, TextSnippet
from archiv.utils import sentence_splitter, vectorize


class Command(BaseCommand):
    help = "import JAD full texts"

    def handle(self, *args, **options):
        # client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        # client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
        client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="llama-ccp")
        start_time = time.time()
        col, _ = Collection.objects.get_or_create(title="JAD sentences")
        url = "https://raw.githubusercontent.com/jerusalem-70-ad/jad-baserow-dump/refs/heads/main/json_dumps/occurrences.json"  # noqa
        data = requests.get(url).json()
        for _, value in tqdm(data.items()):
            text = value["text_paragraph"]
            text_id = value["jad_id"]
            if text:
                pass
            else:
                text = value["passage"]
            sentences = [x for x in sentence_splitter(text) if len(x) > 25]
            for i, x in enumerate(sentences, start=1):
                sent_id = f"{text_id}-{i:02}"
                snippet, _ = TextSnippet.objects.get_or_create(
                    collection=col,
                    text_id=sent_id,
                )
                snippet.content = x
                snippet.save()
                try:
                    vectorize(client, snippet, update=True)
                except (BadRequestError, InternalServerError) as e:
                    print(f"failed to process {text_id}, with text {len(x)} due to {e}")
        duration = time.time() - start_time
        print(f"done in {timedelta(seconds=int(duration))}")
