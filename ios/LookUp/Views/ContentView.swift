import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        ZStack {
            ARCameraView()
                .ignoresSafeArea()

            LabelOverlayView()

            if appState.showDebugOverlay {
                DebugOverlayView()
            }

            if let error = appState.errorMessage {
                VStack {
                    Text(error)
                        .font(.caption)
                        .foregroundColor(.white)
                        .padding(8)
                        .background(.red.opacity(0.8))
                        .cornerRadius(8)
                    Spacer()
                }
                .padding(.top, 60)
            }
        }
        .statusBarHidden()
    }
}
