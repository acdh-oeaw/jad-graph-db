from django.http import Http404, JsonResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view

from archiv.models import Collection, TextSnippet


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="vector-field",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Vector field to use for similarity search (default: embedding_nomic)",
            required=False,
            enum=TextSnippet.get_vector_field_names(),
        ),
        OpenApiParameter(
            name="jad-id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="JAD occurrence ID (must contain 'jad_occurrence__', default: jad_occurrence__1)",
            required=False,
        ),
        OpenApiParameter(
            name="amount",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Number of similar items to return (default: 3, max: 10)",
            required=False,
        ),
        OpenApiParameter(
            name="max-distance",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Maximum distance threshold for similarity (default: 0.02, max: 0.5)",
            required=False,
        ),
        OpenApiParameter(
            name="collection",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Collection to compare with (default: 'JAD sentences')",
            required=False,
            enum=list(Collection.objects.values_list("title", flat=True)),
        ),
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "jad-id": {"type": "string", "example": "jad_occurrence__1"},
                "sents-in-passage": {"type": "integer", "example": 9},
                "max-distance": {"type": "number", "format": "float", "example": 0.02},
                "requested-amount": {"type": "integer", "example": 3},
                "similar_passages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["jad_occurrence__45"],
                },
                "similar": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "text": {"type": "string"},
                            "similar": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "distance": {
                                            "type": "number",
                                            "format": "float",
                                        },
                                        "text": {"type": "string"},
                                        "passage_id": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
                "error": {"type": "string"},
            },
        }
    },
)
@api_view(["get"])
def find_similar_passages(request):
    """Find similar passages based on vector similarity for a given JAD occurrence ID"""
    vector_field = request.GET.get("vector-field", "embedding_nomic")
    if vector_field not in TextSnippet.get_vector_field_names():
        raise Http404(f"Invalid vector field: {vector_field}")
    jad_id = request.GET.get("jad-id", "jad_occurrence__1")
    amount = request.GET.get("amount", 3)
    max_distance = request.GET.get("max-distance", 0.02)
    collection_title = request.GET.get("collection", "JAD sentences")
    print(collection_title)
    if collection_title not in list(Collection.objects.values_list("title", flat=True)):
        raise Http404(f"Collection with title {collection_title} does not exist")
    try:
        max_distance = float(max_distance)
    except ValueError:
        print("foo")
        max_distance = 0.2
    if max_distance > 0.5:
        max_distance = 0.2
    try:
        amount = int(amount)
    except ValueError:
        amount = 3
    if amount > 10:
        amount = 10
    payload = {}
    if jad_id:
        if "jad_occurrence__" in jad_id:
            items = TextSnippet.objects.filter(
                text_id__startswith=f"{jad_id}-"
            ).order_by("text_id")
            payload["jad-id"] = jad_id
            payload["sents-in-passage"] = items.count()
            payload["max-distance"] = max_distance
            payload["requested-amount"] = amount
            sents = []
            similar_passages = set()
            for x in items:
                item = {"id": x.text_id, "text": x.content, "similar": []}
                for y in x.find_similar(
                    vector_field=vector_field,
                    collection_title=collection_title,
                    amount=amount,
                ):
                    if y.distance < max_distance and y.text_id != x.text_id:
                        item["similar"].append(
                            {
                                "id": y.text_id,
                                "distance": y.distance,
                                "text": y.content,
                                "passage_id": y.text_id.split("-")[0],
                            }
                        )
                        similar_passages.add(y.text_id.split("-")[0])
                sents.append(item)
            payload["similar_passages"] = list(similar_passages)
            payload["similar"] = sents
        else:
            payload["error"] = (
                f"{jad_id} does not match expacted pattern 'jad_occurrence__'"
            )
    else:
        payload["error"] = "please provide a query param '?jad-id=jad_occurrence__"
    return JsonResponse(payload)
