from django.shortcuts import render


def create_order(request):
    context = {}
    return render(request, template_name="", context=context)
