from django.http import HttpResponse


def dashboard(request):
    return HttpResponse('<h1>Service CRM Django Running</h1>')
