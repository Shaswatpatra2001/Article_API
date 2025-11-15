from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Article
from .serializers import *

class ArticleCreateView(APIView):
    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            # In real implementation, check user role from request
            is_staff = request.data.get('is_staff', False)
            
            article_data = serializer.validated_data.copy()
            
            # Auto-set status for students
            if not is_staff and 'status' not in article_data:
                article_data['status'] = 'pending_review'
                article_data['submitted_at'] = timezone.now()
            
            # Validate staff can set published status
            if is_staff and article_data.get('status') == 'published':
                article_data['published_at'] = timezone.now()
            
            article = Article.objects.create(**article_data)
            
            response_serializer = ArticleDetailSerializer(article)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleUpdateView(APIView):
    def put(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        
        serializer = ArticleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # In real implementation, check user role from request
            is_staff = request.data.get('is_staff', False)
            
            data = serializer.validated_data.copy()
            
            # Handle status transitions
            if 'status' in data:
                new_status = data['status']
                if new_status == 'pending_review' and article.status != 'pending_review':
                    data['submitted_at'] = timezone.now()
                
                if new_status == 'published' and is_staff:
                    data['published_at'] = timezone.now()
            
            # Update article fields
            for field, value in data.items():
                setattr(article, field, value)
            
            article.save()
            response_serializer = ArticleDetailSerializer(article)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetailView(APIView):
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleDetailSerializer(article)
        return Response(serializer.data)

class ArticleListView(APIView):
    def get(self, request):
        # Get query parameters
        status_filter = request.GET.get('status')
        author_id = request.GET.get('author_id')
        category = request.GET.get('category')
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        business_id = request.GET.get('business_id', 'default_business')
        
        # Filter articles
        articles = Article.objects.filter(business_id=business_id)
        
        if status_filter:
            articles = articles.filter(status=status_filter)
        if author_id:
            articles = articles.filter(author_id=author_id)
        if category:
            articles = articles.filter(category=category)
        
        # Pagination
        paginator = Paginator(articles, limit)
        page_number = (offset // limit) + 1
        page_obj = paginator.get_page(page_number)
        
        serializer = ArticleListSerializer(page_obj, many=True)
        
        return Response({
            'data': serializer.data,
            'total': paginator.count,
            'page': page_number,
            'limit': limit
        })

class ArticleApproveView(APIView):
    def patch(self, request, article_id):
        serializer = ArticleApproveSerializer(data=request.data)
        if serializer.is_valid():
            article = get_object_or_404(Article, id=article_id)
            
            article.status = 'published'
            article.approved_by = serializer.validated_data['approved_by']
            article.approved_by_name = serializer.validated_data['approved_by_name']
            article.published_at = timezone.now()
            article.save()
            
            response_serializer = ArticleDetailSerializer(article)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleRejectView(APIView):
    def patch(self, request, article_id):
        serializer = ArticleRejectSerializer(data=request.data)
        if serializer.is_valid():
            article = get_object_or_404(Article, id=article_id)
            
            article.status = 'rejected'
            article.rejected_by = serializer.validated_data['rejected_by']
            article.rejected_by_name = serializer.validated_data['rejected_by_name']
            article.rejection_reason = serializer.validated_data['rejection_reason']
            article.rejected_at = timezone.now()
            article.save()
            
            response_serializer = ArticleDetailSerializer(article)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardStatsView(APIView):
    def get(self, request):
        business_id = request.GET.get('business_id', 'default_business')
        today = timezone.now().date()
        
        # Basic counts
        total_articles = Article.objects.filter(business_id=business_id).count()
        pending_review = Article.objects.filter(
            business_id=business_id, 
            status='pending_review'
        ).count()
        published = Article.objects.filter(
            business_id=business_id, 
            status='published'
        ).count()
        rejected = Article.objects.filter(
            business_id=business_id, 
            status='rejected'
        ).count()
        
        # Today's submissions
        today_submissions = Article.objects.filter(
            business_id=business_id,
            submitted_at__date=today
        ).count()
        
        # Recent articles for review
        recent_articles = Article.objects.filter(
            business_id=business_id,
            status='pending_review'
        ).order_by('-submitted_at')[:5]
        
        recent_articles_serializer = ArticleListSerializer(recent_articles, many=True)
        
        return Response({
            'total_articles': total_articles,
            'pending_review': pending_review,
            'published': published,
            'rejected': rejected,
            'today_submissions': today_submissions,
            'recent_articles': recent_articles_serializer.data
        })