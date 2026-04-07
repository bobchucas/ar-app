import Foundation
import CoreLocation
import Combine

/// Central observable state for the app.
final class AppState: ObservableObject {
    // MARK: - Sensor data
    @Published var userLocation: CLLocation?
    @Published var smoothedBearing: Double = 0   // degrees, 0 = North
    @Published var pitchAngle: Double = 0        // radians, positive = looking up

    // MARK: - Identified features
    @Published var landmarks: [LandmarkFeature] = []
    @Published var aircraft: [Aircraft] = []

    // MARK: - UI state
    @Published var isLoading: Bool = false
    @Published var showDebugOverlay: Bool = true
    @Published var errorMessage: String?

    // MARK: - Services
    let locationService = LocationService()
    private var cancellables = Set<AnyCancellable>()

    init() {
        // Forward location updates to published properties
        locationService.$location
            .receive(on: DispatchQueue.main)
            .assign(to: &$userLocation)

        locationService.$smoothedHeading
            .receive(on: DispatchQueue.main)
            .assign(to: &$smoothedBearing)

        locationService.start()
    }
}
