
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the CINTRACON Backend!. This backend is Supplying data to the CINTRACON Frontend through REST API.")