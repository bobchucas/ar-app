import Foundation
import CoreLocation
import Combine

/// Manages GPS location and compass heading updates.
final class LocationService: NSObject, ObservableObject {
    private let locationManager = CLLocationManager()
    private let compassSmoother = CompassSmoother()

    @Published var location: CLLocation?
    @Published var smoothedHeading: Double = 0

    override init() {
        super.init()
        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest
        locationManager.headingFilter = 0.5  // degrees — responsive without flooding
        locationManager.distanceFilter = 5   // meters
    }

    func start() {
        locationManager.requestWhenInUseAuthorization()
        locationManager.startUpdatingLocation()
        locationManager.startUpdatingHeading()
    }

    func stop() {
        locationManager.stopUpdatingLocation()
        locationManager.stopUpdatingHeading()
    }
}

extension LocationService: CLLocationManagerDelegate {
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let latest = locations.last else { return }
        // Filter out stale or wildly inaccurate readings
        guard latest.horizontalAccuracy >= 0, latest.horizontalAccuracy < 100 else { return }
        location = latest
    }

    func locationManager(_ manager: CLLocationManager, didUpdateHeading newHeading: CLHeading) {
        // Use true heading when available, magnetic otherwise
        let heading = newHeading.trueHeading >= 0 ? newHeading.trueHeading : newHeading.magneticHeading
        smoothedHeading = compassSmoother.update(heading)
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("[LocationService] Error: \(error.localizedDescription)")
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            start()
        default:
            break
        }
    }
}
