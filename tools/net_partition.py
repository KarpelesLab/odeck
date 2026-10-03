"""Partition the still-unrouted nets of a board by placement region (docs/floorplan.md / layout scripts' REGION).
usage (KiCad python): net_partition.py <board.kicad_pcb> <layout_dir> <out.json>
A net is 'local' to a region if all its pads lie in that region's rectangles; otherwise 'interblock'."""
import sys, os, glob, json, importlib.util, collections
import pcbnew

MM = pcbnew.ToMM
board = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
board.BuildConnectivity()
conn = board.GetConnectivity()
regions = {}
for p in sorted(glob.glob(os.path.join(sys.argv[2], "*.py"))):
    n = os.path.splitext(os.path.basename(p))[0]
    if n.startswith(("_", "zz")):
        continue
    spec = importlib.util.spec_from_file_location("l_" + n, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    regions[n] = m.REGION

def region_of(x, y):
    for n, rects in regions.items():
        for x0, y0, x1, y1 in rects:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return n
    return "?"

unrouted = collections.defaultdict(int)
for net, ni in board.GetNetsByName().items():
    code = ni.GetNetCode()
    if code <= 0:
        continue
    c = conn.GetUnconnectedCount  # noqa
cnt = collections.Counter()
nets_pads = collections.defaultdict(list)
for fp in board.GetFootprints():
    for p in fp.Pads():
        if p.GetNetCode() > 0:
            nets_pads[p.GetNetname()].append((fp.GetReference(), p.GetNumber(), MM(p.GetPosition().x), MM(p.GetPosition().y)))
pad_objs = collections.defaultdict(list)
for fp in board.GetFootprints():
    for p in fp.Pads():
        if p.GetNetCode() > 0:
            pad_objs[p.GetNetname()].append(p)

def components(net):
    pads = pad_objs[net]
    key = lambda p: (p.GetParentFootprint().GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y)
    seen, comps = set(), 0
    for p in pads:
        if key(p) in seen:
            continue
        comps += 1
        stack = [p]
        while stack:
            q = stack.pop()
            if key(q) in seen:
                continue
            seen.add(key(q))
            for r in conn.GetConnectedItems(q):
                if r.GetClass() == "PAD" and r.GetNetname() == net and key(r) not in seen:
                    seen.add(key(r))
    return comps

out = {"local": collections.defaultdict(list), "interblock": [], "counts": {}}
for net, pads in nets_pads.items():
    ni = board.FindNet(net)
    # count unconnected pads of this net (ratsnest edges)
    n_unc = components(net) - 1
    if n_unc == 0:
        continue
    regs = {region_of(x, y) for _, _, x, y in pads}
    short = net.split("/")[-1] if net.count("/") >= 2 else net
    if len(regs) == 1 and "?" not in regs:
        out["local"][regs.pop()].append({"net": net, "pads": len(pads), "unrouted": n_unc})
    else:
        out["interblock"].append({"net": net, "regions": sorted(regs), "pads": len(pads), "unrouted": n_unc})
for r, l in out["local"].items():
    out["counts"][r] = {"nets": len(l), "edges": sum(x["unrouted"] for x in l)}
out["counts"]["interblock"] = {"nets": len(out["interblock"]), "edges": sum(x["unrouted"] for x in out["interblock"])}
json.dump(out, open(sys.argv[3], "w"), indent=1)
print(json.dumps(out["counts"], indent=1))
