from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from .models import Article
from .serializers import *
from .services import ArticleService
from article_api.swagger_documentation import *

class ArticleCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Create a new article",
        request_body=article_create_schema,
        responses={201: ArticleDetailSerializer, 400: 'Bad Request'},
        manual_parameters=[authorization_header, business_id_param]
    )
    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Get business_id from authenticated user or request
            business_id = getattr(request.user, 'business_id', request.GET.get('business_id', 'default_business'))
            
            # Check if user is staff (from token claims)
            is_staff = getattr(request.user, 'usertype', None) == 'business'
            
            article_data = serializer.validated_data.copy()
            article_data['business_id'] = business_id
            
            article = ArticleService.create_article(
                article_data, 
                is_staff=is_staff
            )
            
            response_serializer = ArticleDetailSerializer(article)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleUpdateView(APIView):
    @swagger_auto_schema(
        operation_description="Update an existing article",
        request_body=article_update_schema,
        responses={200: ArticleDetailSerializer, 400: 'Bad Request', 404: 'Not Found'},
        manual_parameters=[authorization_header, business_id_param]
    )
    def put(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        
        serializer = ArticleUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # Check if user is staff
            is_staff = getattr(request.user, 'usertype', None) == 'business'
            
            updated_article = ArticleService.update_article(
                article_id, 
                serializer.validated_data, 
                is_staff=is_staff
            )
            
            if updated_article:
                response_serializer = ArticleDetailSerializer(updated_article)
                return Response(response_serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Get a single article by ID",
        responses={200: ArticleDetailSerializer, 404: 'Not Found'},
        manual_parameters=[authorization_header, business_id_param]
    )
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        serializer = ArticleDetailSerializer(article)
        return Response(serializer.data)

class ArticleListView(APIView):
    @swagger_auto_schema(
        operation_description="Get paginated list of articles with filtering",
        responses={200: ArticleListSerializer(many=True)},
        manual_parameters=[
            authorization_header,
            business_id_param,
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('author_id', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('offset', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        # Get query parameters
        status_filter = request.GET.get('status')
        author_id = request.GET.get('author_id')
        category = request.GET.get('category')
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        business_id = getattr(request.user, 'business_id', request.GET.get('business_id', 'default_business'))
        
        filters = {
            'status': status_filter,
            'author_id': author_id,
            'category': category,
            'business_id': business_id
        }
        
        articles = ArticleService.get_articles(filters)
        
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
    @swagger_auto_schema(
        operation_description="Approve a student article (Staff only)",
        request_body=approve_schema,
        responses={200: ArticleDetailSerializer, 400: 'Bad Request', 404: 'Not Found'},
        manual_parameters=[authorization_header, business_id_param]
    )
    def patch(self, request, article_id):
        serializer = ArticleApproveSerializer(data=request.data)
        if serializer.is_valid():
            approved_article = ArticleService.approve_article(
                article_id,
                serializer.validated_data['approved_by'],
                serializer.validated_data['approved_by_name'],
                serializer.validated_data.get('notes')
            )
            
            if approved_article:
                response_serializer = ArticleDetailSerializer(approved_article)
                return Response(response_serializer.data)
            
            return Response(
                {'error': 'Article not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleRejectView(APIView):
    @swagger_auto_schema(
        operation_description="Reject a student article (Staff only)",
        request_body=reject_schema,
        responses={200: ArticleDetailSerializer, 400: 'Bad Request', 404: 'Not Found'},
        manual_parameters=[authorization_header, business_id_param]
    )
    def patch(self, request, article_id):
        serializer = ArticleRejectSerializer(data=request.data)
        if serializer.is_valid():
            rejected_article = ArticleService.reject_article(
                article_id,
                serializer.validated_data['rejected_by'],
                serializer.validated_data['rejected_by_name'],
                serializer.validated_data['rejection_reason']
            )
            
            if rejected_article:
                response_serializer = ArticleDetailSerializer(rejected_article)
                return Response(response_serializer.data)
            
            return Response(
                {'error': 'Article not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardStatsView(APIView):
    @swagger_auto_schema(
        operation_description="Get dashboard statistics (Staff only)",
        responses={200: DashboardStatsSerializer},
        manual_parameters=[authorization_header, business_id_param]
    )
    def get(self, request):
        business_id = getattr(request.user, 'business_id', request.GET.get('business_id', 'default_business'))
        stats = ArticleService.get_dashboard_stats(business_id)
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)