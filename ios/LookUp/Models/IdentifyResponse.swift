import Foundation

/// Response from POST /identify.
struct IdentifyResponse: Codable {
    let features: [LandmarkFeature]
}
