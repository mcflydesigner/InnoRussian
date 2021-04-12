from django.contrib import admin

from .models import (Category,
                     SubCategory,
                     Card,
                     Favourite)

# Register all models to control them in the admin panel
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Card)
admin.site.register(Favourite)