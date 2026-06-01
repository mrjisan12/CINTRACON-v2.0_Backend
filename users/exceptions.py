from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import Throttled


def custom_exception_handler(exc, context):
    if isinstance(exc, Throttled):
        wait = exc.wait
        msg = f'Too many requests. Please wait {int(wait)} seconds.' if wait else 'Too many requests. Please wait.'
        return Response(
            {'success': False, 'msg': msg, 'data': None, 'code': 429},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    return exception_handler(exc, context)
