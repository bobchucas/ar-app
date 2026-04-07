import Foundation

/// Client for the backend POST /identify endpoint.
final class IdentifyAPIClient {
    private let baseURL: URL
    private let session: URLSession
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    init(baseURL: URL = URL(string: Constants.backendBaseURL)!) {
        self.baseURL = baseURL
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 5
        self.session = URLSession(configuration: config)
    }

    /// Identify landmarks visible from the given viewpoint.
    func identify(_ request: IdentifyRequest) async throws -> IdentifyResponse {
        let url = baseURL.appendingPathComponent("identify")
        var urlRequest = URLRequest(url: url)
        urlRequest.httpMethod = "POST"
        urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
        urlRequest.httpBody = try encoder.encode(request)

        let (data, response) = try await session.data(for: urlRequest)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw IdentifyError.serverError
        }

        return try decoder.decode(IdentifyResponse.self, from: data)
    }

    enum IdentifyError: Error, LocalizedError {
        case serverError
        var errorDescription: String? { "Backend server error" }
    }
}
