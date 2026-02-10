from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, AIAgentConfigForm, KYCUploadForm
from .models import UserProfile, AIAgentConfig


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            full_name = form.cleaned_data.get('full_name', '')
            user.first_name = full_name
            user.save()
            # Create associated profile and AI config
            UserProfile.objects.create(user=user, name=full_name)
            AIAgentConfig.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {email}!')
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Display user dashboard"""
    profile = request.user.profile
    ai_config = request.user.ai_config
    
    context = {
        'user': request.user,
        'profile': profile,
        'ai_config': ai_config,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    """Display and update user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'kyc_submit' in request.POST:
            # Handle KYC document upload
            kyc_form = KYCUploadForm(request.POST, request.FILES, instance=profile)
            if kyc_form.is_valid():
                kyc_profile = kyc_form.save(commit=False)
                kyc_profile.kyc_status = 'PENDING'
                kyc_profile.save()
                messages.success(request, 'KYC document submitted successfully! Your verification is under review.')
                return redirect('profile')
            form = UserProfileForm(instance=profile)
        else:
            # Handle profile update
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('profile')
            kyc_form = KYCUploadForm(instance=profile)
    else:
        form = UserProfileForm(instance=profile)
    
    kyc_form = KYCUploadForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'kyc_form': kyc_form,
        'profile': profile
    })


@login_required
def ai_agent_view(request):
    """Display and update AI agent configuration"""
    # KYC verification check
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.kyc_status != 'VERIFIED':
        return redirect('kyc_required')
    
    ai_config, created = AIAgentConfig.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = AIAgentConfigForm(request.POST, instance=ai_config)
        if form.is_valid():
            form.save()
            messages.success(request, 'AI Agent configuration saved successfully!')
            return redirect('ai_agent')
    else:
        form = AIAgentConfigForm(instance=ai_config)
    
    webhook_url = ai_config.get_webhook_url()
    
    return render(request, 'accounts/ai_agent.html', {
        'form': form,
        'webhook_url': webhook_url,
        'ai_config': ai_config
    })


@login_required
def kyc_required_view(request):
    """Display KYC required page when user hasn't completed verification"""
    profile = getattr(request.user, 'profile', None)
    return render(request, 'accounts/kyc_required.html', {'profile': profile})


@login_required
def subscription_expired(request):
    """Display subscription expired page"""
    return render(request, 'accounts/subscription_expired.html')

