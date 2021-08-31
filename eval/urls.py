from django.urls import path

from . import views

urlpatterns = [
    # ex: /polls/5/
    path('api/generate/<product_code>/', views.generate_missing_evaluations, name='generate_evaluations'),
]