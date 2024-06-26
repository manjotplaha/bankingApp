from django.db import transaction
from django.shortcuts import render, redirect
from account.models import  Account
from django.contrib.auth.decorators import  login_required
from django.db.models import Q
from django.contrib import messages
from core.models import Transaction,Contact
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# @login_required
# @login_required
def search_users_by_account_number(request):
    # account=Account.objects.filter(account_status="active")
    contacts = Contact.objects.filter(user=request.user)
    print(request.user)
    for i in contacts:
        print(i.contact_name)
        print(i.account_number)

    account=Account.objects.all()
    query=request.POST.get("account_number")
    if query:
        account=account.filter(
            Q(account_number=query)|
            Q(account_id=query)
        ).distinct()
    context={
        "account":account,
        "query":query,
        "contacts":contacts
    }
    print('debug1')
    return render(request,"transfer/search-user-by-account-number.html", context)


def AmountTransfer(request, account_number):
    try:
        account = Account.objects.get(account_number=account_number)
    except:
        messages.warning(request, "Account does not exist.")
        return redirect("core:search-account")
    context = {
        "account": account,
    }
    print('debug2')
    if request.session.get('payment_in_progress') is None:
        print(request.session, 'payment_in_progress')
        # session expiration to 20 seconds from now, user will logout automatically
        # request.session.set_expiry(20)
        # Set session variable to indicate payment in progress
        request.session['payment_in_progress'] = True
        # Set session variable to store the timestamp when the session expires
        request.session['_session_expiry_timestamp'] = int((timezone.now() + timedelta(seconds=70)).timestamp())
        print('Session expiry set:', request.session['_session_expiry_timestamp'])
    session_expiry_timestamp = request.session.get('_session_expiry_timestamp')
    print("expiry time----", session_expiry_timestamp);

    return render(request, "transfer/amount-transfer.html", context)


def AmountTransferProcess(request, account_number):
    session_expiry_timestamp = request.session.get('_session_expiry_timestamp')

    t = timezone.now().timestamp();

    if request.method == "POST" and session_expiry_timestamp and session_expiry_timestamp < t:
        # Session has expired
        messages.warning(request, "Session has expired. Please try again.")
        request.session['payment_in_progress'] = None  # Reset session
        request.session['_session_expiry_timestamp'] = 0  # Reset session expiry
        print('Session expired, resetting session.')

        return redirect("core:search-account")


    account = Account.objects.get(account_number=account_number)  ## Get the account that the money would be sent to
    sender = request.user
    reciever = account.user

    sender_account = request.user.account
    reciever_account = account

    if sender_account.account_status == 'active' and reciever_account.account_status == 'active':
        if request.method == "POST":
            amount = request.POST.get("amount-send")
            description = request.POST.get("description")

            print(amount)
            print(description)

            if sender_account.account_balance :
                new_transaction = Transaction.objects.create(
                    user=request.user,
                    amount=amount,
                    description=description,
                    reciever=reciever,
                    sender=sender,
                    sender_account=sender_account,
                    reciever_account=reciever_account,
                    status="failed",
                    transaction_type="transfer"
                )
                new_transaction.save()

                # Get the id of the transaction that vas created nov
                transaction_id = new_transaction.transaction_id
                print('debug3')

                return redirect("core:transfer-confirmation", account.account_number, transaction_id)
            else:
                messages.warning(request, "Insufficient Fund.")
                print('debug4')

            return redirect("core:amount-transfer", account.account_number)
        else:
            messages.warning(request, "Error Occured, Try again later.")
            print('debug5')

            return redirect("account:account")
    else:
        messages.warning(request, "Not an Active User")
        return redirect("account:account")


def TransferConfirmation(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transaction does not exist.")
        print('debug6')

        return redirect("account:account")
    context = {
        "account": account,
        "transaction": transaction
    }
    print('debug7')

    return render(request, "transfer/transfer-confirmation.html", context)


def TransferProcess(request, account_number, transaction_id):
    account = Account.objects.get(account_number=account_number)
    transaction = Transaction.objects.get(transaction_id=transaction_id)

    sender = request.user
    reciever = account.user

    sender_account = request.user.account
    reciever_account = account

    completed = False

    if request.method == "POST":
        pin_number = request.POST.get("pin-number")
        print(pin_number)

        if pin_number == sender_account.pin_number:
            transaction.status = "completed"
            transaction.save()

            # Remove the amount that i am sending from my account balance and update my account
            sender_account.account_balance -= transaction.amount
            sender_account.save()

            # Add the amount that vas removed from my account to the person that i am sending the money too
            account.account_balance += transaction.amount
            account.save()

            messages.success(request, "Transfer Successfull.")
            print('1')
            return redirect("core:transfer-completed", account.account_number, transaction.transaction_id)
        else:
            messages.warning(request, "Incorrect Pin.")
            print('2')
            return redirect('core:transfer-confirmation', account.account_number, transaction.transaction_id)
    else:
        messages.warning(request, "An error occured, Try again later.")
        print('3')
        return redirect('account:account')


def TransferCompleted(request, account_number, transaction_id):
    try:
        account = Account.objects.get(account_number=account_number)
        transaction = Transaction.objects.get(transaction_id=transaction_id)
    except:
        messages.warning(request, "Transfer does not exist.")
        return redirect("account:account")
    context = {
        "account": account,
        "transaction": transaction
    }
    return render(request, "transfer/transfer-completed.html", context)


#     if sender_account.user.account.kyc_confirmed: