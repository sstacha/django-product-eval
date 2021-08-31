"""docroot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('eval/', include('eval.urls')),
]

# ------------------------ DOCROOT CMS URLS ------------------------------------
# add our different urls for the cms to work
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from docrootcms.views import MarkdownImageUploadView

urlpatterns += [
    path('_cms/', include('docrootcms.urls')),
    path('blog/', include('docrootcms.contrib.blog.urls')),
    # sas 2020-09-27 : override the markdownx url and apply our overridden view/form instead
    # NOTE: don't forget to copy the js changes into static for transferring the new field to the view
    path('markdownx/upload/', MarkdownImageUploadView.as_view(), name='markdownx_upload'),
    path('markdownx/', include('markdownx.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ------------------------ DOCROOT CMS URLS ------------------------------------