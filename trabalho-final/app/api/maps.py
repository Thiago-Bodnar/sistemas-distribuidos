from fastapi import APIRouter
from ..services import maps_service

router = APIRouter()

@router.get("/rota_endereco")
async def rota_endereco(origem: str, destino: str):
    """
    Recebe endereço do motorista e do passageiro como string.
    Retorna rota, distância e tempo.
    """
    orig_coords = await maps_service.geocode_address(origem)
    dest_coords = await maps_service.geocode_address(destino)
    
    if not orig_coords or not dest_coords:
        return {"error": "Não foi possível geocodificar algum endereço."}

    geometry = await maps_service.calculate_route(orig_coords, dest_coords)
    distance = await maps_service.calculate_distance(orig_coords, dest_coords)
    duration = await maps_service.estimate_time(orig_coords, dest_coords)

    return {
        "distance_km": distance,
        "duration_min": duration
    }
