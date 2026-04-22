from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Material
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import StudentProfile
from django.utils.dateparse import parse_date
from datetime import datetime
import re

# 1. LANDING PAGE
def index(request):
    return render(request, 'index.html')

# 2. SIGNUP VIEW
def signup_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        e = request.POST.get('email')
        p = request.POST.get('password')
        cp = request.POST.get('confirm_password')


        # 1. Username: Must be alphabets ONLY (no numbers, no spaces)
        if not u.isalpha():
            messages.error(request, "Username must contain only alphabets (A-Z). No numbers or symbols allowed.")
        
        # 2. Strict Email Check: Must end with a valid domain (e.g., .com, .in, .edu)
        # This regex ensures there is an @ and a dot followed by at least 2 characters at the end
        elif not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", e):
            messages.error(request, "Please enter a valid email address (e.g., name@gmail.com).")

        # 3. Password Match Check
        elif p != cp:
            messages.error(request, "Passwords do not match!")
        
        # 4. Existing User Check
        elif User.objects.filter(username=u).exists():
            messages.error(request, "Username already taken.")
            
        else:
            # All checks passed
            user = User.objects.create_user(username=u, email=e, password=p)
            StudentProfile.objects.create(user=user)
            login(request, user)
            return redirect('browse')
            
    return render(request, 'signup.html')

# 3. LOGIN VIEW
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            # If a superuser logs in, you could optionally redirect them straight to the portal
            if user.is_superuser:
                return redirect('admin-dashboard')
            return redirect('browse')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'login.html')

# 4. LOGOUT VIEW
def logout_view(request):
    logout(request)
    return redirect('index')

# 5. BROWSE / SEARCH VIEW
@login_required(login_url='login')
def browse_materials(request):
    query = request.GET.get('search')
    category = request.GET.get('category')
    materials = Material.objects.all().order_by('-uploaded_at')

    if query:
        materials = materials.filter(
            Q(title__icontains=query) | Q(subject__icontains=query)
        )
    if category and category != 'All':
        materials = materials.filter(category=category)

    return render(request, 'browse.html', {'materials': materials})

# 6. UPLOAD VIEW
@login_required(login_url='login')
def upload_material(request):
    if request.method == 'POST':
        Material.objects.create(
            title=request.POST.get('title'),
            subject=request.POST.get('subject'),
            semester=request.POST.get('semester'),
            category=request.POST.get('category'),
            description=request.POST.get('description'),
            file=request.FILES.get('file'),
            uploaded_by=request.user
        )
        return redirect('browse')
    return render(request, 'upload.html')

# 7. INDIVIDUAL VIEW
@login_required(login_url='login')
def view_material(request, pk):
    material = get_object_or_404(Material, pk=pk)
    return render(request, 'view.html', {'material': material})

# ==========================================================
# ADMIN SEPARATE ENVIRONMENT (Custom Webpages)
# ==========================================================

# 8. ADMIN MAIN DASHBOARD
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_main_dashboard(request):
    """ The main summary page (dashboard/admin_dashboard.html) """
    customer_count = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_files = Material.objects.count()
    
    context = {
        'total_users': customer_count,
        'total_files': total_files,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

# 9. ADMIN WORK PAGE
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_work_page(request):
    """ The task/pending items overview (dashboard/admin_work_page.html) """
    return render(request, 'dashboard/admin_work_page.html')

# 10. MANAGE USERS TABLE
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_manage_users(request):
    customers = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    return render(request, 'dashboard/tables.html', {'users': customers})

# 11. CHANGE ADMIN PASSWORD
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_change_password(request):
    """ Custom change password page (dashboard/change_password.html) """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('admin-dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'dashboard/change_password.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_report_generation(request):
    """
    View to generate reports based on the actual USER JOIN DATE.
    """
    # 1. Start with profiles, excluding admins
    profiles = StudentProfile.objects.filter(
        user__is_staff=False, 
        user__is_superuser=False
    ).order_by('-user__date_joined') # Order by signup date
    
    # 2. Get the dates from the search form
    from_date_str = request.GET.get('from')
    to_date_str = request.GET.get('to')
    
    # 3. Apply filters to user__date_joined instead of enquiry_date
    if from_date_str:
        from_date = parse_date(from_date_str)
        if from_date:
            # Filter by the date the USER joined
            profiles = profiles.filter(user__date_joined__date__gte=from_date)
            
    if to_date_str:
        to_date = parse_date(to_date_str)
        if to_date:
            # Filter by the date the USER joined
            profiles = profiles.filter(user__date_joined__date__lte=to_date)
    
    context = {
        'profiles': profiles,
        'from_date_val': from_date_str,
        'to_date_val': to_date_str,
    }
    
    return render(request, 'dashboard/reports.html', context)