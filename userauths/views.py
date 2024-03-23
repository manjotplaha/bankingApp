from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from userauths.models import User
from userauths.forms import UserRegisterForm


def RegisterView(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("account:account")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account was created successfully.")
            new_user = authenticate(username=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, new_user)
            return redirect("account:account")
        else:
            messages.warning(request, 'Passwords do not match.')
            return render(request, "userauths/sign-up.html", {"form": form})
    else:
        form = UserRegisterForm()
    context = {
        "form": form
    }
    return render(request, "userauths/sign-up.html", context)


def LoginView(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, email=email, password=password)

            if user is not None:  # if there is a user
                login(request, user)
                messages.success(request, "You are logged.")
                return redirect("account:account")
            else:
                messages.warning(request, "Username or password does not exist")
                return redirect("userauths:sign-in")
        except:
            messages.warning(request, "User does not exist")

    if request.user.is_authenticated:
        messages.warning(request, "You are already logged In")
        return redirect("account:account")

    return render(request, "userauths/sign-in.html")


def logoutView(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("userauths:sign-in")



def password_reset_confirm(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.warning(request, 'User with this email does not exist.')
            return render(request, 'userauths/password_reset_confirm.html')

        if new_password == confirm_password:
            # Validate the new password
            try:
                validate_password(new_password, user=user)
            except ValidationError as e:
                messages.warning(request, e.messages[0])  # Display the first error message
                return render(request, 'userauths/password_reset_confirm.html')

            # If password is valid, set and save it
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password reset successfully.')
            return redirect('userauths:sign-in')
        else:
            messages.warning(request, 'New password and confirm password do not match.')
            return render(request, 'userauths/password_reset_confirm.html')

    return render(request, 'userauths/password_reset_confirm.html')