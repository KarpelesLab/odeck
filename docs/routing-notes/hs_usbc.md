# Routing notes: `hs_usbc` (high-speed nets of the usbc block + links to the hub)

Script: `hardware/odeck-10/routing/c_hs_usbc.py` (64 nets, no zones). Applied alone on the placed board it is
DRC-clean (no clearance/short/width/hole errors). Impedance widths are the brief's estimates and **must be
confirmed in JLC's impedance calculator for JLC061611-1080A before fab**.

## Plan (reconciling usbc.md and hubrails.md)

The two notes disagreed (usbc: hub SS on L3 down the middle, exit y 80 at x 159-164; hubrails: L1 in the
corridor x 167.5-174 from y 80 up to the hub). Both are kept, joined by a layer change in the free L1 area
just north of the block boundary:

1. **Mux end, L1 -> L3** (via pairs next to the mux hub pins / SSRX caps, x 154.9-164.5, y 63.2-66.0).
2. **L3 corridor under the DP caps**, x 160.0-163.1 (centre-lines 160.37 / 161.19 / 162.01 / 162.83:
   UP TX, UP RX, P5 RX, P5 TX), y 63-76, then L3 east-runs at y 75.55 / 76.92 / 77.74 / 78.56.
3. **L3 -> L1** at x 166.9-174.2, y 78.2-79.5 (UP pairs west of R415, P5 pairs between R415 and C415).
4. **L1 hub corridor** (hubrails intent), columns x 168.17 (UP RX), 169.45 (UP TX), 171.01 (laptop USB2),
   171.70 (P5 RX), 172.97 (P5 TX), down to the hub pins / TX caps C601/C602/C611/C612 at y 88.2.
   No vias in the hub corridor except the two laptop-USB2 vias at y 80.15 (only free row above U602).

**Keep-outs other routers must respect:** L3 x 159.75-163.4 from y 63 to 79 (hub SS corridor, so no through vias
there, which matters for the strap grid under it: put the strap rail vias outside that band); L3 y 79.3-80.6 from x 145.8
to 171 (laptop USB2); L1 x 166.6-174.4, y 76.9-80 (transitions).

## Layers per group

| Group | Route |
|---|---|
| DP ML0-3 (U502 -> C515-C522 -> U503) | L1, 85 ohm (HS_85 class, w 0.10 / g 0.12), straight, P above N cap, N below P cap |
| DP AUX | L1; DP_AUX_N hops on L3 (2 x 0.4 mm vias at 159.05,72.9 / 159.30,75.95): forced crossing (pins P-west/N-east, caps P-north) |
| Laptop lanes J501 -> D502/D503 -> TX caps -> U502 | L1 nested L's; TX1/RX2 straight from the A row; TX2 (B2/B3) and RX1 (B10/B11) leave the THT B row on L3 through the B1-B4 / B9-B12 gaps and come up beside the ESD top pads |
| Downstream lanes J502 -> D506/D507 -> caps -> U503 | L1; B-row pairs (TX2, RX1) via 0.35 mm vias between the SMD rows -> L3 -> up above the ESD; U503's pin order swaps the pairs of each half: RX2 and TX1 hop on L3 (0.35 / 0.45 mm vias) |
| Hub links UP / P5 (+ SSRX caps C513/C514/C530/C531) | see plan; 90 ohm (L3 w 0.16 / g 0.20, L1 w 0.10 / g 0.18) |
| UP_SBU1/2 (U501 -> R502/R503 -> U502) | L6 south from U501, 2 staggered 0.4 mm vias (153.0,72.95 / 153.6,73.55), L1 |
| LAPTOP_USB_DP/DN (D504 -> hub pins 89/90) | D504 flow-through on L6, L6 down x 146, L3 east at y 79.7, vias at y 80.15, L1 column |

Default-class lane nets (UP_*, DS_*, HUB_*) need 0.15 mm clearance, so their L1 "85 ohm" pairs use
gap 0.15 (about 87 ohm) instead of 0.12. **Suggest adding netclass patterns** (UP_TX*, UP_RX*, UP_C_*, DS_TX*,
DS_RX*, DS_C_*, HUB_*_SS_*, *_TX?_IC -> HS_85/USB_90). Then these pairs can go back to the nominal gap.

GND return vias: 22 of 36 wanted (2 per transition) fit and are placed automatically (`gnd_returns`, nearest free spot within 1.3 mm).
The tightest connector hops have none. There, the J501 B1/B12 THT GND pins sit next to the hop.

## Lengths / intra-pair skew (mm, end to end; AC caps counted as zero)

| Pair | P | N | skew | vias P/N |
|---|---|---|---|---|
| UP TX1 | 8.85 | 8.91 | -0.06 | 0/0 |
| UP TX2 | 21.46 | 21.48 | -0.02 | 1/1 (+THT) |
| UP RX1 | 14.82 | 14.93 | -0.11 | 1/1 (+THT) |
| UP RX2 | 16.38 | 16.38 | 0.00 | 0/0 |
| DS TX1 | 15.83 | 15.81 | +0.02 | 2/2 |
| DS TX2 | 10.57 | 10.67 | -0.09 | 2/2 |
| DS RX1 | 17.30 | 17.36 | -0.06 | 2/2 |
| DS RX2 | 10.61 | 11.27 | **-0.66** | 2/2 |
| UP SS TX (incl. IC side) | 47.71 | 47.84 | -0.13 | 2/2 |
| UP SS RX (incl. SSRX stubs) | 43.03 | 43.07 | -0.04 | 2/2 |
| P5 SS TX (cap side only) | 36.51 | 36.49 | +0.02 | 2/2 |
| P5 SS RX | 46.37 | 46.66 | **-0.29** | 2/2 |
| DP ML0 / 1 / 2 / 3 | 4.82 / 4.84 / 4.87 / 4.91 | 4.87 / 4.89 / 4.92 / 4.94 | -0.05 / -0.05 / -0.04 / -0.03 | 0 |
| DP AUX (1 Mb/s, not matched) | 10.96 | 16.54 | -5.6 | 0/2 |
| Laptop USB2 (D504 -> hub) | 54.67 | 53.99 | +0.68 | 2/2 |

