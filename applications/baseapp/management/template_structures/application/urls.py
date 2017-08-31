TEMPLATE_URLS = """from django.conf.urls import url

from .views import {app_name_title}View

urlpatterns = [
    url(regex=r'^$', view={app_name_title}View.as_view(), name='{app_name}_index'),
]

"""


__all__ = [
    'TEMPLATE_URLS',
]