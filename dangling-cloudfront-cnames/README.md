# Dangling CloudFront CNAMEs behind a Cloudflare proxy

You tear down a staging stack. The CloudFront distribution goes away. The `staging.example.com` CNAME that pointed at `d1234abcd.cloudfront.net` stays in Cloudflare, because nothing ever deletes DNS. Months later the name still resolves and still answers, so no uptime check and no "look for NXDOMAIN" script ever flags it.

Two things hide it:

1. **Cloudflare's proxy answers for the name.** An orange-cloud record returns Cloudflare's own IPs and an HTTP response, a `530` (origin unreachable), not a DNS failure. Every dangling-record scanner that keys on NXDOMAIN reads it as healthy.
2. **The target lives in another account.** Your CloudFront list from one AWS profile does not know about distributions in the client's account or the staging account, so "is this domain ours" needs the union of every profile you can read.

## The method

Join two lists:

- every DNS record in every Cloudflare zone your token can see, keeping the CNAMEs whose target ends in `.cloudfront.net`;
- every CloudFront distribution's domain name from every AWS profile you can read.

A CloudFront target that is in the first list and not the second is either dangling or in an account you cannot read. One HTTPS request settles it: a live distribution answers for its alias; a deleted one gives you `530` through the proxy or CloudFront's own `403 Bad request` without it.

```sh
export CLOUDFLARE_API_TOKEN=...            # Zone:Read + DNS:Read on the zones to check
python3 find_dangling.py --profiles default,staging,client-a
```

Output is one line per candidate with the hostname, the target, and the probe's status code. Delete the record (save it first) or re-point it.

## Why it matters

A proxied dangling record is mostly hygiene: a dead host that looks alive, and a distribution alias that could be claimed if the account that owned it is no longer yours. An unproxied one is the classic subdomain-takeover shape. Either way, the fleet scan should run this join, not a resolver check.

Found four of them in one pass across 167 zones and 148 distributions.
