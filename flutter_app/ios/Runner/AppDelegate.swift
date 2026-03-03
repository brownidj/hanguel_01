import Flutter
import UIKit
import audio_session
import just_audio
import shared_preferences_foundation

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // Manual registration to avoid path_provider_foundation crash on iOS 26.
    if let registrar = registrar(forPlugin: "AudioSessionPlugin") {
      AudioSessionPlugin.register(with: registrar)
    }
    if let registrar = registrar(forPlugin: "JustAudioPlugin") {
      JustAudioPlugin.register(with: registrar)
    }
    if let registrar = registrar(forPlugin: "SharedPreferencesPlugin") {
      SharedPreferencesPlugin.register(with: registrar)
    }
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
