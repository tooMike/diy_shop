from main.models import Category, Manufacturer

def categories(request):
    return {'categories': Category.objects.all()}

def manufacturers(request):
    return {'manufacturers': Manufacturer.objects.all()}
