from django.shortcuts import redirect
from datetime import date

from userauths.models import User


class PaymentTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get('payment_in_progress'):
            if not request.session.get_expiry_age() > 0:
                # Payment timed out, redirect to search-account
                del request.session['payment_in_progress']
                return redirect('core:search-account')

        response = self.get_response(request)
        return response


class UserVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current session visit date
        session_visit_date = request.session.get('visit_date')
        current_date = date.today().isoformat()

        if session_visit_date != current_date:
            # This is a new day or a new visitor
            request.session['visit_date'] = current_date
            request.session['visits_count'] = 1
        else:
            # Increment the visit count
            request.session['visits_count'] += 1

        request.session.set_expiry(900)

        response = self.get_response(request)

        # Set a cookie with user-unique identifier if it doesn't exist
        # if not request.COOKIES.get('user_id'):
        response.set_cookie('user_id', request.session.session_key, max_age=3)

        return response
