import SwiftUI

/// Shows live sensor data for development/debugging.
struct DebugOverlayView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(alignment: .leading) {
            Spacer()

            VStack(alignment: .leading, spacing: 4) {
                if let loc = appState.userLocation {
                    debugRow("LAT", String(format: "%.5f", loc.coordinate.latitude))
                    debugRow("LON", String(format: "%.5f", loc.coordinate.longitude))
                    debugRow("ALT", String(format: "%.1fm", loc.altitude))
                    debugRow("H.ACC", String(format: "%.1fm", loc.horizontalAccuracy))
                } else {
                    debugRow("GPS", "Waiting...")
                }

                debugRow("BRG", String(format: "%.1f°", appState.smoothedBearing))
                debugRow("PITCH", String(format: "%.1f°", appState.pitchAngle * 180 / .pi))
                debugRow("LMKS", "\(appState.landmarks.count)")
                debugRow("PLANES", "\(appState.aircraft.count)")
            }
            .padding(10)
            .background(.black.opacity(0.6))
            .cornerRadius(8)
            .padding(.horizontal, 12)
            .padding(.bottom, 40)
        }
    }

    private func debugRow(_ label: String, _ value: String) -> some View {
        HStack {
            Text(label)
                .font(.system(size: 10, weight: .bold, design: .monospaced))
                .foregroundColor(.green.opacity(0.8))
                .frame(width: 50, alignment: .leading)
            Text(value)
                .font(.system(size: 10, design: .monospaced))
                .foregroundColor(.green)
        }
    }
}
