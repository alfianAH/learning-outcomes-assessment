from django.http import HttpRequest


def add_role_to_context(request: HttpRequest):
    """Add user role to context

    Args:
        request (HttpRequest): Request

    Returns:
        dict: User's role
    """

    user_role = None
    if request.user.is_authenticated:
        user_role = request.user.role
    return {'user_role': user_role}
