from rest_framework.response import Response


def api_response(success, msg, data=None, code=200, status_code=200, pagination=None):
    body = {
        'msg': msg,
        'success': success,
        'data': data,
        'code': code,
    }
    if pagination is not None:
        body['pagination'] = pagination
    return Response(body, status=status_code)