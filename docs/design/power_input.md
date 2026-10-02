# odeck-10 — power_input sheet

Source: `hardware/odeck-10/sheets/power_input.py` (generates `power_input.kicad_sch`, ref_base 100, A2).
Status: first schematic pass, 2026-10-02. `build_all.py power_input` → `netlist verify: OK`.
Stock figures: JLC parts API on 2026-10-02.

## Topology

```
 USB-C PD-in (J101) ─ VBUS_PDIN ─┬─ SMCJ51A, 2.2 µF + 100 nF
   CC ─ TPD4S480 (U101) ─ TPS26750 (U102) ── EEPROM AT24C512C (U103, private I2Cc)
   │       VBUS → VBUS_LV (×0.42 in EPR) → TPS26750 VBUS
   │       TPS26750 POWER_PATH_EN ─ 2×2N7002 buffer ─ PD_SINK_EN
   └─ Q104 ──(PD_MID)── Q105 ──┐   LM74800 U104: ideal diode + load switch, EN = PD_SINK_EN, OV 57 V
                                ├── VIN_OR ── 2 mΩ shunt ── VIN (bulk 2×100 µF/80 V + 4×2.2 µF/100 V)
 Barrel PJ-063BH (J102) ─ VBAR ─┤                           INA237 (U109) on I2C_SYS, 0x45
   SMCJ48CA, 100 nF             │
   └─ Q106 ──(BAR_MID)── Q107 ──┘   LM74800 U105: reverse polarity, OV 27.4 V, UVLO 6.8 V,
                                    EN pulled low by Q108 when PDIN_PRESENT (PD-in priority)

 EXT_PWR_PRESENT = BAR_OK OR PD_OK      (SN74LVC1G32, U108; all on +3V3)
   BAR_OK = TLV6700 window on VBAR (9.2 … 28.4 V), via 1N4148W
   PD_OK  = TLV6700 window on VBUS_PDIN (7.7 … 56.2 V) AND TPS26750 sink path enabled (Q103)
```

All four path FETs are BSC026N08NS5 (80 V, 2.6 mΩ, TDSON-8). Both inputs are true ideal diodes with a
second, series cut-off FET, so neither input can back-feed the other. VIN may also be back-fed from
downstream (e.g. the bidirectional buck-boost); both paths block that.

### Interface nets
Global (from `nets.py`): `VIN`, `VBUS_PDIN`, `EXT_PWR_PRESENT`, `PDIN_PRESENT`, `I2C_PD_SCL/SDA`,
`PDIN_INT_N`, `I2C_SYS_SCL/SDA`, `+3V3`, `GND`. **No new inter-sheet nets.**
PWR_FLAGs: `VIN`, `VBUS_PDIN`, plus local `VBAR`.

## 1. PD-in connector and protection

- **J101 JAE DX07S024XJ1R1100** (C134113, 1626 in stock): 24-pin, 5 A / 48 V EPR rated. Same part as the
  laptop port, so one footprint to validate. Power only: VBUS, CC1/CC2, GND, shell → GND.
  **USB2 D+/D-, SBU and SuperSpeed pins are left unconnected** (no data on this port). Consequence: no
  BC1.2 detection, which is irrelevant here since a 5 V-only charger cannot run the deck anyway.
- **TVS SMCJ51A** (C408371, 11.5k): VRWM 51 V ≥ 50.4 V (EPR 48 V + 5 %), VBR 56.7–62.7 V, VC 82.4 V at
  18 A. See risks: the TPD4S480 VBUS pin is 63 V abs max.
- **TPD4S480** (C43131250, 2881): follows the TI reference (TPD4S480 Fig. 7-1, TPS26750 Fig. 8-24):
  RPD_G1/G2 shorted to C_CC1/C_CC2 (dead-battery Rd needed: the deck may be completely unpowered),
  VBIAS 100 nF/100 V (≥ 63 V required), VPWR from TPS26750 LDO_3V3 with 1 µF, VBUS_LV 100 nF/50 V,
  FLT# 10 k to LDO_3V3 → TPS26750 GPIO2. EPR_EN from TPS26750 GPIO0 (also auto-asserts above
  EPR_THRESH). EPR_BLK_G unused (the optional blocking FET is only needed to source 5 V from PP5V).
  SBU channels unused.

