# odeck-10 routing notes: copper zones and power routing

Scripts: `hardware/odeck-10/routing/a_planes.py` (zones, keep-outs, GND stitching),
`hardware/odeck-10/routing/b_power.py` (power pours, via arrays, gate drives, Kelvin taps, card-reader VCC),
shared helpers in `routing/_pwrlib.py` (skipped by `apply_routing.py`: zone/keep-out helpers, a via placer that
checks every pad, hole, track and via already on the board, and a small A* grid router for the short local nets).
Check: `apply_routing.py <copy> --only a_planes,b_power --drc` gives 0 DRC errors (only unconnected items of other
nets and the small rail/decoupling connections listed at the end).

## 1. Zones (`ZONES` in both scripts)

| Layer | Zones | Priority |
|---|---|---|
| L2 In1.Cu | `GND_L2` whole board (0.5 mm pull-back, 4 mm keep-out around H1–H4) | 0 |
| L5 In4.Cu | `GND_L5` same | 0 |
| L4 In3.Cu | `L4_GND` everywhere + power islands (table below) | 0 / 5 |
| L1 / L6 | `GND_L1`, `GND_L6` whole board (free areas) | 0 |
| L1 / L6 / L3 | power pours `P_*` (b_power.py) | 10 |
| L1 / L6 | switch-node copper `P_BB_SW1`, `P_BB_LS`, `P_BB_SW2`, `P_5V_SW`, `P_5V_SW_L6` | 11 |
| L1 | hot-loop GND copper `P_GND_HOT_*` (buck/boost/LM5148 input caps to FET sources) | 12 |

All zones: 0.3 mm clearance (meets the 0.3 mm HV rule everywhere), solid pad connection, min width 0.25 mm,
islands removed.

L4 island map (power plane, everything else on L4 is GND):

| Island | Area | Feeds |
|---|---|---|
| `L4_VBAR` | x 100.5–118.8, y 50.5–64 (+ strip down to y 69.6 at x < 103.4) | J102 pin 1 (THT) → Q106 sources |
| `L4_VBUS_PDIN` | x 119.4–133, y 50.5–63.6 (+ x 128.6–133 to y 66) | J101 VBUS (THT B4/B9) → D101 / Q104 |
| `L4_BB_PSO` | x 100.5–114.2, y 70.4–74.3 + x 100.5–109, y 74.3–78.4 | boost output caps C205–C208, R202.1 |
| `L4_VIN` | x 109.3–115.9, y 74.6–88 (tab at R137) + x 100.5–138, y 88–107.7 + hubrails x 138–151.6, y 95–107.7 | Q201/C201–C204, U201 VIN, C122, LM5148 Q301/C301–C306 |
| `L4_VBB_OUT` | x 116.3–131, y 74.8–87.6 (+ x 116.3–121.3 from y 71.8) | R202.2, C209–C212, Q213 sources |
| `L4_SRC_MID` | x 121.7–132.8, y 66.4–74.4 | Q213/Q214 drain EPs (thermal) |
| `L4_VBUS_LAPTOP` | x 133.4–154, y 50.5–66.2 + tab x 133.4–138.6 to y 70.4 | R243.2/C233 → D501 → J501 B4/B9 (THT) |
| `L4_5V_BUCK` | x 138.5–151.5, y 80.4–90.3 | copy of the bottom 5V_BUCK pour (C309–C314) |
| `L4_P5V` | sink strip x 131.4–156.2, y 76–80.4; hub centre x 151.9–164.4, y 80.4–108; strip x 164.4–174.2, y 86–90.4; tab x 168.6–172.4, y 76.4–86 (R415); front x 100.5–180, y 108–138.5; J902 corner x 180–198 from y 119.6 | U206 sink output, R312.2 (LM5148 output), U304 VIN, USB-A shunts R704/R709, U901, R415 |
| `L4_P3V3` | usbc x 154.4–166.5, y 50.5–75.7; band over J502 y 50.5–56.4 to x 180.3; strip x 180.3–183.3 down to y 72; right block x 180.3–229.5, y 72–138.5 minus the J902 corner; MCU column x 222–229.5 from y 58.6; hub band x 156.5–168.3, y 75.9–85.8 | L302.2 (+3V3 buck), muxes/PMG1, RP2350, LCD, U802 |
| `L4_VBUS_DS` | x 166.8–179.7, y 56.8–75.6 + x 172.9–179.7 to y 80.3 | Q402 pin 3, J502 VBUS, D505, C536 |
| `L4_P1V15` | under U601 x 164.6–179.7, y 90.8–105.4 + column x 174.5–179.7 from y 80.6 | L303.2 / C338–C341 → hub VCORE caps |
| `L4_ETH_3V3` | x 183.6–202, y 50.5–59.3 + x 183.6–192.4 to y 64 | U802 OUT (via `P_ETH_3V3_U802`) |
| `L4_ETH_0V95` | under the RTL x 192.7–201.8, y 59.6–71.6 + x 183.6–201.8, y 64.3–71.6 | L801.2 (via `P_ETH_0V95_L801`) |

