from app.secondhand_app.models import VerifiedProduct, VerifiedProductImage, VerifiedOrder, VerifiedFavorite, VerifiedDevice
from django.db import transaction

with transaction.atomic():
    VerifiedOrder.objects.all().delete()
    VerifiedFavorite.objects.all().delete()
    VerifiedProductImage.objects.all().delete()
    VerifiedProduct.objects.all().delete()
    VerifiedDevice.objects.all().delete()
print('deleted verified products/orders/favorites/images/devices')
