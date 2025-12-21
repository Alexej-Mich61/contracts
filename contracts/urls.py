# contracts/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf.urls import handler404, handler500, handler403
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    # ←←← АВТОРИЗАЦИЯ ←←←
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html", next_page="/"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/login/"), name="logout"),
    path("", include("contracts_app.urls")),
]

# Кастомные страницы ошибок
handler404 = "contracts_app.views.custom_page_not_found"
handler403 = "contracts_app.views.permission_denied_view"
handler500 = "contracts_app.views.custom_server_error"

if settings.DEBUG or True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
