import Foundation

/// Request body sent to POST /identify.
struct IdentifyRequest: Codable {
    let latitude: Double
    let longitude: Double
    let altitude: Double       // meters above sea level
    let bearing: Double        // compass heading in degrees
    let pitch: Double          // device pitch in degrees (positive = up)
    let fovHorizontal: Double  // horizontal field of view in degrees
    let fovVertical: Double    // vertical field of view in degrees

    enum CodingKeys: String, CodingKey {
        case latitude, longitude, altitude, bearing, pitch
        case fovHorizontal = "fov_horizontal"
        case fovVertical = "fov_vertical"
    }
}
