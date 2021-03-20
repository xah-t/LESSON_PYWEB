from django.contrib import admin

# Register your models here.
from .models import Tablo


@admin.register(Tablo)
class TabloAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_add', 'public')