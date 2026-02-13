from django.urls import path
from . import views
from .api_views import api_get_user_config

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    path('ai-agent/', views.ai_agent_view, name='ai_agent'),

    path('feed/', views.feed_view, name='feed'),
    path('report/', views.report_view, name='report'),
    path('delete-comment/', views.delete_comment_view, name='delete_comment'),
    path('kyc-required/', views.kyc_required_view, name='kyc_required'),

    
    # API endpoints
    path('api/user/<str:admin_password>/<str:email_prefix>/<str:field>/', api_get_user_config, name='api_user_config'),
    
    # Subscription
    path('subscription-expired/', views.subscription_expired, name='subscription_expired'),
]

