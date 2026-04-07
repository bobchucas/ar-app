import Foundation

/// An aircraft from the OpenSky Network API.
struct Aircraft: Identifiable {
    let id: String             // ICAO24 transponder address
    let callsign: String?
    let airlineName: String?
    let latitude: Double
    let longitude: Double
    let altitudeM: Double      // barometric altitude in meters
    let velocityMs: Double?    // ground speed m/s
    let trueTrack: Double?     // heading in degrees
    let verticalRate: Double?  // m/s, positive = climbing
    let onGround: Bool

    /// Computed bearing from a given observer position.
    var bearingFromObserver: Double?
    /// Computed elevation angle from observer.
    var elevationAngleFromObserver: Double?
    /// Computed distance from observer in km.
    var distanceFromObserverKm: Double?
}
