import Foundation

enum Constants {
    /// Backend API base URL. For local dev, use your Mac's local network IP.
    /// Change this to your actual IP when running on a physical device.
    static let backendBaseURL = "http://100.87.237.56:8200"

    /// OpenSky polling interval in seconds.
    static let openSkyPollInterval: TimeInterval = 10

    /// Minimum bearing change (degrees) to trigger a new /identify request.
    static let bearingChangeThreshold: Double = 5.0

    /// Minimum pitch change (degrees) to trigger a new /identify request.
    static let pitchChangeThreshold: Double = 3.0

    /// Debounce delay after sensor change before firing API request.
    static let apiDebounceDelay: TimeInterval = 0.3

    /// Maximum time between API requests regardless of movement.
    static let maxApiInterval: TimeInterval = 3.0

    /// Approximate horizontal FOV of iPhone camera (wide lens, degrees).
    static let defaultFovHorizontal: Double = 69.0

    /// Approximate vertical FOV of iPhone camera (wide lens, degrees).
    static let defaultFovVertical: Double = 54.0
}
