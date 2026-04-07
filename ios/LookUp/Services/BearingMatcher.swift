import Foundation
import CoreLocation

/// Matches aircraft positions against the user's field of view.
struct BearingMatcher {

    /// Enrich aircraft with bearing/distance/elevation from the observer,
    /// then filter to only those within the user's field of view.
    static func matchVisible(
        aircraft: [Aircraft],
        from location: CLLocation,
        bearing: Double,
        pitch: Double,
        fovH: Double,
        fovV: Double
    ) -> [Aircraft] {
        aircraft.compactMap { plane in
            var enriched = plane

            // Compute bearing from observer to aircraft
            let planeLoc = CLLocation(latitude: plane.latitude, longitude: plane.longitude)
            let dist = location.distance(from: planeLoc) / 1000.0 // km
            let brg = GeoMath.bearing(
                from: location.coordinate,
                to: CLLocationCoordinate2D(latitude: plane.latitude, longitude: plane.longitude)
            )

            // Compute elevation angle
            let altDelta = plane.altitudeM - location.altitude
            let elevAngle = atan2(altDelta, dist * 1000) * 180 / .pi // degrees

            enriched.bearingFromObserver = brg
            enriched.distanceFromObserverKm = dist
            enriched.elevationAngleFromObserver = elevAngle

            // Check if within FOV
            let bearingDiff = GeoMath.angleDifference(brg, bearing)
            let pitchDiff = abs(elevAngle - pitch)

            guard abs(bearingDiff) <= fovH / 2 + 5,  // +5° margin
                  pitchDiff <= fovV / 2 + 5 else { return nil }

            return enriched
        }
    }
}
