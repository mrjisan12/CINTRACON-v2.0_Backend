from rest_framework.response import Response

def api_response(success, msg, data=None, code=200, status_code=200):
    return Response({
        'msg': msg,
        'success': success,
        'data': data,
        'code': code
    }, status=status_code)