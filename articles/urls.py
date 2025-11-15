from django.urls import path
from . import views

urlpatterns = [
    path('articles', views.ArticleCreateView.as_view(), name='article-create'),
    path('articles/<uuid:article_id>', views.ArticleDetailView.as_view(), name='article-detail'),
    path('articles/<uuid:article_id>/update', views.ArticleUpdateView.as_view(), name='article-update'),
    path('articles/list', views.ArticleListView.as_view(), name='article-list'),
    path('articles/<uuid:article_id>/approve', views.ArticleApproveView.as_view(), name='article-approve'),
    path('articles/<uuid:article_id>/reject', views.ArticleRejectView.as_view(), name='article-reject'),
    path('dashboard/stats', views.DashboardStatsView.as_view(), name='dashboard-stats'),
]