L3 hub/usbc corridors (x 159.5–164 down to y 80, and the P1/P2 channel) sit over solid `L4_P3V3` / `L4_P5V`;
the only split they cross is y ≈ 85.8 (+3V3 → +5V) if they continue on L3 below y 80. Card-reader SS on L3 should run east
along y 108–112 (all `L4_P5V`) before turning north at x ≥ 152, not north at x ≈ 139 (that is `L4_VIN`).

Keep-outs (rule areas): `KO_HOLE_1..4` (r = 4 mm, all layers); switch nodes `KO_BB_SW1_*`, `KO_BB_LS`, `KO_BB_SW2`,
`KO_5V_SW_*` (no tracks/vias/pour on L3/L4 under the SW copper; `_L6` copies forbid L6 pour under the BB nodes;
the Q302 EP keeps its thermal vias); `KO_3V3_SW`, `KO_1V15_SW`, `KO_ETH_SW`, `KO_VREG_LX` (nothing on L3);
`KO_RJ45` (no pour on L1/L4/L6 under the cable-side half of the magjack, x 202.3–221.7, y < 60; L2/L5 stay solid
because the shell is GND per ethernet.md); `VOID_<cap>_<pad>` = L2 (top caps) / L5 (bottom caps) voids under every
SS/DP AC-coupling cap pad (C509–C522, C530–C535, C601–C612, C835/C836, C917/C918).

GND stitching (a_planes, GND in its `NETS`): 4 mm grid (227 vias, 0.45/0.25) outside every courtyard, the usbc
block, the HS corridors/channels named in the layout notes, the two power stages and the power pours; edge fence
1.4 mm from the edge at 2.5 mm pitch (102 vias). b_power adds hot-loop GND via rows (C201/C203/C205–C208/Q202/
Q203/LM5148 input caps, 8–12 per loop).

## 2. Power paths (current sizing: 1 oz, IPC-2152 ≈ 20 °C rise; vias 0.6/0.3 unless noted)

