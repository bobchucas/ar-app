from __future__ import annotations
from pydantic import BaseModel
from uuid import uuid4


class Feature(BaseModel):
    id: str
    name: str
    type: str
    distance_km: float
    bearing: float
    elevation: float
    latitude: float
    longitude: float

    @classmethod
    def create(cls, name: str, type: str, distance_km: float, bearing: float,
               elevation: float, latitude: float, longitude: float) -> "Feature":
        return cls(
            id=str(uuid4()),
            name=name, type=type, distance_km=distance_km,
            bearing=bearing, elevation=elevation,
            latitude=latitude, longitude=longitude,
        )


class IdentifyResponse(BaseModel):
    features: list[Feature]
