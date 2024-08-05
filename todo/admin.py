from django.contrib import admin
from .models import todo
# Register your models here.

class todo_admin(admin.ModelAdmin):
    readonly_fields = ('created',)

admin.site.register(todo, todo_admin)