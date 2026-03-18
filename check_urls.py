import django
django.setup()

from django.urls import get_resolver
from users.urls import urlpatterns as users_urls
from materials.urls import urlpatterns as materials_urls

print("=" * 50)
print("ПРОВЕРКА URL-ОВ")
print("=" * 50)

print("\n1. URL-ы из materials.urls:")
for pattern in materials_urls:
    print(f"   {pattern}")

print("\n2. URL-ы из users.urls:")
for pattern in users_urls:
    print(f"   {pattern}")

print("\n3. Все зарегистрированные API URL-ы:")
resolver = get_resolver()
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'pattern'):
        print(f"   /{pattern.pattern}")