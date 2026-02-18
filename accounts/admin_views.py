from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import CustomUser, UserProfile, AIAgentConfig

# Check if user is superuser
def is_superuser(user):
    return user.is_superuser

@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    """
    Main Admin Dashboard View
    Displays overview statistics and recent activity.
    """
    total_users = CustomUser.objects.count()
    new_users_today = CustomUser.objects.filter(date_joined__date=timezone.now().date()).count()
    pending_kyc = UserProfile.objects.filter(kyc_status='PENDING').count()
    total_ai_agents = AIAgentConfig.objects.count()
    
    # Recent 5 users
    recent_users = CustomUser.objects.select_related('profile').order_by('-date_joined')[:5]

    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'pending_kyc': pending_kyc,
        'total_ai_agents': total_ai_agents,
        'recent_users': recent_users,
        'active_subscriptions': UserProfile.objects.filter(subscription_expiry__gt=timezone.now()).count()
    }
    return render(request, 'custom_admin/dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_user_list(request):
    """
    List all users with search and filtering
    """
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'all')
    
    users = CustomUser.objects.select_related('profile').all().order_by('-date_joined')
    
    if query:
        users = users.filter(
            Q(email__icontains=query) | 
            Q(profile__name__icontains=query) |
            Q(profile__mobile_number__icontains=query)
        )
        
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'verified':
        users = users.filter(profile__kyc_status='VERIFIED')
    elif status_filter == 'pending':
        users = users.filter(profile__kyc_status='PENDING')

    context = {
        'users': users,
        'query': query,
        'status_filter': status_filter
    }
    return render(request, 'custom_admin/user_list.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_user_detail(request, user_id):
    """
    View to manage a specific user
    """
    user = get_object_or_404(CustomUser, id=user_id)
    profile = user.profile
    ai_config = getattr(user, 'ai_config', None)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_status':
            user.is_active = not user.is_active
            user.save()
            messages.success(request, f"User status updated to {'Active' if user.is_active else 'Inactive'}.")
            
        elif action == 'assign_subscription':
            days = int(request.POST.get('days', 0))
            if days > 0:
                profile.subscription_expiry = timezone.now() + timezone.timedelta(days=days)
                profile.package_name = f"{days} Days Package"
                profile.save()
                
                # Log history
                from .models import SubscriptionHistory
                SubscriptionHistory.objects.create(
                    profile=profile,
                    package_name=f"{days} Days Package - Admin Assigned",
                    expiry_date=profile.subscription_expiry
                )
                
                messages.success(request, f"Subscription extended by {days} days.")
        
        elif action == 'update_info':
             profile.name = request.POST.get('name', profile.name)
             profile.mobile_number = request.POST.get('mobile_number', profile.mobile_number)
             user.email = request.POST.get('email', user.email)
             profile.save()
             user.save()
             messages.success(request, "User information updated.")

        return redirect('admin_user_detail', user_id=user_id)
        
    context = {
        'user_obj': user,
        'profile': profile,
        'ai_config': ai_config
    }
    return render(request, 'custom_admin/user_detail.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_kyc_list(request):
    """
    List pending KYC requests
    """
    kyc_requests = UserProfile.objects.filter(
        kyc_status='PENDING'
    ).select_related('user').order_by('-user__date_joined')
    
    context = {
        'kyc_requests': kyc_requests
    }
    return render(request, 'custom_admin/kyc_list.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_kyc_action(request):
    """
    Handle KYC Approval/rejection
    """
    profile = None
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        profile = get_object_or_404(UserProfile, user__id=user_id)
        
        if action == 'approve':
            profile.kyc_status = 'VERIFIED'
            profile.save()
            messages.success(request, f"KYC for {profile.user.email} has been APPROVED.")
            
        elif action == 'reject':
            profile.kyc_status = 'REJECTED'
            profile.save()
            messages.warning(request, f"KYC for {profile.user.email} has been REJECTED.")
            
    return redirect('admin_kyc_list')
