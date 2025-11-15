from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .models import Article

class ArticleService:
    
    @staticmethod
    def create_article(data, is_staff=False):
        """Create a new article with automatic status handling"""
        article_data = data.copy()
        
        # Auto-set status for students
        if not is_staff and 'status' not in article_data:
            article_data['status'] = 'pending_review'
            article_data['submitted_at'] = timezone.now()
        
        # Validate staff can set published status
        if is_staff and article_data.get('status') == 'published':
            article_data['published_at'] = timezone.now()
        
        article = Article.objects.create(**article_data)
        
        # TODO: Trigger email notification for staff when student submits for review
        if article.status == 'pending_review' and not is_staff:
            ArticleService._notify_staff_for_review(article)
            
        return article
    
    @staticmethod
    def update_article(article_id, data, is_staff=False):
        """Update an existing article"""
        try:
            article = Article.objects.get(id=article_id)
            
            # Handle status transitions
            if 'status' in data:
                new_status = data['status']
                if new_status == 'pending_review' and article.status != 'pending_review':
                    data['submitted_at'] = timezone.now()
                    # TODO: Notify staff for review
                
                if new_status == 'published' and is_staff:
                    data['published_at'] = timezone.now()
            
            for field, value in data.items():
                setattr(article, field, value)
            
            article.save()
            return article
            
        except Article.DoesNotExist:
            return None
    
    @staticmethod
    def approve_article(article_id, approved_by, approved_by_name, notes=None):
        """Approve a student article (staff only)"""
        try:
            article = Article.objects.get(id=article_id)
            
            article.status = 'published'
            article.approved_by = approved_by
            article.approved_by_name = approved_by_name
            article.published_at = timezone.now()
            article.save()
            
            # TODO: Send notification to student about approval
            return article
            
        except Article.DoesNotExist:
            return None
    
    @staticmethod
    def reject_article(article_id, rejected_by, rejected_by_name, rejection_reason):
        """Reject a student article (staff only)"""
        try:
            article = Article.objects.get(id=article_id)
            
            article.status = 'rejected'
            article.rejected_by = rejected_by
            article.rejected_by_name = rejected_by_name
            article.rejection_reason = rejection_reason
            article.rejected_at = timezone.now()
            article.save()
            
            # TODO: Send notification to student about rejection
            return article
            
        except Article.DoesNotExist:
            return None
    
    @staticmethod
    def get_articles(filters=None):
        """Get articles with filtering and pagination"""
        queryset = Article.objects.all()
        
        if filters:
            status = filters.get('status')
            author_id = filters.get('author_id')
            category = filters.get('category')
            business_id = filters.get('business_id', 'default_business')
            
            queryset = queryset.filter(business_id=business_id)
            
            if status:
                queryset = queryset.filter(status=status)
            if author_id:
                queryset = queryset.filter(author_id=author_id)
            if category:
                queryset = queryset.filter(category=category)
        
        return queryset
    
    @staticmethod
    def get_dashboard_stats(business_id='default_business'):
        """Get dashboard statistics for staff"""
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
        
        return {
            'total_articles': total_articles,
            'pending_review': pending_review,
            'published': published,
            'rejected': rejected,
            'today_submissions': today_submissions,
            'recent_articles': recent_articles
        }
    
    @staticmethod
    def _notify_staff_for_review(article):
        """Placeholder for staff notification email"""
        # TODO: Implement email notification to staff
        print(f"Notification: Article '{article.title}' submitted for review by {article.author_name}")
        pass