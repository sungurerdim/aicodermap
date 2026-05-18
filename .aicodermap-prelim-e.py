import json, os, sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path("scripts").resolve()))
from lib.matrix import active_models, matrix_snapshot, priority_cells
from lib.whitelist import contracts as wl_contracts, load_whitelist as wl_load

models = json.loads(Path("data/models.json").read_text(encoding="utf-8"))
wl = wl_load(Path("data/sources-whitelist.json"))
ctr = wl_contracts(wl)
core_keys = wl.get("_schema", {}).get("coreBenchKeys", [])

active = active_models(models)
ms_list = models.get("models", []) if isinstance(models, dict) else models
print("total models:", len(ms_list))
print("active models:", len(active))
print("core bench keys:", len(core_keys))

vm_path = Path(".aicodermap-verification-map.json")
vm = json.loads(vm_path.read_text(encoding="utf-8")) if vm_path.exists() else {}
print("verification map cells:", len(vm.get("cells", {})))

ms = matrix_snapshot(active, core_keys)
print(
    "MATRIX: total={} filled={} na={} expected={} fill={:.3f}".format(
        ms["totalCells"],
        ms["filledCells"],
        ms["notApplicableCells"],
        ms["expectedTotal"],
        ms["fillRatio"],
    )
)

ttl_days = ctr.get("FRESHNESS_TTL_DAYS", 7)
stale_days = ctr.get("STALE_DAYS", 14)
print("FRESHNESS_TTL_DAYS={} STALE_DAYS={}".format(ttl_days, stale_days))

pc = priority_cells(
    active,
    core_keys,
    limit=200,
    verification_map=vm,
    skip_confirmed_within_days=ttl_days,
)
print("priorityCells:", len(pc))
for c in pc[:10]:
    print("  - {}.{}".format(c["modelId"], c["benchKey"]))

today = datetime.now(timezone.utc).date()
thr = stale_days - 7
fresh = 0
stale = []
for m in active:
    lu = m.get("lastUpdated", "")
    if not lu:
        stale.append((m["id"], "no-lastUpdated"))
        continue
    try:
        d = datetime.fromisoformat(lu.replace("Z", "+00:00")).date()
        age = (today - d).days
        if age <= thr:
            fresh += 1
        else:
            stale.append((m["id"], "{}d".format(age)))
    except Exception as e:
        stale.append((m["id"], "err:{}".format(e)))

print(
    "freshness threshold <= {}d: fresh={}/{} stale={}".format(
        thr, fresh, len(active), len(stale)
    )
)
for sm in stale[:15]:
    print("  - {} {}".format(sm[0], sm[1]))

all_fresh = len(stale) == 0
no_priority = len(pc) == 0
force = os.environ.get("AICODERMAP_FULL_REFRESH") == "1"
gate = all_fresh and no_priority and not force
print(
    "GATE: priorityEmpty={} allFresh={} force={} -> trigger={}".format(
        no_priority, all_fresh, force, gate
    )
)
