from django.shortcuts import render

from django.http import HttpResponse


# Create your views here.
def index(request):
    return HttpResponse("fizz buzz")


from django.views import View


class Index(View):
    template = "index.html"

    def get(self, request):
        return render(request, self.template)
