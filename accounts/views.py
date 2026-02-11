from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, AIAgentConfigForm, KYCUploadForm

from .models import UserProfile, AIAgentConfig
import pandas as pd
import io
import requests


@login_required
def report_view(request):
    """Fetch and display report from Google Sheet"""
    # Ensure AI config exists
    ai_config, created = AIAgentConfig.objects.get_or_create(user=request.user)
    
    # Handle Sheet ID update
    if request.method == 'POST' and 'google_sheet_id' in request.POST:
        new_id = request.POST.get('google_sheet_id', '').strip()
        if new_id:
            ai_config.google_sheet_id = new_id
            ai_config.save()
            messages.success(request, 'Google Sheet ID updated successfully!')
            return redirect('report')
            
    sheet_id = ai_config.google_sheet_id
    
    data = []
    columns = []
    error = None
    
    if sheet_id:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Read into pandas DataFrame with UTF-8 encoding
            # Use content (bytes) and BytesIO for better encoding handling
            df = pd.read_csv(io.BytesIO(response.content), encoding='utf-8')
            
            # Filter logic if requested
            query = request.GET.get('q', '').strip()
            if query:
                # Simple case-insensitive search across all columns
                mask = df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)
                df = df[mask]
                
            columns = df.columns.tolist()
            df = df.iloc[::-1] # Reverse payload to show most recent at top
            df = df.fillna('') # Replace NaN with empty string
            data = df.values.tolist()
            
        except Exception as e:
            error = f"Failed to load report data: {str(e)}"
    
    return render(request, 'accounts/report.html', {
        'data': data,
        'columns': columns,
        'error': error,
        'query': request.GET.get('q', ''),
        'google_sheet_id': sheet_id
    })



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
            
            # Handle AJAX request for auto-save
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Variable saved'})
                
            messages.success(request, 'AI Agent configuration saved successfully!')
            return redirect('ai_agent')
        
        # Handle AJAX errors
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
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

