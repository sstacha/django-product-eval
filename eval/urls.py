from django.urls import path

from . import views

urlpatterns = [
    # ex: /eval/api/generate/virtual/
    path('api/generate/<product_code>/', views.generate_missing_evaluations, name='generate_evaluations'),
    path('api/export/', views.export_evaluations, name='export_evaluations'),
]