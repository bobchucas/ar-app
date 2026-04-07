import XCTest
import CoreLocation
@testable import LookUp

final class BearingMatcherTests: XCTestCase {

    func testAircraftInFOV() {
        // Observer at Belfast (54.6, -5.93), looking north (bearing 0)
        let observer = CLLocation(
            coordinate: CLLocationCoordinate2D(latitude: 54.6, longitude: -5.93),
            altitude: 50, horizontalAccuracy: 5, verticalAccuracy: 5, timestamp: Date()
        )

        let plane = Aircraft(
            id: "abc123", callsign: "RYR123", airlineName: "Ryanair",
            latitude: 55.0, longitude: -5.93, altitudeM: 10000,
            velocityMs: 250, trueTrack: 180, verticalRate: 0, onGround: false,
            bearingFromObserver: nil, elevationAngleFromObserver: nil, distanceFromObserverKm: nil
        )

        let matched = BearingMatcher.matchVisible(
            aircraft: [plane], from: observer,
            bearing: 0, pitch: 10, fovH: 69, fovV: 54
        )

        XCTAssertEqual(matched.count, 1)
        XCTAssertNotNil(matched.first?.bearingFromObserver)
    }
}
