import XCTest
import CoreLocation
@testable import LookUp

final class GeoMathTests: XCTestCase {

    func testBearingNorth() {
        // From London (51.5, -0.1) looking north to Edinburgh-ish (55.9, -0.1)
        let from = CLLocationCoordinate2D(latitude: 51.5, longitude: -0.1)
        let to = CLLocationCoordinate2D(latitude: 55.9, longitude: -0.1)
        let bearing = GeoMath.bearing(from: from, to: to)
        // Should be roughly north (~0°/360°)
        XCTAssertEqual(bearing, 0, accuracy: 2.0)
    }

    func testBearingEast() {
        let from = CLLocationCoordinate2D(latitude: 51.5, longitude: -0.1)
        let to = CLLocationCoordinate2D(latitude: 51.5, longitude: 0.5)
        let bearing = GeoMath.bearing(from: from, to: to)
        XCTAssertEqual(bearing, 90, accuracy: 2.0)
    }

    func testAngleDifferenceWraparound() {
        XCTAssertEqual(GeoMath.angleDifference(10, 350), 20, accuracy: 0.01)
        XCTAssertEqual(GeoMath.angleDifference(350, 10), -20, accuracy: 0.01)
        XCTAssertEqual(GeoMath.angleDifference(180, 0), 180, accuracy: 0.01)
    }

    func testDistanceKnown() {
        // London to Paris ~ 344km
        let london = CLLocationCoordinate2D(latitude: 51.5074, longitude: -0.1278)
        let paris = CLLocationCoordinate2D(latitude: 48.8566, longitude: 2.3522)
        let dist = GeoMath.distance(from: london, to: paris)
        XCTAssertEqual(dist / 1000, 344, accuracy: 5)
    }
}
