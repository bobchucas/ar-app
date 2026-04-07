import Foundation
import ARKit
import RealityKit
import simd

/// Converts geographic coordinates to screen positions via ARKit's world coordinate system.
struct ScreenProjection {

    /// Convert a bearing (degrees from north) and distance to an ARKit world position.
    ///
    /// ARKit with `gravityAndHeading` alignment:
    /// - +X = East
    /// - +Y = Up
    /// - -Z = North
    ///
    /// For distant features, we cap the AR distance to avoid float precision issues
    /// while preserving the correct direction and elevation angle.
    static func worldPosition(
        bearingDeg: Double,
        distanceM: Double,
        relativeElevationM: Double
    ) -> SIMD3<Float> {
        let bearingRad = bearingDeg * .pi / 180.0

        // Cap visual distance in AR space — labels for features >5km get placed
        // at 500m in AR space with correct direction. This keeps float precision
        // manageable and labels readable.
        let maxARDistance: Double = 500.0
        let arDistance = min(distanceM, maxARDistance)

        // Scale elevation proportionally if we capped distance
        let scale = arDistance / max(distanceM, 1.0)
        let arElevation = relativeElevationM * scale

        let x = Float(arDistance * sin(bearingRad))     // East component
        let z = Float(-arDistance * cos(bearingRad))     // North component (negative Z)
        let y = Float(arElevation)                       // Up component

        return SIMD3<Float>(x, y, z)
    }

    /// Project a world position to a 2D screen point using the ARView.
    /// Returns nil if the point is behind the camera.
    static func projectToScreen(
        worldPos: SIMD3<Float>,
        arView: ARView
    ) -> CGPoint? {
        // RealityKit's project returns the point in the view's coordinate space
        let screenPoint = arView.project(worldPos)
        guard let point = screenPoint else { return nil }

        // Check if point is within reasonable screen bounds (with margin)
        let bounds = arView.bounds
        let margin: CGFloat = 100
        let expandedBounds = bounds.insetBy(dx: -margin, dy: -margin)
        guard expandedBounds.contains(point) else { return nil }

        return point
    }
}
