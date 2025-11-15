from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from .swagger_documentation import schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('articles.urls')),
    
    # Swagger Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
]