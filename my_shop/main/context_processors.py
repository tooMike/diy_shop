from main.models import Category, Manufacturer

def categories(request):
    return {'categories': Category.objects.filter(is_active=True)}

def manufacturers(request):
    return {'manufacturers': Manufacturer.objects.filter(is_active=True)}
