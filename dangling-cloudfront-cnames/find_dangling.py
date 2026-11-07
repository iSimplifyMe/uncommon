#!/usr/bin/env python3
"""Find CNAMEs in your Cloudflare zones that point at CloudFront distributions none of your AWS profiles own.
Needs: CLOUDFLARE_API_TOKEN in the environment (Zone:Read, DNS:Read), the aws CLI configured for each profile.
Usage: python3 find_dangling.py --profiles default,staging [--no-probe]"""
import argparse, json, os, subprocess, sys, urllib.request, urllib.error, concurrent.futures as cf

def cf_get(path):
    tok = os.environ.get("CLOUDFLARE_API_TOKEN") or sys.exit("CLOUDFLARE_API_TOKEN not set")
    req = urllib.request.Request("https://api.cloudflare.com/client/v4" + path, headers={"Authorization": f"Bearer {tok}"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def cf_paged(path):
    page, out = 1, []
    while True:
        d = cf_get(f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
        out += d["result"]
        if page >= d["result_info"]["total_pages"]: return out
        page += 1

def aws_distribution_domains(profile):
    p = subprocess.run(["aws", "--profile", profile, "--output", "json", "cloudfront", "list-distributions",
                        "--query", "DistributionList.Items[].DomainName"], capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        print(f"# profile {profile}: {p.stderr.strip()[:120]}", file=sys.stderr); return set()
    return {d.lower() for d in (json.loads(p.stdout) or [])}

def probe(host):
    try:
        with urllib.request.urlopen(urllib.request.Request(f"https://{host}/", headers={"User-Agent": "find-dangling/1.0"}), timeout=12) as r:
            return r.status
    except urllib.error.HTTPError as e: return e.code
    except Exception as e: return type(e).__name__

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--profiles", default="default"); ap.add_argument("--no-probe", action="store_true")
    a = ap.parse_args()
    ours = set()
    for prof in a.profiles.split(","): ours |= aws_distribution_domains(prof.strip())
    print(f"# {len(ours)} CloudFront distributions across profiles {a.profiles}", file=sys.stderr)
    zones = cf_paged("/zones?")
    print(f"# {len(zones)} Cloudflare zones", file=sys.stderr)
    def sweep(z):
        recs = cf_paged(f"/zones/{z['id']}/dns_records?type=CNAME")
        return [(r["name"], r["content"].lower(), r["proxied"]) for r in recs if r["content"].lower().endswith(".cloudfront.net")]
    cands = []
    with cf.ThreadPoolExecutor(8) as ex:
        for rows in ex.map(sweep, zones):
            cands += [(n, t, p) for n, t, p in rows if t not in ours]
    if not cands: print("no CloudFront CNAMEs outside your profiles"); return
    with cf.ThreadPoolExecutor(16) as ex:
        codes = ["-"] * len(cands) if a.no_probe else list(ex.map(lambda c: probe(c[0]), cands))
    for (name, target, proxied), code in zip(cands, codes):
        verdict = "DANGLING" if code in (530, 403, "URLError") else "check: other account?"
        print(f"{name}\t{target}\tproxied={proxied}\thttp={code}\t{verdict}")

if __name__ == "__main__": main()
