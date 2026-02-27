import openrouteservice
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MapsClient:
    def __init__(self, api_key: str):
        self.client = openrouteservice.Client(key=api_key)
        self.executor = ThreadPoolExecutor()

    async def route(self, start: list, end: list):
        """
        start/end: [longitude, latitude]
        ORS não é nativamente async, então rodamos em thread separada.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: self.client.directions(
                coordinates=[start, end],
                profile="driving-car",
                format="geojson"
            )
        )
