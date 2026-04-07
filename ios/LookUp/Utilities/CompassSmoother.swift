import Foundation

/// Smooths compass heading using a circular rolling average.
/// Handles the 360°/0° wraparound correctly using sin/cos decomposition.
final class CompassSmoother {
    private let windowSize: Int
    private var sinValues: [Double] = []
    private var cosValues: [Double] = []

    init(windowSize: Int = 10) {
        self.windowSize = windowSize
    }

    /// Add a new heading sample (degrees) and return the smoothed heading.
    func update(_ headingDeg: Double) -> Double {
        let rad = headingDeg * .pi / 180.0
        sinValues.append(sin(rad))
        cosValues.append(cos(rad))

        // Keep only the last `windowSize` samples
        if sinValues.count > windowSize {
            sinValues.removeFirst()
            cosValues.removeFirst()
        }

        let avgSin = sinValues.reduce(0, +) / Double(sinValues.count)
        let avgCos = cosValues.reduce(0, +) / Double(cosValues.count)

        var result = atan2(avgSin, avgCos) * 180.0 / .pi
        if result < 0 { result += 360 }
        return result
    }

    func reset() {
        sinValues.removeAll()
        cosValues.removeAll()
    }
}
