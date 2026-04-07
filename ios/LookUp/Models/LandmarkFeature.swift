import Foundation

/// A named geographic feature returned by the backend.
struct LandmarkFeature: Identifiable, Codable {
    let id: UUID
    let name: String
    let type: String           // e.g. "peak", "city", "lake"
    let distanceKm: Double
    let bearing: Double        // degrees from north
    let elevation: Double      // meters above sea level
    let latitude: Double
    let longitude: Double

    enum CodingKeys: String, CodingKey {
        case id, name, type
        case distanceKm = "distance_km"
        case bearing, elevation, latitude, longitude
    }
}
