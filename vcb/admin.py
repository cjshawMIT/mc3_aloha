from django.contrib import admin
from vcb.models import Classes

class ClassesAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['class_name','class_number']}),
    ]

admin.site.register(Classes, ClassesAdmin)