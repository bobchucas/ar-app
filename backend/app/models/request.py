from pydantic import BaseModel, Field


class IdentifyRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: float = Field(..., description="Meters above sea level")
    bearing: float = Field(..., ge=0, lt=360, description="Compass heading in degrees")
    pitch: float = Field(..., ge=-90, le=90, description="Device pitch in degrees, positive = up")
    fov_horizontal: float = Field(default=69.0, description="Horizontal FOV in degrees")
    fov_vertical: float = Field(default=54.0, description="Vertical FOV in degrees")
