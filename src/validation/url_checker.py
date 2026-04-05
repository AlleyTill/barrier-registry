"""Level 1 validation: Check if all source URLs in the database are reachable."""

import httpx
import time
from src.database.models import HealthPolicy, get_session, init_db


def check_urls(sample_size: int = None, timeout: int = 15):
    """Check all (or sampled) policy source URLs for reachability."""
    init_db()
    session = get_session()

    query = session.query(HealthPolicy).filter(HealthPolicy.source_url.isnot(None))
    if sample_size:
        policies = query.limit(sample_size).all()
    else:
        policies = query.all()

    total = len(policies)
    print(f"Checking {total} URLs...\n")

    results = {"ok": [], "redirect": [], "dead": [], "error": [], "no_url": []}

    for i, policy in enumerate(policies):
        url = policy.source_url
        if not url or url.strip() == "":
            results["no_url"].append(policy)
            continue

        try:
            response = httpx.head(url, timeout=timeout, follow_redirects=True)
            status = response.status_code

            if status == 200:
                results["ok"].append((policy, status))
            elif 300 <= status < 400:
                results["redirect"].append((policy, status, str(response.headers.get("location", "unknown"))))
            elif status == 403:
                # Many gov sites block HEAD requests but work fine with GET
                results["ok"].append((policy, "403-head-blocked"))
            elif status == 405:
                # Method not allowed for HEAD, try GET
                response2 = httpx.get(url, timeout=timeout, follow_redirects=True)
                if response2.status_code == 200:
                    results["ok"].append((policy, "200-via-get"))
                else:
                    results["dead"].append((policy, response2.status_code))
            else:
                results["dead"].append((policy, status))

        except httpx.TimeoutException:
            results["error"].append((policy, "TIMEOUT"))
        except httpx.ConnectError:
            results["error"].append((policy, "CONNECT_ERROR"))
        except Exception as e:
            results["error"].append((policy, str(e)[:80]))

        # Progress indicator
        if (i + 1) % 20 == 0 or (i + 1) == total:
            print(f"  [{i+1}/{total}] OK:{len(results['ok'])} Dead:{len(results['dead'])} Error:{len(results['error'])}")

        # Be polite to servers
        time.sleep(0.3)

    session.close()

    # Report
    print(f"\n{'='*60}")
    print(f"URL VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Total checked:  {total}")
    print(f"OK (200):       {len(results['ok'])}")
    print(f"Redirects:      {len(results['redirect'])}")
    print(f"Dead:           {len(results['dead'])}")
    print(f"Errors:         {len(results['error'])}")
    print(f"No URL:         {len(results['no_url'])}")

    if results["dead"]:
        print(f"\n--- DEAD URLs ---")
        for policy, status in results["dead"]:
            print(f"  [{status}] {policy.country} | {policy.title[:60]} | {policy.source_url[:80]}")

    if results["error"]:
        print(f"\n--- ERRORS ---")
        for policy, err in results["error"]:
            print(f"  [{err}] {policy.country} | {policy.title[:60]} | {policy.source_url[:80]}")

    return results


if __name__ == "__main__":
    check_urls()
