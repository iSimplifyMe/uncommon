# uncommon

Things we hit while running a fleet of about ninety repos, a hundred and fifty hostnames, two WordPress hosts and a handful of AWS and Cloudflare accounts with one operator and an AI chief of staff. Each folder is one thing: what broke or what was missing, why the usual advice did not cover it, and the fix with the code we actually ran.

If something isn't common, it's probably because it just hasn't been common yet.

| Folder | What it gives you |
|---|---|
| [`call-claude-launcher/`](call-claude-launcher/) | A one-click macOS launcher for a terminal AI session, with a Dock icon, and the macOS automation-permission trap that silently breaks the obvious AppleScript version. |
| [`dangling-cloudfront-cnames/`](dangling-cloudfront-cnames/) | Find DNS records that still point at CloudFront distributions you deleted, even when a Cloudflare proxy hides the usual NXDOMAIN signal. |

MIT licensed. Maintained by [iSimplifyMe](https://isimplifyme.com). Issues and pull requests welcome; so is "this is wrong, here is why."
