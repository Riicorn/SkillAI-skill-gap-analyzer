from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from skills.views import landing

urlpatterns = [
    path('', landing, name='landing'),

    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),

    path('dashboard/', include('dashboard.urls')),   # ADD THIS LINE

    path('skills/', include('skills.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('notifications/', include('notifications.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)