import Foundation
import CoreLocation

/// Client for the OpenSky Network REST API.
/// Fetches real-time aircraft positions in a bounding box around the user.
final class OpenSkyClient {
    private let session: URLSession
    private let decoder = JSONDecoder()

    /// Known airline ICAO prefixes → names (subset for prototype).
    private static let airlines: [String: String] = [
        "BAW": "British Airways", "RYR": "Ryanair", "EZY": "easyJet",
        "DLH": "Lufthansa", "AFR": "Air France", "KLM": "KLM",
        "UAE": "Emirates", "SWR": "Swiss", "DAL": "Delta",
        "AAL": "American Airlines", "UAL": "United", "THY": "Turkish Airlines",
        "IBE": "Iberia", "SAS": "SAS", "FIN": "Finnair",
        "AER": "Aer Lingus", "LOG": "Loganair", "BEE": "Flybe",
        "VIR": "Virgin Atlantic", "TOM": "TUI", "EIN": "Aer Lingus",
        "EXS": "Jet2", "WZZ": "Wizz Air", "NAX": "Norwegian",
    ]

    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 10
        self.session = URLSession(configuration: config)
    }

    /// Fetch aircraft within ~200km of the given location.
    func fetchNearby(location: CLLocation) async throws -> [Aircraft] {
        let lat = location.coordinate.latitude
        let lon = location.coordinate.longitude
        let delta = 2.0 // ~200km

        let url = URL(string: "https://opensky-network.org/api/states/all"
            + "?lamin=\(lat - delta)&lomin=\(lon - delta)"
            + "&lamax=\(lat + delta)&lomax=\(lon + delta)")!

        let (data, _) = try await session.data(from: url)
        let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
        guard let states = json?["states"] as? [[Any?]] else { return [] }

        return states.compactMap { state -> Aircraft? in
            guard state.count >= 17,
                  let icao = state[0] as? String,
                  let lat = state[6] as? Double,
                  let lon = state[5] as? Double,
                  let alt = state[7] as? Double else { return nil }

            let onGround = (state[8] as? Bool) ?? false
            guard !onGround else { return nil } // Skip grounded aircraft

            let callsign = (state[1] as? String)?.trimmingCharacters(in: .whitespaces)
            let airlinePrefix = callsign.map { String($0.prefix(3)) }
            let airlineName = airlinePrefix.flatMap { Self.airlines[$0] }

            return Aircraft(
                id: icao,
                callsign: callsign,
                airlineName: airlineName,
                latitude: lat,
                longitude: lon,
                altitudeM: alt,
                velocityMs: state[9] as? Double,
                trueTrack: state[10] as? Double,
                verticalRate: state[11] as? Double,
                onGround: onGround,
                bearingFromObserver: nil,
                elevationAngleFromObserver: nil,
                distanceFromObserverKm: nil
            )
        }
    }
}
