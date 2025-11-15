from rest_framework import serializers
from .models import Article

class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title', 'subtitle', 'content', 'cover_image_url', 
            'category', 'author_name', 'author_id', 'status'
        ]

class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'title', 'subtitle', 'content', 'cover_image_url', 
            'category', 'author_name', 'status'
        ]

class ArticleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'subtitle', 'cover_image_url', 'category',
            'author_name', 'author_id', 'status', 'submitted_at', 'created_at'
        ]

class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'subtitle', 'content', 'cover_image_url', 'category',
            'author_name', 'author_id', 'status', 'submitted_at', 'approved_by',
            'approved_by_name', 'rejection_reason', 'created_at', 'updated_at'
        ]

class ArticleApproveSerializer(serializers.Serializer):
    approved_by = serializers.CharField(max_length=100)
    approved_by_name = serializers.CharField(max_length=200)
    notes = serializers.CharField(required=False, allow_blank=True)

class ArticleRejectSerializer(serializers.Serializer):
    rejected_by = serializers.CharField(max_length=100)
    rejected_by_name = serializers.CharField(max_length=200)
    rejection_reason = serializers.CharField()

class DashboardStatsSerializer(serializers.Serializer):
    total_articles = serializers.IntegerField()
    pending_review = serializers.IntegerField()
    published = serializers.IntegerField()
    rejected = serializers.IntegerField()
    today_submissions = serializers.IntegerField()
    recent_articles = ArticleListSerializer(many=True)