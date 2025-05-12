from django.urls import path
from .views import FuelRouteView, ProcessCsvView

urlpatterns = [
    path('fuel-route/', FuelRouteView.as_view(), name='fuel-route'),
    path('csv-process/', ProcessCsvView.as_view(), name='CSV-process'),
]
