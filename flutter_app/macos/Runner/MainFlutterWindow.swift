import Cocoa
import FlutterMacOS

class MainFlutterWindow: NSWindow {
  override func awakeFromNib() {
    let flutterViewController = FlutterViewController()
    let windowFrame = self.frame
    let targetSize = NSSize(width: 1200, height: 900)
    let targetFrame = NSRect(
      x: windowFrame.origin.x,
      y: windowFrame.origin.y,
      width: targetSize.width,
      height: targetSize.height
    )
    self.contentViewController = flutterViewController
    self.setFrame(targetFrame, display: true)
    self.minSize = NSSize(width: 1100, height: 800)
    self.center()

    RegisterGeneratedPlugins(registry: flutterViewController)

    super.awakeFromNib()
  }
}
