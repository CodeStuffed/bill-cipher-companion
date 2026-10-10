import AppKit
import ApplicationServices

/// The "push windows around" feature: when the character walks into an app
/// window during a stroll, it nudges that window a few points sideways —
/// physically, smoothly, via the Accessibility API (`AXSetAttributeValue`
/// on the window's position, animated over ~0.2s so it slides rather than
/// snaps). Gated behind the Settings toggle + the Accessibility permission;
/// completely inert otherwise, and it never touches the frontmost window the
/// user is typing in (same rule as the minimize prank).
@MainActor
enum WindowPusher {
    /// How far a single push shoves the window, in points.
    private static let pushDistance: CGFloat = 24
    /// One push per window per stroll beat — repeated contact re-nudges
    /// only after the character has walked away and come back.
    private static var recentlyPushed: [CGWindowID: Date] = [:]
    private static let pushCooldown: TimeInterval = 4

    static func maybePush(panel: NSPanel, at feet: CGPoint) {
        guard AppPreferences().isWindowPushingEnabled, WindowTitleReader.isTrusted else { return }
        guard let screen = panel.screen ?? NSScreen.main else { return }

        // The window being walked into: the topmost platform whose rect
        // contains the character's feet, excluding our own panel.
        guard let target = WindowTopology
            .platforms(excludingWindowNumber: panel.windowNumber, fresh: true)
            .first(where: { $0.rect.insetBy(dx: -6, dy: -6).contains(feet) })
        else { return }

        // Never the frontmost window — nudging what the user is actively
        // using would be hostile, not playful (same rule as the prank).
        guard let front = NSWorkspace.shared.frontmostApplication,
              target.ownerPID != front.processIdentifier
        else { return }

        // Cooldown per window.
        if let last = recentlyPushed[CGWindowID(target.windowNumber)],
            Date().timeIntervalSince(last) < pushCooldown { return }
        recentlyPushed[CGWindowID(target.windowNumber)] = Date()
        if recentlyPushed.count > 16 {
            recentlyPushed = Dictionary(
                recentlyPushed.filter { Date().timeIntervalSince($0.value) < pushCooldown },
                uniquingKeysWith: { a, _ in a }
            )
        }

        // Direction: away from where the character is walking toward.
        let pushRight = feet.x < target.rect.midX
        animatePush(windowNumber: CGWindowID(target.windowNumber), by: pushRight ? pushDistance : -pushDistance)
    }

    /// Smooth push: ~8 small `AXSetAttributeValue` steps over 0.2s — a slide,
    /// not a teleport. Skips gracefully if the window isn't AX-movable
    /// (fullscreen, some system windows).
    private static func animatePush(windowNumber: CGWindowID, by dx: CGFloat) {
        // Resolve the AX window for this CGWindowID.
        guard let axWindow = AXWindowIDToAXWindow(windowNumber) else { return }

        var originValue: CFTypeRef?
        guard AXUIElementCopyAttributeValue(axWindow, kAXPositionAttribute as CFString, &originValue) == .success,
              let origin = unsafeBitCast(originValue, to: AXValue?.self)
        else { return }
        var point = CGPoint.zero
        guard AXValueGetValue(origin, .cgPoint, &point) else { return }

        // Check it's actually settable before starting the animation —
        // some windows refuse silently and we don't want 8 failed writes.
        let probe = AXValueCreate(.cgPoint, &point)
        guard AXUIElementSetAttributeValue(axWindow, kAXPositionAttribute as CFString, probe) == .success else { return }

        // Slide: 8 steps of dx/8 over ~0.2s (60Hz-friendly).
        let steps = 8
        let stepDX = dx / CGFloat(steps)
        for step in 1...steps {
            DispatchQueue.main.asyncAfter(deadline: .now() + Double(step) * 0.025) {
                point.x += stepDX
                let value = AXValueCreate(.cgPoint, &point)
                AXUIElementSetAttributeValue(axWindow, kAXPositionAttribute as CFString, value)
            }
        }
    }

    /// Map a CGWindowID to its AXUIElement by scanning the app's windows.
    private static func AXWindowIDToAXWindow(_ id: CGWindowID) -> AXUIElement? {
        // Find the owning app via CGWindowList, then its AX windows.
        let options: CGWindowListOption = [.optionOnScreenOnly]
        guard let infoList = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] else {
            return nil
        }
        guard let info = infoList.first(where: { ($0[kCGWindowNumber as String] as? Int) == id }),
              let pid = info[kCGWindowOwnerPID as String] as? Int
        else { return nil }

        let app = AXUIElementCreateApplication(pid)
        var windowsValue: CFTypeRef?
        guard AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &windowsValue) == .success,
              let axWindows = windowsValue as? [AXUIElement]
        else { return nil }

        // Match by frame: the AX window whose frame equals the CG frame.
        guard let cgFrame = info[kCGWindowBounds as String] as? [String: Any],
              let x = cgFrame["X"] as? CGFloat, let y = cgFrame["Y"] as? CGFloat,
              let w = cgFrame["Width"] as? CGFloat, let h = cgFrame["Height"] as? CGFloat
        else { return nil }
        let targetRect = CGRect(x: x, y: y, width: w, height: h)

        for axWindow in axWindows {
            var frameValue: CFTypeRef?
            if AXUIElementCopyAttributeValue(axWindow, kAXPositionAttribute as CFString, &frameValue) == .success,
               let frame = frameValue as? AXValue {
                var pos = CGPoint.zero
                if AXValueGetValue(frame, .cgPoint, &pos) {
                    // CG coordinates (top-left) vs AX (bottom-left): compare
                    // sizes instead — matching windows of the same app by
                    // size is unambiguous enough here.
                    var sizeValue: CFTypeRef?
                    if AXUIElementCopyAttributeValue(axWindow, kAXSizeAttribute as CFString, &sizeValue) == .success,
                       let size = sizeValue as? AXValue {
                        var sz = CGSize.zero
                        if AXValueGetValue(size, .cgSize, &sz), sz.width == w, sz.height == h {
                            return axWindow
                        }
                    }
                }
            }
        }
        return nil
    }
}
