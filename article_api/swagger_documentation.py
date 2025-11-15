from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Article API",
        default_version="v1",
        description="API documentation for Article Management System",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

# Common Swagger parameters
business_id_param = openapi.Parameter(
    'business_id',
    openapi.IN_QUERY,
    description="Business ID for scoping data",
    type=openapi.TYPE_STRING,
    default="default_business"
)

authorization_header = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="Bearer token for authentication",
    type=openapi.TYPE_STRING,
    required=True,
    default="Bearer "
)

# Request body schemas for Swagger
article_create_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['title', 'content', 'author_name', 'author_id'],
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING),
        'subtitle': openapi.Schema(type=openapi.TYPE_STRING),
        'content': openapi.Schema(type=openapi.TYPE_STRING),
        'cover_image_url': openapi.Schema(type=openapi.TYPE_STRING),
        'category': openapi.Schema(type=openapi.TYPE_STRING, enum=['Technology', 'Science', 'Business', 'Health', 'Education', 'Other']),
        'author_name': openapi.Schema(type=openapi.TYPE_STRING),
        'author_id': openapi.Schema(type=openapi.TYPE_STRING),
        'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['draft', 'pending_review', 'published']),
    }
)

article_update_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING),
        'subtitle': openapi.Schema(type=openapi.TYPE_STRING),
        'content': openapi.Schema(type=openapi.TYPE_STRING),
        'cover_image_url': openapi.Schema(type=openapi.TYPE_STRING),
        'category': openapi.Schema(type=openapi.TYPE_STRING),
        'author_name': openapi.Schema(type=openapi.TYPE_STRING),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

approve_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['approved_by', 'approved_by_name'],
    properties={
        'approved_by': openapi.Schema(type=openapi.TYPE_STRING),
        'approved_by_name': openapi.Schema(type=openapi.TYPE_STRING),
        'notes': openapi.Schema(type=openapi.TYPE_STRING),
    }
)

reject_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['rejected_by', 'rejected_by_name', 'rejection_reason'],
    properties={
        'rejected_by': openapi.Schema(type=openapi.TYPE_STRING),
        'rejected_by_name': openapi.Schema(type=openapi.TYPE_STRING),
        'rejection_reason': openapi.Schema(type=openapi.TYPE_STRING),
    }
)