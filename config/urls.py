from django.conf import settings
from django.conf.urls import (
    url,
    static,
    include,
)
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^__baseapp__/', include('baseapp.urls', namespace='baseapp')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