| Path | Copper | Width | Vias (layer changes) |
|---|---|---|---|
| VBAR (≤ 8 A barrel): J102.1 → Q106 sources | L4 island + L6 pour (J102 → between peg and sleeve → y 62–64 → Q106) + L1 at D102 | L6 ≥ 1.45 mm neck, L4 ≥ 8 mm | 5 at D102, 4×0.5/0.25 at Q106 |
| BAR_MID / PD_MID (FET-pair drains) | L6 pours over both EPs | 4.4 mm | none (drain pads under D101/D102, per notes) |
| VBUS_PDIN: J101 → D101 → Q104 | L4 island, A4/A9→B9/B4 links (0.25), L1 D101 pour, L6 Q104/C101 pour | 4 mm | 3 filled via-in-pad D101.1/Q104 1–3 + 1 at C101 |
| VIN_OR → R137.1 | L6 pour | 3.4 mm | – |
| VIN: R137.2 → L4 → Q201, C122, U201, hubrails | L6 pour at R137, L4 `L4_VIN`, L1 pours at Q201/C201–C203, C122, Q301/C301–C305, L6 pours under the buck caps and Q301 | L4 ≥ 3.6 mm tab, then plane | **4** at R137 (see problems), 9 Q201 EP, 6 caps, 4 C122, 8 Q301 EP/drain, 6+4 LM5148 caps |
| BB_SW1 / BB_LS / BB_SW2 / 5V_SW | small L1 shapes only (5V_SW also L6 under Q302, 9 EP vias) | pad-sized | – |
| BB_PSO: Q204 → caps → R202.1 | L1 pours + L4 island + L6 at C207 | ≥ 2.7 mm | 13 total (none in the Q204 EP: TP1202 sits under it on the bottom) |
| VBB_OUT (5 A, ≤ 28 V): R202.2 → C209–C212 → Q213 | L1 pours + L4 island | plane | 14 |
| SRC_MID (Q213/Q214 drains) | L1 + L4 + L6 | EP-wide | 15 thermal (EP arrays) |
| VBUS_LSW (5 A): Q214 → R243.1 → Q217 | L1 + **L3 helper pour** x 133.4–138.6, y 69.5–81.6 (L1 is choked by R116/C232/R247/C235) | L3 5 mm | 5 + 4 |
| VBUS_LAPTOP (5 A): R243.2/C233 → D501 → J501 | L1 at both ends, L4 island ≥ 8 mm, L6 pour under J501/D501, A4/A9→B9/B4 links | plane | 8 + 8 + 1 |
| +5V sink (≤ 3.3 A): U206.6 → L4 | 0.3 mm stub + small L6 pour | – | **2** |
| 5V_ISNS (8 A): L301.2 → R303.1 | L1 pour 1.9–3.8 mm | | – |
| 5V_BUCK (8 A): R303.2 → C309–C314, Q303 | L6 pour + L4 copy | plane | 4 (R303.2 via-in-pad) + 10 |
| 5V_OR: Q303 → R312.1 | L6 pour (1 mm neck at x 154.5–155.5, under R303) | | – |
| +5V (8 A): R312.2 → L4 plane | L6 pour (to x 162.8 east of U303) | | **5–6** (see problems); C323 5, C324 1 |
| +3V3 / +1V15 buck outputs | L4 islands | plane | 6 (L302.2) / 5 (L303.2) |
| DS_SRC / DS_FETD / VBUS_DS (3 A) | L1 pours at R415/Q402 (drain copper on the right of the SOIC), L4 island | | 3 (Q402.3, under the SOIC body) + 3 (D505/C536) + 2 (J502 B4/B9) + 1 (C422) |
| USB-A (1.8 A each): R704/R709 → SW_IN → TPS IN; TPS OUT → POSCAP → J70x.1 | +5V via L4 (3 vias each), SW_IN: L6 at the shunt → 2 vias → **L3 strip** → 2 vias → L1 at TPS IN; +5V_USBAx L1 pours | ≥ 2 mm | 3 + 2 + 2 |
| ETH_3V3 / ETH_0V95 | small L1 pours at U802 OUT / L801.2 + 3/4 vias (0.5/0.25) to the L4 islands | | |

Gate drives and local loops (grid router, 0.25–0.4 mm, L1 with L3 where needed): BB_HO1/HO2/LO1/LO2 → R203–R206 →
BB_G1–G4, HB1/HB2 and the SW1/SW2 driver returns to C219/C220; BAR_DGATE/HGATE, PD_DGATE/HGATE, SRC_DGATE/HGATE
(L6/L3), SNK_GATE; 5V_HG via R301 (L3 under the stage, outside the SW keep-out), 5V_HO, 5V_LG (0.4 mm), 5V_BOOT,
SW return U301.14 → Q302; 5V_ORG; 3V3_SW/3V3_BST, 1V15_SW/1V15_BST, ETH_SW; U305 VIN from C336 to the L4 +5V strip.

Kelvin taps (0.15 mm, separate tracks; the power pours are pulled back from the inner pad edges so the taps leave
the pad there; the router keeps them off other same-net copper): R201 → R210/R211 → C221 → U201.37/38 (CSA via-in-pad
0.35/0.15 through C221.1/U201.37); R202 → U201.22/23 (two 0.4 mm vias at the pins' inner ends above the EP, then L3;
U201.20 joins C210 directly); R137 → U109.9/10; R243 → U204.8–10; R303 → U301.20/21 (+ U301.16); R312 → U303.8–10;
R704/R709 → U703/U706 IN+/IN−. Card-reader VCC: U901.23 → C913/C914 → J901.4 (0.25 at the pin, then 0.4) and
U901.24 → C916/C915 (0.4).

