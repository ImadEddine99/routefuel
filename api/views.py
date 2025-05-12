from django.views import View
from django.http import JsonResponse

from .geocode_csv_preprocess import process_csv
from .utils import get_route_data, find_optimal_fuel_stops, calculate_total_cost
import traceback
from rest_framework import status

class FuelRouteView(View):
    def get(self, request):
        start = request.GET.get('start')  # e.g., "Chicago, IL"
        end = request.GET.get('end')      # e.g., "Los Angeles, CA"

        if not start or not end:
            return JsonResponse({'error': 'Missing start or end location'}, status=400)

        try:
            route_data = get_route_data(start, end)  # API call to OpenRouteService or similar
            fuel_stops = find_optimal_fuel_stops(route_data)  # Based on fuel range and prices
            total_cost = calculate_total_cost(route_data, fuel_stops)

            return JsonResponse({
                'route': route_data,
                # 'route': route_data,
                'fuel_stops': fuel_stops,
                'total_fuel_cost': round(total_cost, 2)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()  # Logs full error stack trace
            trace= traceback.format_exc()
            content={"err":f" {e}","trace":str(trace)}
            return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)
class ProcessCsvView(View):
    def get(self,request):
        try:
            process_csv()
            return JsonResponse({
                'msg': 'done'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            traceback.print_exc()  # Logs full error stack trace
            trace= traceback.format_exc()
            content={"err":f" {e}","trace":str(trace)}
            return JsonResponse(content, status=status.HTTP_400_BAD_REQUEST)