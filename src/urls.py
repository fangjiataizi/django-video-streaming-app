"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from apps.core import views

from src import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('upload/', views.video_upload, name='video_upload'),
    path('play/<int:id>/<int:is_display>', views.video_play, name='video_play'),
    path('mark/<int:id>', views.video_mark, name='video_mark'),
    path('save_coordinates/', views.save_coordinates, name='save_coordinates'),
    path('clear_marks/', views.clear_marks, name='clear_marks'),
    path('generate_content/', views.generate_content, name='generate_content'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
