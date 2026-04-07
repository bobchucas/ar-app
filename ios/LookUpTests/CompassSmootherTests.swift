import XCTest
@testable import LookUp

final class CompassSmootherTests: XCTestCase {

    func testSmoothing() {
        let smoother = CompassSmoother(windowSize: 3)
        _ = smoother.update(10)
        _ = smoother.update(12)
        let result = smoother.update(8)
        // Average of 10, 12, 8 ≈ 10
        XCTAssertEqual(result, 10, accuracy: 1)
    }

    func testWraparound() {
        // Headings around north: 355, 0, 5 should average to ~0
        let smoother = CompassSmoother(windowSize: 3)
        _ = smoother.update(355)
        _ = smoother.update(0)
        let result = smoother.update(5)
        // Should be close to 0 (or 360)
        let normalised = result < 180 ? result : result - 360
        XCTAssertEqual(normalised, 0, accuracy: 2)
    }
}