## 3. Problems / for the lead

1. **Net classes match nothing.** `kicad_pro` patterns are `/VIN*`, `/VBUS_*`, `/+5V`, but these are global nets
   named `VIN`, `VBUS_LAPTOP`, `+5V` (no leading `/`), so HV/PWR/PWR_HC are empty and the DRC never checks the 0.3 mm HV
   rule. My copper keeps 0.3 mm from HV rails by construction (zone clearance 0.3, via placer, router), except at IC
   pins and the deliberate fine-pitch vias at U201. Fix the patterns (e.g. `VIN*`, `VBUS_*`, `+5V`) before the final DRC.
2. **Placement-limited via counts** (top-side parts sit right over the transition sites):
   - VIN at R137 (up to 8 A barrel): only **4** vias to L4. R122/C114 above and R121 below R137.2 block the rest.
     Moving R122/C114 2 mm away would allow ≥ 10.
   - +5V at R312.2 (8 A): **5–6** vias. U603/R626/R632/D602 (VBUS detect, top) sit over R312 and the U301 sense lanes
     run there. I added an L6 pour east of U303. Move the VBUS-detect group ≥ 3 mm, or move R312 to the top.
   - +5V sink at U206 (3.3 A): **2** vias. C211.2, R238 and R246 surround the spot.
   - VBAR at Q106: D102's pads cover the area above the FET, so the main path is the L6 pour (1.45 mm neck between
     the J102 peg and the sleeve pin) plus L4.
   - VBUS_DS at J502: only B4/B9 got vias (0.5/0.25). A9 is left unconnected because the usbc routing puts DS_TX2 and GND
     vias between A9 and B4. R415.1/C421 (+5V feed of the 3 A DS switch) has no via: the hub DS pair vias occupy
     y 78–80, x 169–172. The usbc owner should add VBUS_DS/+5V vias once the pairs are final.
   - No thermal vias in the Q204 EP: TP1202 is placed under it on the bottom.
3. **U201 left pin field is overfull.** C220 above pins 20–23 and R205/R206 beside the pin column force SW2/HB2 up the
   toe column. The R202 Kelvin pair therefore leaves from the inner ends of pins 22/23, through two 0.4 mm vias under
   the package (above the EP corner, 0.15 mm clearance), and U201.20 → C210 runs separately. The clean fix is to move
   C220 to the bottom under pins 25/26.
4. **Freerouting:** the DSN export turns copper zones into planes, which block other nets. Run the autorouter
   without `GND_L1`/`GND_L6` (and ideally without the `P_*` pours), then re-apply the scripts so they refill around
   the result.
5. The mounting holes H1–H4 have no net, so their pad vias float. Assign GND if they are meant to ground the case.
6. **Conflicts with the current HS scripts** (as of this run): a VIN via at (146.1, 107.5) against CR_DN on B.Cu,
   and a hot-loop GND via at C203 (113.7, 107.7) against CR_SD_D1 on F.Cu. Both HS routes cross a power stage and
   should move. The ETH/microSD/CR areas are now excluded from stitching.
7. The DS_GIN/DS_GOUT gates and the CSP/CSN_P1 Kelvin pair go to PMG1 BGA balls. I left them to the usbc/BGA fan-out.

## 4. Left for the autorouter / other owners

Small rail drops and decoupling connections on +3V3 (≈ 199 pads), +1V15 hub caps ↔ VCORE pins, +5V branches (U901,
C901/C902, C241, F1101, R1101, C412/C413/PMG1, U305 caps), ETH_3V3/ETH_0V95 to the RTL pins and decaps, VIN/VBB_OUT
sense taps (U201.3, C215, R234, R207, R209, R220, R235, D205, U202.2, R304, D301), VBUS_LAPTOP to D205/R625/U401,
VBUS_DS to U401, VBUS_PDIN to U101/R133/U104, VBAR to U105/R127/D103, SNK_MID to C238/R248/U205, C213/C115/C415/C422,
the +5V_USBAx clamps (D702/D704 pin 5), CR_USD_VCC long run to J902.4, CR_3V3/CR_1V2 (B.Cu, local), PMG1_VDDD (BGA),
and GND pads/pour islands that still need a via (≈ 74 items).
