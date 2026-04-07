import Foundation
import CoreLocation

/// Geographic math utilities.
enum GeoMath {

    /// Compute bearing (degrees, 0=North, clockwise) from one coordinate to another.
    /// Uses the forward azimuth formula on a sphere.
    static func bearing(from: CLLocationCoordinate2D, to: CLLocationCoordinate2D) -> Double {
        let lat1 = from.latitude.radians
        let lat2 = to.latitude.radians
        let dLon = (to.longitude - from.longitude).radians

        let y = sin(dLon) * cos(lat2)
        let x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
        let bearing = atan2(y, x).degrees

        return (bearing + 360).truncatingRemainder(dividingBy: 360)
    }

    /// Haversine distance between two coordinates in meters.
    static func distance(from: CLLocationCoordinate2D, to: CLLocationCoordinate2D) -> Double {
        let R = 6371000.0 // Earth radius in meters
        let lat1 = from.latitude.radians
        let lat2 = to.latitude.radians
        let dLat = (to.latitude - from.latitude).radians
        let dLon = (to.longitude - from.longitude).radians

        let a = sin(dLat / 2) * sin(dLat / 2)
            + cos(lat1) * cos(lat2) * sin(dLon / 2) * sin(dLon / 2)
        let c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c
    }

    /// Signed angular difference between two bearings in degrees.
    /// Result is in range (-180, 180].
    static func angleDifference(_ a: Double, _ b: Double) -> Double {
        var diff = a - b
        while diff > 180 { diff -= 360 }
        while diff <= -180 { diff += 360 }
        return diff
    }
}

// MARK: - Convenience extensions

private extension Double {
    var radians: Double { self * .pi / 180 }
    var degrees: Double { self * 180 / .pi }
}
