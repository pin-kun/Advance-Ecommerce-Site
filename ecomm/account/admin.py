from django.contrib import admin
from account.models import Customer

# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'firstname', 'lastname', 'user', 'email', 'id_user', 'profileimg']
admin.site.register(Customer, CustomerAdmin)