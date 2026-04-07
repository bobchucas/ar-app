import SwiftUI
import ARKit
import RealityKit

/// Wraps an ARView for use in SwiftUI. Configures world tracking with
/// gravity+heading alignment so the coordinate system is compass-aligned:
/// +X = East, +Y = Up, -Z = North.
struct ARCameraView: UIViewRepresentable {
    @EnvironmentObject var appState: AppState

    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        arView.automaticallyConfigureSession = false

        let config = ARWorldTrackingConfiguration()
        config.worldAlignment = .gravityAndHeading
        config.planeDetection = []
        // Disable unnecessary features for performance
        config.environmentTexturing = .none
        config.isLightEstimationEnabled = false

        arView.session.run(config)
        arView.session.delegate = context.coordinator

        // Store reference for screen projection
        context.coordinator.arView = arView
        ARViewStore.shared.arView = arView

        return arView
    }

    func updateUIView(_ uiView: ARView, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(appState: appState)
    }

    class Coordinator: NSObject, ARSessionDelegate {
        let appState: AppState
        weak var arView: ARView?

        init(appState: AppState) {
            self.appState = appState
        }

        func session(_ session: ARSession, didUpdate frame: ARFrame) {
            // Extract pitch from camera transform.
            // The camera's forward vector is the third column of the transform (negated).
            let transform = frame.camera.transform
            let forward = simd_make_float3(
                -transform.columns.2.x,
                -transform.columns.2.y,
                -transform.columns.2.z
            )
            // Pitch = angle between forward vector and horizontal plane
            let pitch = Double(asin(forward.y))

            DispatchQueue.main.async {
                self.appState.pitchAngle = pitch
            }
        }

        func session(_ session: ARSession, didFailWithError error: Error) {
            DispatchQueue.main.async {
                self.appState.errorMessage = "AR session error: \(error.localizedDescription)"
            }
        }
    }
}

/// Provides access to the ARView for screen projection from anywhere in the view hierarchy.
final class ARViewStore {
    static let shared = ARViewStore()
    weak var arView: ARView?
    private init() {}
}
