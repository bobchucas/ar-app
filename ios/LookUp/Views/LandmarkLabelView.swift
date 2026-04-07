import SwiftUI

/// A floating label for a landmark/geographic feature.
struct LandmarkLabelView: View {
    let feature: LandmarkFeature

    var body: some View {
        VStack(spacing: 2) {
            Text(feature.name)
                .font(.system(size: fontSize, weight: .semibold))
                .foregroundColor(.white)

            Text(subtitle)
                .font(.system(size: fontSize - 2, weight: .regular))
                .foregroundColor(.white.opacity(0.8))
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 4)
        .background(backgroundColor)
        .cornerRadius(6)
        .shadow(color: .black.opacity(0.3), radius: 2, x: 0, y: 1)
    }

    private var subtitle: String {
        let dist = feature.distanceKm
        let distStr = dist < 1
            ? String(format: "%.0fm", dist * 1000)
            : String(format: "%.1fkm", dist)
        return "\(distStr) · \(feature.type)"
    }

    /// Closer features get larger labels.
    private var fontSize: CGFloat {
        switch feature.distanceKm {
        case ..<2: return 14
        case ..<10: return 12
        case ..<30: return 11
        default: return 10
        }
    }

    private var backgroundColor: Color {
        switch feature.type {
        case "peak", "hill", "mountain":
            return .brown.opacity(0.85)
        case "city", "town", "village":
            return .blue.opacity(0.85)
        case "lake", "reservoir":
            return .cyan.opacity(0.85)
        default:
            return .gray.opacity(0.85)
        }
    }
}
