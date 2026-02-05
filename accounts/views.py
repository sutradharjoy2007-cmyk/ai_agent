from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, AIAgentConfigForm
from .models import UserProfile, AIAgentConfig


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated profile and AI config
            UserProfile.objects.create(user=user)
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
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def ai_agent_view(request):
    """Display and update AI agent configuration"""
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
