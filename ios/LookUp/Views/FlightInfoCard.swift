import SwiftUI

/// Floating card showing aircraft information.
struct FlightInfoCard: View {
    let aircraft: Aircraft

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            HStack(spacing: 4) {
                Image(systemName: "airplane")
                    .font(.system(size: 10))
                Text(aircraft.callsign?.trimmingCharacters(in: .whitespaces) ?? "Unknown")
                    .font(.system(size: 12, weight: .bold))
            }

            if let airline = aircraft.airlineName {
                Text(airline)
                    .font(.system(size: 10))
            }

            Text(details)
                .font(.system(size: 9))
                .foregroundColor(.white.opacity(0.8))
        }
        .foregroundColor(.white)
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(Color.orange.opacity(0.85))
        .cornerRadius(6)
        .shadow(color: .black.opacity(0.3), radius: 2, x: 0, y: 1)
    }

    private var details: String {
        let altFt = Int(aircraft.altitudeM * 3.28084) // meters to feet
        var parts = ["\(altFt)ft"]
        if let speed = aircraft.velocityMs {
            let knots = Int(speed * 1.94384) // m/s to knots
            parts.append("\(knots)kts")
        }
        if let dist = aircraft.distanceFromObserverKm {
            parts.append(String(format: "%.0fkm", dist))
        }
        return parts.joined(separator: " · ")
    }
}