## 2. TPS26750 (U102)

- Supplies: VIN_3V3 = `+3V3` (10 µF), LDO_3V3 10 µF (5–25 µF allowed), LDO_1V5 10 µF (4.5–12 µF), CC1/CC2
  220 pF each (200–480 pF). VBUS pins = VBUS_LV (≤ 21.2 V in EPR: 0.42 × 50.4 V).
- **PP5V tied to GND**: sink-only port, no 5 V source and no VCONN needed. (Open issue: confirm with TI that
  grounding PP5V is acceptable; alternative is +5V with 10 µF.)
- **ADCIN1/ADCIN2 = 100 k / 100 k each** (DIV 0.5 → decoded 5/5): *AlwaysEnableSink*, I2C target address
  index #2 = **0x21**. The sink path is enabled at the implicit 5 V contract, so the deck boots from PD-in
  even with a blank EEPROM (JLC delivers it blank) and the RP2350 can then program it. This matches the TI
  example schematic. Alternative (TI's recommendation when a patch is loaded from EEPROM): *SafeMode*,
  ADCIN1 → LDO_3V3, ADCIN2 → GND (7/0), address 0x20 — then a blank EEPROM means no PD-in power.
- **EEPROM AT24C512C-SSHD-T** (C12371, 53k): 64 KB ≥ 36 KB required, address 0x50 (A2..A0 = GND), WP = GND,
  2.2 k pull-ups to LDO_3V3, own 100 nF. Test pads TP101/TP102 on I2Cc for recovery programming.
  The RP2350 reaches it only through the TPS26750 host interface (I2Ct at 0x21); see open issues.
- GPIO use (configured in the EEPROM image):
  - GPIO0 → `PDIN_EPR_EN` (TPD4S480 EPR_EN), 100 k pull-down.
  - GPIO1 → `PDIN_PRES_L` → 1 k → **`PDIN_PRESENT`**; 100 k pull-down so Hi-Z / blank EEPROM = low.
    Configure as push-pull "sink contract active / PD power path enabled". The 1 k limits back-drive into an
    unpowered +3V3 domain (TPS26750 runs from VBUS while the deck boots). `PDIN_PRES_L` also drives Q108.
  - GPIO2 ← TPD4S480 FLT#.
  - GPIO3–7, GPIO11: 100 k to GND (datasheet: tie low when unused; resistor avoids a short if a config drives one).
  - I2Ct_IRQ → `PDIN_INT_N` (10 k to +3V3 on this sheet). I2Cc_IRQ 10 k to LDO_3V3 (must not be grounded).
  - I2Ct SDA/SCL → `I2C_PD_SDA/SCL`; pull-ups expected on the MCU sheet.
- POWER_PATH_EN (6–12 V, ~10 µA charge-pump output, not a logic level) is buffered exactly as datasheet
  Fig. 8-5: Q101 inverts it (`PD_PP_EN_INV`, 100 k to LDO_3V3), Q102 gives `PD_SINK_EN` (100 k to LDO_3V3)
  for the LM74800 EN. Q103 (gate = `PD_PP_EN_INV`) pulls `PD_OK` low while the sink path is off.

## 3. PD-in sink path (U104 LM74800-Q1, Q104/Q105)

Chosen over a TPS26750-driven FET pair because POWER_PATH_EN is referenced to GND and cannot drive a high-side
NFET at 48 V; the LM74800 adds reverse blocking (ideal diode), OV cut-off and inrush control.

- Common-drain back-to-back: Q104 source = VBUS_PDIN (DGATE, ideal diode), Q105 source = VIN_OR (HGATE).
  VS = C = PD_MID, 100 nF VS–GND (100 V), 100 nF CAP–VS.
- **OV**: R121 100 k (from SW) / R122 2.2 k → V_OV = 1.231 × (102.2 / 2.2) = **57.2 V** (55.5–58.9 V with
  V_OVR 1.195–1.267 V); recovery at 1.13 × 46.45 = 52.5 V. Above 50.4 V EPR max, below 70 V abs max.
- **Inrush**: CdVdT = 47 nF/100 V + 100 Ω on HGATE. dV/dt = 55 µA / 47 nF = 1.17 V/ms → 48 V in ~41 ms;
  into an assumed 500 µF total on VIN (this sheet 209 µF + downstream) I = 0.59 A. (The cap sees up to
  VIN + 11 V ≈ 62 V → 100 V part.)
- Losses: 5 A × (2 × 2.6 mΩ) = 0.13 W (+ 10.5 mV regulated drop on Q104 at light load).

## 4. Barrel path (U105 LM74800-Q1, Q106/Q107)

- **J102 Same Sky PJ-063BH** (C3095900, 240 stock — low, pre-order): 5.5 × 2.5 mm, 8 A, 24 V.
  Pin 1 = centre pin (+), pin 2 = sleeve/spring (–) per datasheet. The two MS (mounting/shield) tabs are
  **left unconnected**: tying them to GND would short a reversed plug if the shield touches the sleeve.
- **TVS SMCJ48CA** (C408370, bidirectional): standoff 48 V so a wrongly plugged 36–48 V brick or a reversed
  24 V supply does not destroy it; VC 77.4 V at 19 A, under the 80 V FETs.
- **Why LM74800 instead of the planned LM74720 (C5219205)**: the LM74720 turns its second FET off by pulling
  the gate (PD pin) to GND. In an OR-ing design VIN stays up from PD-in, so that gives Vgs ≈ −48 V (beyond the
  ±20 V rating); TI's 18 V gate-source zener would then conduct and dump up to 10 mA × ~47 V into the PD
  pull-down. The LM74800 references HGATE to OUT, provides the same −65 V reverse protection and an
  adjustable OV, adds an accurate UVLO, needs no boost inductor, and is the same part as the PD path (4040 in
  stock vs 776).
- **OV**: R125 100 k / R126 4.7 k → 1.231 × 104.7 / 4.7 = **27.4 V** (26.6–28.2 V); recovers at 25.2 V
  (1.132 × 22.28). A 24 V ± 5 % brick (25.2 V max) never trips it.
- **UVLO**: R127 100 k / R128 22 k on EN/UVLO → rising 1.231 × 122 / 22 = **6.8 V**, falling 6.3 V.
- **PD-in priority** (hardware only, no MCU): Q108 (2N7002, gate = `PDIN_PRES_L`) pulls EN/UVLO below V_ENF
  → both gates off, LM74800 in shutdown. During the short window before the PD contract (or with a blank
  EEPROM) both paths may be enabled at once; this is safe because both are ideal diodes (the higher voltage
  wins, no cross-conduction).
- Inrush: identical to the PD path (47 nF + 100 Ω, 1.17 V/ms).
- Losses: 8.3 A × 2 × 2.6 mΩ = 0.36 W (on top of the jack contact resistance).

## 5. EXT_PWR_PRESENT

Derived from the input side only (VIN can be back-fed, and a plain VIN comparator would see that):

- **BAR_OK**: TLV6700 U106 window on VBAR through D103 (1N4148W, keeps negative voltage off the TLV6700
  inputs, abs min −0.3 V). Ladder R129 1 M / R130 33 k / R131 15 k (total 1.048 MΩ), V_IT 0.40 V, diode ≈ 0.5 V:
  - UV (INA+ at the 1 M / 33 k node): 0.4 × 1048 / 48 + 0.5 = **9.2 V**
  - OV (INB− at the 33 k / 15 k node): 0.4 × 1048 / 15 + 0.5 = **28.4 V** (≈ barrel OV 27.4 V; in the
    26.6–28.4 V band BAR_OK may read high while the LM74800 is already cut off — only reachable with an
    out-of-spec 27–28 V brick).
  - At 48 V on VBAR the UV input sees 2.2 V (< 7 V abs max).
- **PD_OK**: TLV6700 U107 window on VBUS_PDIN, R133 1 M / R134 47 k / R135 7.5 k (1.0545 MΩ):
  UV 0.4 × 1054.5 / 54.5 = **7.7 V**, OV 0.4 × 1054.5 / 7.5 = **56.2 V**, wire-ANDed with Q103 (sink path
  enabled). **A 5 V PD contract therefore does not count as external power** (5 V on VIN cannot run the
  buck-boost/laptop source path usefully).
- Open-drain outputs per source wire-AND into BAR_OK / PD_OK (100 k pull-ups to +3V3), then SN74LVC1G32 U108
  → `EXT_PWR_PRESENT` (push-pull, +3V3). Everything runs from +3V3, which exists whenever anything powers the
  deck (both TLV6700s are low when +3V3 is absent, and so is the gate).

## 6. VIN: shunt, monitor, bulk

- **Shunt** R137 Vishay WSL25122L000FEA18, 2 mΩ 1 % 2512 (C844691, 29k): 8.3 A → 16.6 mV, P = 0.14 W.
  Placed between VIN_OR and VIN so both sources and any back-feed are measured. Route IN+/IN− as Kelvin pairs.
- **INA237** (U109, C2864837, JLC stock ~5k; replaced the 0-stock INA228 — same pinout):
  85 V common mode, 16-bit. VBUS pin = VIN. VS = +3V3. Address **0x45**
  (A1 = A0 = VS) — chosen to avoid the TMP1075 range 0x48–0x4F and the usual 0x40/0x41 of the INA226s.
  ADCRANGE = 1 (±40.96 mV) → ±20.5 A full scale; CURRENT_LSB = 20.48 A / 2¹⁹ ≈ 39 µA;
  SHUNT_CAL = 13107.2 × 10⁶ × 39.06 µA × 0.002 Ω × 4 (ADCRANGE=1) ≈ 4096. ALERT unused (NC).
- **Bulk**: 2 × 100 µF / 80 V aluminium electrolytic (KNSCHA RVT, C5246576, 12.8k, 10 × 10.5 mm) + 4 ×
  2.2 µF / 100 V X7R 1210 (C153036, 347k). Everything on VIN rated ≥ 80 V (VIN up to 50.4 V). The bulk caps
  sit after the ideal diodes, so they also hold VIN up through input drop-outs and PD transitions. The
  downstream converters add their own low-ESR input ceramics on their sheets.

## Part list

| Ref | Part | LCSC | JLC stock | Notes |
|---|---|---|---|---|
| J101 | JAE DX07S024XJ1R1100 | C134113 | 1626 | USB-C 48 V/5 A, hybrid THT |
| J102 | Same Sky PJ-063BH | C3095900 | 240 | Low stock; pre-order |
| U101 | TI TPD4S480RUKR | C43131250 | 2881 | |
| U102 | TI TPS26750SRSMR | C42166327 | 165 | Low stock; Mouser ~1500 |
| U103 | Microchip AT24C512C-SSHD-T | C12371 | 53480 | |
| U104, U105 | TI LM74800QDRRRQ1 | C3215600 | 4040 | LM74800MDRRR C7216630 (6031) is a drop-in |
| U106, U107 | TI TLV6700DDCR | C2868382 | 1613 | |
| U108 | TI SN74LVC1G32DBVR | C10096 | 112k | |
| U109 | TI INA237AIDGSR | C2864837 | 5240 | Replaced INA228 (0 stock) |
| Q104–Q107 | Infineon BSC026N08NS5 | C5955453 | 5786 | 80 V 2.6 mΩ; TPH2R608NH C5379811 alternative |
| Q101–Q103, Q108 | 2N7002 | C8545 | basic | |
| D101 | SMCJ51A (MDD) | C408371 | 11506 | |
| D102 | SMCJ48CA (MDD) | C408370 | 5406 | bidirectional |
| D103 | 1N4148W | C81598 | basic | |
| R137 | WSL25122L000FEA18 2 mΩ | C844691 | 29410 | |
| C122, C123 | 100 µF 80 V alu SMD | C5246576 | 12807 | |
| C101, C124–C127 | 2.2 µF 100 V X7R 1210 | C153036 | 347k | |
| C102, C103, C112, C115, C116 | 100 nF 100 V 0603 | C15725 | 707k | |
| C114, C118 | 47 nF 100 V 0603 | C576852 | 233k | |
| C106–C108 | 10 µF 0603 | C19702 | basic | |
| others | 0402/0603 R & C | C25741, C25744, C11702, C25879, C25900, C25076, C25768, C26083, C25779, C25756, C25792, C1525, C14663, C52923, C1603 | basic | |
| R135 | 7.5 k 0402 | C25918 | 1.2M | extended |

Approximate cost of the sheet: ≈ $21 incl. INA237 (~$1.9) and TPS26750 (~$3.2).

## Assumptions

- PD-in sources are USB PD compliant: VBUS starts at vSafe5V, and 28–48 V only after EPR entry. This matters
  because the TPD4S480 VBUS pin tolerates only 24 V until VPWR (TPS26750 LDO_3V3) is up.
- The TPS26750 configuration (TI web tool) sets: sink-only, PDOs 5 V + 9/15/20 V SPR + 28/36/48 V EPR,
  GPIO0 = EPR mode, GPIO1 = power path / contract active (push-pull), GPIO2 = fault input.
- Total VIN capacitance (this sheet + downstream) ≈ 500 µF for the inrush numbers.
- +3V3 is generated from VIN (or from laptop 5 V in bus-powered mode) on the power_rails sheet.

## Open issues / risks

1. **TVS margin on PD-in.** No standard TVS stays under 63 V (TPD4S480 VBUS abs max) at full surge current
   with VRWM ≥ 50.4 V. SMCJ51A clamps at ~60 V for small events but 82 V at rated Ipp. Consider a flat-clamp
   TVS (e.g. TI TVS-series ≥ 53 V, if one exists in stock) or a series element before the TPD4S480 VBUS sense
   pin (small resistor; check the TPD4S480 VBUS input current first).
2. **AlwaysEnableSink at 5 V**: with a blank EEPROM (or before the contract) the deck pulls whatever it needs
   from a 5 V default-USB source. The downstream rails must tolerate a 5 V VIN (LM5148 drops out, buck-boost
   UVLO) and firmware must keep the load low until a contract exists. Alternative straps (SafeMode) are listed.
3. **EEPROM update path**: RP2350 → TPS26750 I2Ct → EEPROM requires the TPS26750 host commands for I2C
   pass-through/EEPROM programming — confirm in the TPS26750 Host Interface TRM. Fallback: I2Cc test pads
   TP101/TP102 (programming jig) or an optional link from RP2350 to the I2Cc bus (would need a new global net).
   WP is hard-tied to GND (writable); the odeck-10 plan mentions a controlled WP — not implemented, needs a net.
4. **PP5V tied to GND** — confirm with TI (E2E) for a sink-only TPS26750.
5. **TPS26750 I2C address 0x21** on I2C_PD: check against the PMG1-S3 address chosen on pd_pmg1.
6. **PJ-063BH footprint** (easyeda import): pad spacing (hole → MS 2.0 mm, hole → pin 2 3.0 mm, pin 2 → pin 1
   6.0 mm) has to be checked against the datasheet's recommended layout (which seems to give 3.0 / 5.0 / 12.0
   mm from a different reference) before layout.
7. **Reverse barrel + PD 48 V at the same time**: with A = −24 V, the LM74800 OUT/C pins are rated only up to
   70 V + V(A) = 46 V while VIN = 48 V. Edge case; accepted for the prototype.
8. **BAR_OK OV window** (28.4 V) is ~1 V above the LM74800 OV (27.4 V); EXT_PWR_PRESENT may read high with an
   out-of-spec 27–28 V brick while the barrel path is already off.
9. PJ-063BH (240) and TPS26750 (165) stock is low at JLC — order early.
10. `tools/import_lcsc.sh` appends symbols with space indentation that `kicad-cli sym upgrade` does not
    rewrite unless `--force` is given, and `fix_pins.py` only matches tab-indented symbols. I ran
    `sym upgrade --force` once under the lock. Also `schgen.verify()` reports `#FLG` PWR_FLAG pins as missing,
    and multi-line `note()` text is lost (embedded newlines). The sheet works around both locally.
