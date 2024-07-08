from django.contrib import admin
from .models import CustomUser, Organisation

admin.site.register(CustomUser)

admin.site.register(Organisation)

# Register your models here.
