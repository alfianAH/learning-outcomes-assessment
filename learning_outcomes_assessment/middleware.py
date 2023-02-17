from django.shortcuts import render
import requests

class TimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, requests.exceptions.Timeout):
            return render(request, 'errors/timeout.html')

        # If the exception is not handled, return None
        return None
