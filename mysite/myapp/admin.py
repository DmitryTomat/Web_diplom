from django.contrib import admin
from django.contrib.auth.models import User

# Отмена регистрации модели User по умолчанию
admin.site.unregister(User)

# Регистрация модели User в админ-панели с использованием декоратора
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass