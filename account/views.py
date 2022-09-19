from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .forms import RegistrationForm, LoginForm
from .tokens import account_activation_token
from .models import *
from django.contrib.auth.decorators import login_required

# Create your views here.
User = get_user_model()


def account_registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user_password = form.cleaned_data['password2']
            user.set_password(form.cleaned_data['password2'])
            user.is_active = False
            user.save()
            account = Account.objects.create(
                user=user,
                country=form.cleaned_data['country']
            )
            account.save()
            author = Author.objects.create(
                user=account,
            )
            author.save()

            # Activation Email
            # current_site = get_current_site(request)  # this get the domain name of the site.
            # subject = 'Activate your Account'
            # message = render_to_string('account/activate.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': account_activation_token.make_token(user)
            # })
            # user.email_user(subject=subject, message=message)
            # messages.success(request,
            #                  'Account was created for ' + str(request.POST.get('username')) + '. A verification email '
            #                                                                                   'has been sent to your '
            #                                                                                   'email address, '
            #                                                                                   'verify your account '
            #                                                                                   'then proceed to login ')
            login_user = authenticate(request, email=user.email, password=user_password)
            if login_user is not None:
                login(request, login_user)
                return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'account/signup.html', {'form': form})


# Email Activation View
def activate_email(request, uid64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uid64))
        user = User.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'account/activate_success.html')
    else:
        return render(request, 'account/activate_error.html')


def Login_View(request):
    form = LoginForm(request.POST)
    if request.method == 'GET':
        return render(request, 'account/login.html', {'form': form})
    value = request.GET.get('value')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if value is not None:
                return redirect(str(value))
            else:
                return redirect('home')

        else:
            messages.warning(request, 'Email or Password is incorrect !')
    return render(request, 'account/login.html', {'form': form})


@login_required()
def logout_view(request):
    logout(request)
    return redirect('login')
