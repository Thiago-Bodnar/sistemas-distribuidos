from ..infra.maps_client import MapsClient
import requests
import os

# Aqui você injeta a chave correta
maps_client = MapsClient(api_key="eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRmOTM1YjhiODA0YTRhYWNhOGY2NDA2MmMwNzg0NTFjIiwiaCI6Im11cm11cjY0In0=")

async def calculate_route(origin: dict, destination: dict):
    start = [origin["lng"], origin["lat"]]
    end = [destination["lng"], destination["lat"]]
    route = await maps_client.route(start, end)
    geometry = route["features"][0]["geometry"]
    return geometry

async def calculate_distance(origin: dict, destination: dict):
    start = [origin["lng"], origin["lat"]]
    end = [destination["lng"], destination["lat"]]
    route = await maps_client.route(start, end)
    distance_m = route["features"][0]["properties"]["summary"]["distance"]
    return distance_m / 1000  # km

async def estimate_time(origin: dict, destination: dict):
    start = [origin["lng"], origin["lat"]]
    end = [destination["lng"], destination["lat"]]
    route = await maps_client.route(start, end)
    duration_s = route["features"][0]["properties"]["summary"]["duration"]
    return duration_s / 60  # minutos

async def geocode_address(address: str):
    """
    Recebe um endereço em string e retorna {lat, lng}.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "MeuAppDeTeste/1.0 (kaikevttuerpe@gmail.com)"
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    try:
        data = response.json()
    except ValueError:
        # caso não retorne JSON, mostrar erro
        print("Erro ao geocodificar:", response.text)
        return None
    
    if not data:
        return None
    
    return {
        "lat": float(data[0]["lat"]),
        "lng": float(data[0]["lon"])
    }
