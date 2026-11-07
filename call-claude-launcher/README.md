# Call Claude: a one-click macOS launcher for a terminal AI session

You run an AI coding agent in Terminal all day. You want a Dock icon, a Spotlight entry and a hotkey that opens a fresh session with your exact flags, the way you type them. This folder builds that app in about two seconds.

## The trap

The obvious build is an AppleScript app (`osacompile`) that tells Terminal to run your command. It works when you double-click it after approving the "wants to control Terminal" dialog. It does nothing, with no error anywhere, when it is launched by anything that cannot show that dialog: a script, a scheduler, a hotkey tool, or the first run before the dialog has ever appeared. The Apple event is refused by TCC (Transparency, Consent and Control) and the app quits clean.

The fix is to send no Apple events at all. Terminal opens any `.command` file as a new window and runs it. So the app is a plain shell bundle whose only job is:

```sh
open -a Terminal "$HOME/.local/share/call-claude/claude-call.command"
```

No permission prompt, works from anywhere.

## Build

```sh
./make-launcher.sh                 # builds ~/Applications/Call Claude.app
CLAUDE_FLAGS="--model claude-opus-5-5" ./make-launcher.sh   # your flags
```

`claude-call.command` is the session itself. Edit the flags there, or set `CLAUDE_FLAGS` before building. It wraps the session in `caffeinate -i` so the Mac does not sleep mid-task.

Then: Spotlight "Call Claude", or drag the app from `~/Applications` to the Dock. For a hotkey: Shortcuts app, new shortcut, action "Open App", pick Call Claude, open its details, "Add Keyboard Shortcut".

## Two smaller traps

- **The Dock keeps the old icon** after you change it. Remove `$(getconf DARWIN_USER_CACHE_DIR)com.apple.dock.iconcache`, bump `CFBundleVersion`, re-register with `lsregister -f`, then `killall Dock`. The script does all four.
- **Icons that are not in Apple's new icon format** render inside a dark rounded frame on recent macOS. Harmless; the badge still reads at Dock size.

Tested on macOS 27.2 with Claude Code; nothing here is specific to that agent except the default command.
