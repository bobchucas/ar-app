import SwiftUI
import ARKit

/// Overlay that projects landmark and aircraft labels onto the camera feed.
/// Uses TimelineView for per-frame updates of screen positions.
struct LabelOverlayView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        GeometryReader { geometry in
            TimelineView(.animation) { timeline in
                ZStack {
                    // Landmark labels
                    ForEach(appState.landmarks) { landmark in
                        if let screenPos = screenPosition(for: landmark) {
                            LandmarkLabelView(feature: landmark)
                                .position(x: screenPos.x, y: screenPos.y)
                        }
                    }

                    // Aircraft labels
                    ForEach(appState.aircraft) { aircraft in
                        if let screenPos = screenPosition(forAircraft: aircraft) {
                            FlightInfoCard(aircraft: aircraft)
                                .position(x: screenPos.x, y: screenPos.y)
                        }
                    }
                }
                .frame(width: geometry.size.width, height: geometry.size.height)
            }
        }
        .allowsHitTesting(false) // Let touches pass through to AR view
    }

    private func screenPosition(for landmark: LandmarkFeature) -> CGPoint? {
        guard let arView = ARViewStore.shared.arView,
              let userAlt = appState.userLocation?.altitude else { return nil }

        let relativeElevation = landmark.elevation - userAlt
        let worldPos = ScreenProjection.worldPosition(
            bearingDeg: landmark.bearing,
            distanceM: landmark.distanceKm * 1000,
            relativeElevationM: relativeElevation
        )
        return ScreenProjection.projectToScreen(worldPos: worldPos, arView: arView)
    }

    private func screenPosition(forAircraft aircraft: Aircraft) -> CGPoint? {
        guard let arView = ARViewStore.shared.arView,
              let bearing = aircraft.bearingFromObserver,
              let userAlt = appState.userLocation?.altitude else { return nil }

        let relativeElevation = aircraft.altitudeM - userAlt
        let distanceM = (aircraft.distanceFromObserverKm ?? 10) * 1000
        let worldPos = ScreenProjection.worldPosition(
            bearingDeg: bearing,
            distanceM: distanceM,
            relativeElevationM: relativeElevation
        )
        return ScreenProjection.projectToScreen(worldPos: worldPos, arView: arView)
    }
}
