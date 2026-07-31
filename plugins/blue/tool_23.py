import json
import subprocess
from pathlib import Path

NAME = "Network Baseline Comparator"
DESCRIPTION = "Snapshot network config, compare against previous baseline."
ALLOWED_ROLES = ["admin", "instructor", "student"]

BASELINE_DB = Path("database/net_baseline.json")


def run(username, role):
    current = _get_network_state()
    print(f"[*] Captured current network state ({len(current['ips'])} IPs, "
          f"{len(current['routes'])} routes, {len(current['listeners'])} listeners)")

    if BASELINE_DB.exists():
        baseline = json.loads(BASELINE_DB.read_text(encoding="utf-8"))
        print("\n--- Changes vs baseline ---")
        diffs = 0

        for iface, ips in current["ips"].items():
            old_ips = baseline.get("ips", {}).get(iface, [])
            new_ips = set(ips) - set(old_ips)
            removed_ips = set(old_ips) - set(ips)
            for ip in new_ips:
                print(f"  [+] IP {ip} added to {iface}")
                diffs += 1
            for ip in removed_ips:
                print(f"  [-] IP {ip} removed from {iface}")
                diffs += 1

        old_routes = set(baseline.get("routes", []))
        new_routes = set(current["routes"])
        for r in new_routes - old_routes:
            print(f"  [+] New route: {r}")
            diffs += 1
        for r in old_routes - new_routes:
            print(f"  [-] Route gone: {r}")
            diffs += 1

        old_listeners = set(baseline.get("listeners", []))
        new_listeners = set(current["listeners"])
        for l in new_listeners - old_listeners:
            print(f"  [!] NEW LISTENER: {l}")
            diffs += 1
        for l in old_listeners - new_listeners:
            print(f"  [-] Listener gone: {l}")
            diffs += 1

        if diffs == 0:
            print("  [+] No network changes detected.")
    else:
        print("[*] No baseline found — this run creates one.")
        print("\nCurrent state:")
        for iface, ips in current["ips"].items():
            print(f"  {iface}: {', '.join(ips) or '(none)'}")
        for r in current["routes"][:10]:
            print(f"  route: {r}")

    BASELINE_DB.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_DB.write_text(json.dumps(current, indent=2), encoding="utf-8")
    print(f"\n[+] Baseline saved: {BASELINE_DB}")


def _get_network_state():
    state = {"ips": {}, "routes": [], "listeners": []}

    # Interface IPs
    result = subprocess.run(["ip", "-o", "addr"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[1] not in ("lo",):
            iface = parts[1]
            ip = parts[3].split("/")[0]
            state["ips"].setdefault(iface, []).append(ip)

    # Routes
    result = subprocess.run(["ip", "route"], capture_output=True, text=True)
    state["routes"] = result.stdout.splitlines()

    # Listening ports (best effort)
    for cmd, args in (("ss", ["-tlnp"]), ("netstat", ["-tlnp"])):
        try:
            result = subprocess.run([cmd] + args, capture_output=True, text=True)
            if result.returncode == 0:
                state["listeners"] = result.stdout.splitlines()[1:]
                break
        except FileNotFoundError:
            continue

    return state
