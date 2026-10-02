"""odeck-10 copper zones: GND planes (L2/L5), L4 power islands (+ GND fill), L1/L6 GND pours, keep-outs, GND
stitching vias and edge via fence. Power-net pours on L1/L6 (and the L3 helper pours) live in b_power.py.

Layer use (JLC061611-1080A): L1 F.Cu sig/power, L2 In1.Cu GND, L3 In2.Cu sig, L4 In3.Cu power, L5 In4.Cu GND,
L6 B.Cu sig/power. See docs/routing-notes/power.md for the island map and its reasoning.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _pwrlib as L  # noqa: E402

NETS = ["GND"]   # stitching / fence vias (drawn first; HS scripts add their own GND return vias afterwards)

# ---------------------------------------------------------------- L4 (In3.Cu) power islands
# (name, net, polygon). Islands do not overlap; whatever is left on L4 is filled with GND (L4_GND, prio 0).
L4_ISLANDS = [
    ("L4_VBAR", "VBAR", [(100.5, 50.5), (118.8, 50.5), (118.8, 64.0), (103.4, 64.0), (103.4, 69.6),
                         (100.5, 69.6)]),
    ("L4_VBUS_PDIN", "VBUS_PDIN", L.rect(119.4, 50.5, 133.0, 63.6)),
    ("L4_BB_PSO", "BB_PSO", [(100.5, 70.4), (114.2, 70.4), (114.2, 74.3), (109.0, 74.3), (109.0, 78.4),
                             (100.5, 78.4)]),
    ("L4_VIN", "VIN", [(109.3, 74.6), (115.9, 74.6), (115.9, 88.0), (138.0, 88.0), (138.0, 95.0), (142.9, 95.0),
                       (142.9, 99.3), (151.6, 99.3), (151.6, 107.7), (100.5, 107.7), (100.5, 88.0),
                       (111.4, 88.0), (111.4, 78.7), (109.3, 78.7)]),
    ("L4_VBB_OUT", "VBB_OUT", [(116.3, 71.8), (121.3, 71.8), (121.3, 74.8), (131.0, 74.8), (131.0, 87.6),
                               (116.3, 87.6)]),
    ("L4_SRC_MID", "SRC_MID", L.rect(121.7, 66.4, 132.8, 74.4)),
    ("L4_VBUS_LAPTOP", "VBUS_LAPTOP", [(133.4, 50.5), (154.0, 50.5), (154.0, 66.2), (138.6, 66.2),
                                       (138.6, 70.4), (133.4, 70.4)]),
    ("L4_5V_BUCK", "5V_BUCK", L.rect(138.5, 80.4, 151.5, 90.3)),
    ("L4_P5V", "+5V", [(131.4, 76.0), (156.2, 76.0), (156.2, 86.0), (168.6, 86.0), (168.6, 76.4), (172.4, 76.4),
                       (172.4, 86.0), (174.2, 86.0), (174.2, 90.4), (164.4, 90.4), (164.4, 105.7),
                       (180.0, 105.7), (180.0, 119.6), (198.0, 119.6), (198.0, 138.5), (100.5, 138.5),
                       (100.5, 108.0), (151.9, 108.0), (151.9, 80.4), (131.4, 80.4)]),
    ("L4_P3V3", "+3V3", [(154.4, 50.5), (183.3, 50.5), (183.3, 72.0), (222.0, 72.0), (222.0, 58.6),
                         (229.5, 58.6), (229.5, 138.5), (198.4, 138.5), (198.4, 119.3), (180.3, 119.3),
                         (180.3, 56.4), (166.5, 56.4), (166.5, 75.9), (168.3, 75.9), (168.3, 85.8),
                         (156.5, 85.8), (156.5, 75.7), (154.4, 75.7)]),
    ("L4_VBUS_DS", "VBUS_DS", [(166.8, 56.8), (179.7, 56.8), (179.7, 80.3), (172.9, 80.3), (172.9, 75.6),
                               (166.8, 75.6)]),
    ("L4_P1V15", "+1V15", [(164.6, 90.8), (174.5, 90.8), (174.5, 80.6), (179.7, 80.6), (179.7, 105.4),
                           (164.6, 105.4)]),
    ("L4_ETH_3V3", "ETH_3V3", [(183.6, 50.5), (202.0, 50.5), (202.0, 59.3), (192.4, 59.3), (192.4, 64.0),
                               (183.6, 64.0)]),
    ("L4_ETH_0V95", "ETH_0V95", [(192.7, 59.6), (201.8, 59.6), (201.8, 71.6), (183.6, 71.6), (183.6, 64.3),
                                 (192.7, 64.3)]),
]

# ---------------------------------------------------------------- keep-outs (rule areas)
# Switch nodes: nothing on L3/L4 under the SW copper (tracks, vias, pours); no pour on L6 (tracks allowed).
SW_KO = [
    ("KO_BB_SW1_R201", L.rect(100.7, 92.9, 102.4, 96.6)),
    ("KO_BB_SW1_FET", [(100.7, 96.95), (112.0, 96.95), (112.0, 98.4), (106.0, 98.4), (106.0, 101.9),
                       (100.7, 101.9)]),
    ("KO_BB_LS", [(101.6, 89.5), (111.0, 89.5), (111.0, 92.35), (108.3, 92.35), (108.3, 96.6), (106.65, 96.6),
                  (106.65, 92.35), (101.6, 92.35)]),
    ("KO_BB_SW2", [(101.6, 82.85), (104.6, 82.85), (104.6, 81.3), (106.6, 81.3), (106.6, 82.85),
                   (108.6, 82.85), (108.6, 79.5), (111.4, 79.5), (111.4, 85.7), (101.6, 85.7)]),
    ("KO_5V_SW_L301", L.rect(142.3, 91.75, 148.2, 95.4)),
    ("KO_5V_SW_Q302", L.rect(145.5, 95.9, 150.3, 100.75)),
    ("KO_5V_SW_Q301", L.rect(143.25, 97.25, 144.65, 99.25)),
]
# Small-buck switch nodes / RP2350 VREG_LX: no L3 signal under them.
L3_KO = [
    ("KO_3V3_SW", L.rect(165.0, 81.8, 167.4, 87.7)),
    ("KO_1V15_SW", L.rect(175.8, 84.1, 178.1, 88.1)),
    ("KO_ETH_SW", L.rect(186.9, 64.8, 190.8, 68.9)),
    ("KO_VREG_LX", L.rect(226.7, 70.3, 228.1, 72.4)),
]
# RJ45 magjack: no pours on L1/L4/L6 under the cable-side half of the jack (shell is GND, L2/L5 stay solid).
RJ45_KO = L.rect(202.3, 50.5, 221.7, 60.0)

# AC-coupling caps on SS/DP lanes: void the adjacent GND plane under their pads (top caps -> L2, bottom -> L5).
AC_CAPS = (["C%d" % n for n in range(601, 613)] + ["C%d" % n for n in range(509, 523)] +
           ["C530", "C531", "C532", "C533", "C534", "C535", "C917", "C918", "C835", "C836"])

# ---------------------------------------------------------------- stitching exclusions
# High-speed corridors / channels named in the layout notes (the HS scripts place their own fences there),
# the usbc block interior, the FPC tail area, and the power pours of b_power.py.
STITCH_EXCLUDE = [
    L.rect(138.0, 50.0, 180.5, 80.5),      # usbc block (dense; fences belong to the usbc routing)
    L.rect(159.0, 80.0, 164.8, 112.5),     # hub SS escape + P1/P2 channel
    L.rect(166.8, 78.0, 174.5, 92.0),      # UP/P5 corridor
    L.rect(165.5, 103.5, 181.0, 108.6),    # P3 / P4 run
    L.rect(136.8, 107.8, 165.0, 112.6),    # CR SS + hub->front hand-off band
    L.rect(136.8, 107.8, 142.0, 121.0),    # CR SS escape
    L.rect(149.0, 104.0, 154.0, 124.5),    # USB-A port 1 channel
    L.rect(168.0, 104.0, 173.0, 124.5),    # USB-A port 2 channel
    L.rect(107.0, 103.5, 138.5, 129.5),    # card reader: SD bus fan-out, microSD escape, CR USB2 on B.Cu
    L.rect(177.5, 64.0, 183.5, 109.0),     # Ethernet USB pairs along the x = 180 block boundary
    L.rect(126.5, 128.6, 182.0, 133.4),    # microSD band
    L.rect(127.5, 114.5, 135.0, 133.4),    # microSD escape from U901
    L.rect(178.5, 119.5, 193.0, 133.4),    # microSD rise + J902 row
    L.rect(180.0, 58.5, 194.0, 65.5),      # Ethernet USB corridor
    L.rect(198.5, 63.5, 220.0, 73.0),      # MDI bundle
    L.rect(193.5, 69.0, 202.5, 92.0),      # LCD FPC tail / J1103
    L.rect(100.0, 62.0, 116.5, 108.5),     # LM51770 column + input FETs (own via arrays in b_power)
    L.rect(138.0, 78.0, 158.5, 108.5),     # LM5148 stage (own via arrays in b_power)
]


# Every zone / rule area this script creates (same-named zones are replaced on each run).
ZONES = (["GND_L2", "GND_L5", "L4_GND", "GND_L1", "GND_L6"] + [z[0] for z in L4_ISLANDS] +
         ["KO_HOLE_%d" % i for i in range(1, 5)] + [n for n, _p in SW_KO] +
         [n + "_L6" for n, _p in SW_KO if n.startswith("KO_BB")] + [n for n, _p in L3_KO] + ["KO_RJ45"] +
         ["VOID_%s_%s" % (c, p) for c in AC_CAPS for p in ("1", "2")])


def route(board, r):
    # --- GND planes L2 / L5 (whole board)
    L.add_zone(board, r, "GND_L2", "GND", "In1.Cu", L.board_poly(), priority=0)
    L.add_zone(board, r, "GND_L5", "GND", "In4.Cu", L.board_poly(), priority=0)
    # --- L4: power islands + GND fill of the rest
    L.add_zone(board, r, "L4_GND", "GND", "In3.Cu", L.board_poly(), priority=0)
    for name, net, poly in L4_ISLANDS:
        L.add_zone(board, r, name, net, "In3.Cu", poly, priority=5)
    # --- L1 / L6 GND pours (lowest priority; power pours in b_power.py sit above them)
    L.add_zone(board, r, "GND_L1", "GND", "F.Cu", L.board_poly(), priority=0)
    L.add_zone(board, r, "GND_L6", "GND", "B.Cu", L.board_poly(), priority=0)

    # --- keep-outs
    for i, (hx, hy) in enumerate(L.HOLES):
        L.add_keepout(board, "KO_HOLE_%d" % (i + 1), L.ALL_CU, L.circle(hx, hy, 4.0))
    for name, poly in SW_KO:
        # Q302 SW EP keeps its thermal vias down to the bottom SW pour (layout notes), so vias stay allowed there
        L.add_keepout(board, name, ["In2.Cu", "In3.Cu"], poly, vias=(name != "KO_5V_SW_Q302"))
        if name.startswith("KO_BB"):
            L.add_keepout(board, name + "_L6", ["B.Cu"], poly, tracks=False, vias=False, pours=True)
    for name, poly in L3_KO:
        L.add_keepout(board, name, ["In2.Cu"], poly, tracks=True, vias=True, pours=True)
    L.add_keepout(board, "KO_RJ45", ["F.Cu", "In3.Cu", "B.Cu"], RJ45_KO, tracks=False, vias=False, pours=True)
    for ref in AC_CAPS:
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        layer = "In4.Cu" if fp.IsFlipped() else "In1.Cu"
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            x0, y0, x1, y1 = (L.MM(bb.GetLeft()), L.MM(bb.GetTop()), L.MM(bb.GetRight()), L.MM(bb.GetBottom()))
            L.add_keepout(board, "VOID_%s_%s" % (ref, p.GetNumber()), [layer], L.rect(x0, y0, x1, y1),
                          tracks=False, vias=False, pours=True)

    # --- GND stitching grid (4 mm) + edge fence (2.5 mm pitch, 1.4 mm in from the edge)
    import b_power
    excl = STITCH_EXCLUDE + [poly for (_n, _net, _l, poly, _p) in b_power.POURS] + \
        [poly for _n, poly in SW_KO] + [poly for _n, poly in L3_KO]
    # no stitching via inside a part's courtyard (big parts that are fine to stitch under are exempt)
    for fp in board.GetFootprints():
        if fp.GetReference() in ("U1101", "J901", "J701", "J702", "J801") or fp.GetReference().startswith("H"):
            continue
        cy = fp.GetCourtyard(L.pcbnew.B_CrtYd if fp.IsFlipped() else L.pcbnew.F_CrtYd)
        if cy.OutlineCount():
            bb = cy.BBox()
            excl.append(L.rect(L.MM(bb.GetLeft()), L.MM(bb.GetTop()), L.MM(bb.GetRight()), L.MM(bb.GetBottom())))
    vp = L.ViaPlacer(board, keepouts=excl)
    n_grid = vp.grid(r, "GND", L.rect(101.0, 51.0, 229.0, 138.0), 4.0, size=0.45, drill=0.25)
    fence = L.ViaPlacer(board, keepouts=STITCH_EXCLUDE[:1] + [poly for (_n, _net, _l, poly, _p) in b_power.POURS])
    n_f = 0
    e = 1.4
    for (ax, ay, bx, by) in ((100 + e, 50 + e, 230 - e, 50 + e), (230 - e, 50 + e, 230 - e, 139 - e),
                             (230 - e, 139 - e, 100 + e, 139 - e), (100 + e, 139 - e, 100 + e, 50 + e)):
        import math
        n = int(math.hypot(bx - ax, by - ay) / 2.5)
        for k in range(n + 1):
            x, y = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
            for d in (0.0, 0.5, -0.5, 1.0, -1.0):
                dx, dy = (d, 0) if ay == by else (0, d)
                if fence.place(r, "GND", x + dx, y + dy, 0.45, 0.25):
                    n_f += 1
                    break
    print("a_planes: %d stitching vias, %d fence vias" % (n_grid, n_f))