Matching uses 45-degree bumps (`tune=` in `lane()`). DS RX2 and P5 RX keep a residual skew because there was no room for more bumps:
DS RX2's L1 drop is boxed in by C535/U504, and the P5 RX column shares its gap with P5 TX.
DP lanes match each other to within 0.1 mm.

## Not routed / blocked (placement)

1. **HUB_P5_TXP_IC / HUB_P5_TXN_IC (hub pins 83/84 -> C611/C612 pad 1): open.** The caps are in reverse P/N
   order w.r.t. the pins (same for C601/C602). UP side is solved by running HUB_UP_TXN_IC under C601's body
   (0.09 mm track between its pads). For P5 there is no room west of C611 (P5 RX + laptop USB2), and the bottom
   decaps under the pin row leave no via spot. **Fix (hubrails): swap C611 <-> C612 (x 172.35 <-> 173.6)**, then
   two straight stubs. Note that P5 TX polarity is fixed with a detour of HUB_DSC_SS_TXN on L3 at the top
   (164.5-164.9, 65.3-66.5): if the caps are swapped, drop that detour (route the pair with pleft=True).
   Swapping C601/C602 too would remove the under-cap track.
2. **Laptop receptacle slow nets: CC1 (A5), SBU1 (A8), D- (A7 tie), B5/B8 (CC2/SBU2), D+/D- to D504 top
   pads: open.** U501 (TPD4S480, bottom) sits directly under the D502/D503 gap. The A-row escape band
   (y 60.4-61.4) has room for the RX1 vias only. Also, U501's pin order C_CC1(4) C_CC2(5) | RPD_G2(6) RPD_G1(7) nests
   CC2 inside CC1 and needs a via in the corner, which is where RX1/D502 are.
   **Needed: move U501 about 2 mm south (or rotate 90 deg)** so that vias fit between the A row and U501.
   LAPTOP_CC1/2 (U501 -> PMG1 N15/J15) were not attempted for the same reason: their exit around U501
   collides with C502, the J501 NPTH/shell and the hub-SS L3 escape.
3. **Downstream slow nets: J502 CC/SBU/D+/D- -> U504, DS_CC1/2 -> PMG1, DS_SBU1/2 (U504 -> R542/R543 ->
   U503), HUB_DSC_DP/DN (U504 -> hub): open.** Through vias are blocked around U503/U504 by the bottom
   parts (U504 under D506/D507, R410-R412 and U503 decaps at x 169-175, y 65.6-71.8, C537). The free
   spots went to the lane crossings. DS_SBU2 can only drop at (166.9,73.25) between the AUX-N and SBU1
   lines. DS_SBU1/U503 pin 28 also need a via that has no free spot.
4. **TP1206** (2x2 mm GND pad, `right` block) sits at (150.7,67.55) in the laptop lane fan-in. RX1 detours
   around it; move it (usbc.md suggested about 143.4,65.0).

## Side effects for other routers

- U502 strap pins 32/35/38 and U503 strap pins 11/14/17 sit between DP lanes with **no room for a via
  between the lanes on the U502 side** (the N leg must dive under the P cap within 0.7 mm). Use
  via-in-pad, or take them out along the gap between the two cap columns. U503 side: 0.35 mm via at x 163.75 fits.
- U502 pin 28 (+3V3) is crossed by DP_AUX_N just below its toe. Escape diagonally to (158.75, 72.95).
- U502 pins 21-23 (CTL) and U503 21-23: UP_SBU / DS_AUX run 0.25-0.45 mm below the toes. Use staggered toe
  vias.
- The hub VDD toe vias for pins 85/88/93 are partly hemmed in by the UP TXN_IC under-C601 track and the USB2 jogs.
- The laptop USB2 L3 run at y 79.7 crosses the hubrails VBUS_LAPTOP feed area (x 158-161, y 80). Take that feed on L6.
- L3 reference: the corridor and the J501 B-row hops need a solid L4 island (+3V3 / VBUS_LAPTOP) above
  them, and no L2 void under the DP caps where the corridor passes.

## Conflicts seen when run together with the other scripts (a_planes, b_power, d_hs_hub, e_hs_eth_sd)

There is no net overlap. The only DRC hits on my nets come from `b_power`, and both are in areas this plan reserves:
- VBUS_DS stubs and vias under J502 A4/A9 at (169.75, 61.3) and (172.25, 61.3) collide with DS TX2/RX1/RX2.
  Move them between the J502 rows (tie A9-B4 / A4-B9 there), or north of the A row. The via at
  (174.5, 79.1) collides with the P5 TX transition via.
- +5V vias on R415 pad 1's south edge (170.1 / 170.9 / 171.7, 79.75) hit the laptop-USB2 vias and P5 RX.
  Put them inside or north of pad 1 (y 78.3-79.4).
