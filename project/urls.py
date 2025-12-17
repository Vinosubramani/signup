from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from project.views import user_login, logout_view, signup

urlpatterns = [
    # ---------------- Admin ----------------
    path('admin/', admin.site.urls),
    path(
        'admin/logout/',
        auth_views.LogoutView.as_view(next_page='/'),
        name='admin_logout'
    ),

    # ---------------- Authentication ----------------
    path('login/', user_login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup, name='signup'),

    # ---------------- Other Apps ----------------
    path('master-admin/', include('administartor.urls')),
    path('staff/', include('staff.urls')),
    path('student/', include('app.urls')),

    # ---------------- Product App (HOME) ----------------
    path('', include('product.urls')),   # Home = /
]

# ---------------- Media Files (IMPORTANT) ----------------
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
