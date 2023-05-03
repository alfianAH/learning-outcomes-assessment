from django.shortcuts import render
from learning_outcomes_assessment.exceptions import(
    ConditionTimeoutException,
    DeleteLockedObjectException,
    SaveLockedObjectException,
)
import requests

class TimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(
            exception,
            (requests.exceptions.Timeout, ConditionTimeoutException) 
        ):
            return render(request, 'errors/timeout.html')

        # If the exception is not handled, return None
        return None


class LockedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, DeleteLockedObjectException):
            return render(request, 'errors/locked.html', context={
                'exception': exception,
                'message': 'Obyek yang sudah dikunci tidak bisa dihapus.',
            })
        elif isinstance(exception, SaveLockedObjectException):
            return render(request, 'errors/locked.html', context={
                'exception': exception,
                'message': 'Obyek yang sudah dikunci tidak bisa diubah.',
            })

        # If the exception is not handled, return None
        return None
