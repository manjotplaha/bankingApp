from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from userauths.models import User
from account.models import Account
from core.forms import SupportCaseForm


# Create your views here.

def index(request):
    return render(request, "core/index.html")


def contact(request):
    return render(request, "core/contact.html")


def about(request):
    return render(request, "core/about.html")


def support_page(request):
    if request.method == 'POST':
        form = SupportCaseForm(request.POST)
        if form.is_valid():
            account_number = request.POST.get('account')
            account_id = request.POST.get('account_id')

            try:
                account = Account.objects.get(account_number=account_number, account_id=account_id)
            except Account.DoesNotExist:
                messages.warning(request, "Invalid Account Number or Account ID.")
                return redirect('account:account')

            support_case = form.save(commit=False)
            support_case.account = account
            support_case.save()
            messages.success(request,
                             "Support case submitted successfully. Your Case ID is: {}".format(support_case.id))
            return redirect('account:account')

    else:
        # Fetching account details from the logged-in user or session
        if request.user.is_authenticated:
            account = Account.objects.get(user=request.user)
        else:
            account = None

        form = SupportCaseForm(account=account)

    return render(request, 'core/support_page.html', {'form': form})
