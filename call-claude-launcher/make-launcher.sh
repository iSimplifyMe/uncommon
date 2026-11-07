#!/bin/zsh
# Builds "Call Claude.app": a permission-free launcher that opens claude-call.command in Terminal.
set -e
APP="$HOME/Applications/Call Claude.app"; DATA="$HOME/.local/share/call-claude"; HERE="${0:A:h}"
mkdir -p "$DATA" "$APP/Contents/MacOS" "$APP/Contents/Resources" "$HOME/Applications"
cp "$HERE/claude-call.command" "$DATA/claude-call.command"; chmod +x "$DATA/claude-call.command"
[[ -n "$CLAUDE_FLAGS" ]] && sed -i '' "s|^: \"\${CLAUDE_FLAGS:=.*}\"|: \"\${CLAUDE_FLAGS:=$CLAUDE_FLAGS}\"|" "$DATA/claude-call.command"
VER=$(( $(/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' "$APP/Contents/Info.plist" 2>/dev/null || echo 0) + 1 ))
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>Call Claude</string>
<key>CFBundleDisplayName</key><string>Call Claude</string>
<key>CFBundleIdentifier</key><string>local.call-claude</string>
<key>CFBundleVersion</key><string>$VER</string>
<key>CFBundleShortVersionString</key><string>1.$VER</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>launcher</string>
<key>CFBundleIconFile</key><string>AppIcon</string>
<key>LSUIElement</key><true/>
</dict></plist>
PLIST
cat > "$APP/Contents/MacOS/launcher" <<LAUNCH
#!/bin/zsh
exec /usr/bin/open -a Terminal "$DATA/claude-call.command"
LAUNCH
chmod +x "$APP/Contents/MacOS/launcher"
# Optional icon: drop an AppIcon.icns next to this script to use it.
[[ -f "$HERE/AppIcon.icns" ]] && cp "$HERE/AppIcon.icns" "$APP/Contents/Resources/AppIcon.icns"
codesign -s - --force "$APP" >/dev/null 2>&1 || true
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP"
rm -f "$(getconf DARWIN_USER_CACHE_DIR)com.apple.dock.iconcache"; touch "$APP"; killall Dock 2>/dev/null || true
echo "built: $APP (version $VER). Spotlight: Call Claude. Dock: drag it from ~/Applications."
