from fastapi import APIRouter
from app.models.request import IdentifyRequest
from app.models.response import IdentifyResponse, Feature
from app.core.viewshed import compute_viewshed
from app.gazetteer.lookup import find_features_near_hits

router = APIRouter()


@router.post("/identify", response_model=IdentifyResponse)
async def identify(req: IdentifyRequest) -> IdentifyResponse:
    """Identify visible landmarks from the given viewpoint."""
    # Step 1: Cast rays and find terrain hits
    hits = compute_viewshed(
        lat=req.latitude,
        lon=req.longitude,
        altitude=req.altitude,
        bearing=req.bearing,
        pitch=req.pitch,
        fov_h=req.fov_horizontal,
        fov_v=req.fov_vertical,
    )

    # Step 2: Query gazetteer for named features near the terrain hits
    features = find_features_near_hits(hits)

    # Step 3: Deduplicate, sort by distance, limit to 20
    seen = set()
    unique = []
    for f in sorted(features, key=lambda x: x.distance_km):
        if f.name not in seen:
            seen.add(f.name)
            unique.append(f)
        if len(unique) >= 20:
            break

    return IdentifyResponse(features=unique)
