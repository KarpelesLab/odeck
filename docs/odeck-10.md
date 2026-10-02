# odeck-10 — 10 Gbps prototype

First odeck build. Goal: a fully working, fully open USB-C deck assembled entirely by JLCPCB
(LCSC stock, plus Mouser/DigiKey consigned parts where needed), validating everything the
later 20G/40G versions will reuse: power architecture, MCU/LCD firmware, card reader, 2.5GbE,
board outline and silkscreen style. Only the core and high-speed section change later.

Status: **planning** (updated 2026-10-02). Stock figures are JLC parts API / Mouser on 2026-10-02 —
re-check before ordering. Detailed research: `research/pd-controllers.md`, `research/hub-signal-path.md`,
`research/power-and-assembly.md`.

## Block diagram

```
 Laptop USB-C ═══ TUSB1064 (UFP mux) ══ USB 10G ══► USB7206C hub
 (data UFP, 10G     │                                 ├─ 10G ─► USB-A #1
  + DP alt C/D,     │                                 ├─ 10G ─► USB-A #2
  EPR src 140 W)    │                                 ├─ 10G ─► GL3523 5G hub (if 3× USB-A)
                    │                                 │           ├─► GL3224 ─► SD + microSD
                    │                                 │           ├─► RTL8156BG ─► RJ45 2.5GbE
                    │                                 │           └─► USB-A #3 (5G)
                    │                                 ├─ 10G ─► TUSB1046 (DFP mux) ═══ downstream USB-C
                    │                                 └─ USB2 ─► RP2350B (UF2, status app)
                    └── DP 2-lane HBR3 + AUX ───────────────────► TUSB1046 (DP alt out, 4K60)

 PMG1-S3 (CYPM1322, dual-port): port 0 = laptop (EPR source, DP UFP_D, drives TUSB1064)
                                port 1 = downstream C (5 V/3 A source, DP DFP_D, drives TUSB1046, HPD relay)
 TPS26750 + TPD4S480: PD-in charger port (EPR sink, up to 48 V)

 PD-in 5–48 V ──► LM74700/LM74800 ─┐
 Barrel 9–24 V ─► LM74720 (rev/OVP)┴─► VIN 9–48 V ─┬─► LM51770 buck-boost ─► 5/9/15/20/28 V ─► [src switch] ─► laptop VBUS
                  (barrel disabled by PD-in present)├─► LM5148 ─► 5 V (USB-A, downstream C, LCD)
 Laptop VBUS ────► [sink switch, only when no external power] ─► 5 V rail (bus-powered mode)
                                                     └─► 3.3 V / 1.15 V / 1.2 V bucks

 RP2350B ── I2C: PD controllers (status/requests only), hub SMBus (port speeds), LCD SPI,
            RTL8156 LED pins, card-detect; 2.0" LCD, GPIO header (unpopulated), Qwiic, SWD
```

## Parts (draft)

| Block | Part | Stock (JLC / Mouser) | Notes |
|---|---|---|---|
| PD: laptop + downstream C | Infineon PMG1-S3 CYPM1322-97BZXI (BGA-97) | 50 / 8095, $7.13 | 28 V EPR src/sink, DP alt UFP_D + DFP_D; Infineon dock example on GitHub; PD stack is a closed Infineon library (downloaded at build, not committed). Fallback: 2× QFN-48 PMG1 |
| PD: charger input | TI TPS26750 + TPD4S480 | 165 / — ; 2881 | EPR sink 28/36/48 V, boots from ROM + I2C EEPROM |
| Upstream mux | TI TUSB1064 (UFP) | 73 / ~400 | 10G + 2-lane DP HBR3, pin assign C/D/E. **Buy early** |
| Downstream mux | TI TUSB1046-DCI (DFP) | 59 / 2798 | |
| USB 10G hub | Microchip USB7206C | 26 / 1950, $8.66 | 5× 10G + 1× USB2; ROM; per-port speed via SMBus (AN2935); ~1.8 W, needs 1.15 V/2 A |
| Sub-hub (3rd USB-A) | Genesys GL3523 (5G) | 11.9k, $2.46 | Carries card reader + LAN + USB-A #3 |
| SD + microSD | Genesys GL3224-ONY04 | 1646 | 2 slots, UHS-I, ROM |
| 2.5GbE | Realtek RTL8156BG-CG | 2915 | LED pins → RP2350 |
| Input OR / protection | LM74720 (barrel, reverse + OVP), LM74700/LM74800 (PD-in) | 776 / 5k+ | Hardware priority PD-in > barrel. LTC4417 rejected (36 V max) |
| Buck-boost to laptop | TI LM51770 + external FETs | 1007 / 2131 | 78 V rated; defaults 5 V; voltage steps set by PD-controller GPIOs (MCU can't set voltage); ~96–97 % eff. Plan B BQ25756 |
| 5 V rail | TI LM5148 (80 V buck ctrl) | 57k | Up to ~8 A |
| 3.3 V / 1.x V | TPS62933 / TPS563201; TPS62A02 / TLV62569 | stock | |
| USB-A port switches | TPS2553 | stock | |
| MCU | RP2350B + W25Q128 | 3875 / 51k | |
| Display | HS20HS072RX 2.0" 320×240 IPS | 2208 | JLC hand-solders FPC; foam tape TBC with JLC |
| Barrel jack | Same Sky PJ-063BH (5.5×2.5, 8 A) | 240 / 1580 | 2.1 mm plugs won't fit |
| RJ45 2.5G | USAKRO DGUK211Q340CD2A4D2 | 111 | Low stock; no LEDs |
| USB-A 10G | Amphenol GSB4111312HR | 3846 | |
| USB-C (laptop, PD-in; 48 V/5 A/10G) | JAE DX07S024XJ1R1100 | 1626 | |
| USB-C (downstream, 20 V/5 A/10G) | Amphenol 12401610E4#2A | stock | |
| SD / microSD sockets | Hanbo SD-111 / Hirose DM3AT | 5209 / 18849 | |

## Key design rules
- **Power safety independent of RP2350 firmware:** PD controllers boot autonomously; buck-boost voltage
  selected only by PD-controller GPIOs; buck-boost/power-path controls on a bus/pins the RP2350 can't reach.
- **Laptop-port direction:** source switch (to laptop) enabled only with external power + buck-boost
  power-good; sink switch (bus power → 5 V rail) enabled only with no external power. Back-to-back FETs,
  never both on. Live transitions via PR_Swap / Fast Role Swap.
- **Hub boot independent of RP2350:** hub SMBus pull-ups powered from an RP2350 GPIO, so in BOOTSEL /
  broken-firmware state the hub boots with defaults and UF2 recovery still works.
- **DP path:** TUSB1064 DP outputs → AC caps → TUSB1046 DP inputs; AUX AC-coupled between muxes;
  each PD port drives its own mux; HPD: monitor → port 1 → port 0 → laptop.

## Power & thermal
- Laptop: up to 140 W EPR, 100 W SPR fallback. Test host: MacBook Pro 16" M4 Max.
- Worst-case board dissipation **~12–14 W** → ~60–80 K rise on a bare 100×60 mm board. **Biggest risk.**
  Mitigations: temperature-based power derating by firmware (thermistors near buck-boost/hub),
  heavy copper + via arrays, optional bottom aluminium plate, or slightly larger board.

## Open questions
1. **PMG1 first-flash path** that later RP2350 user firmware can't abuse (PMG1 USB/I2C bootloader?
   one-time flash then lock? JLC post-solder programming via test pads?).
2. Does PMG1-S3 support PR_Swap / Fast Role Swap for bus-powered ↔ external-power transitions, and do
   Macs accept it? Alternative: accept a brief disconnect when external power is plugged/unplugged.
3. Display out: downstream USB-C DP alt (current plan) vs full-size DP.
4. 2 vs 3 USB-A ports (3 needs the GL3523 sub-hub).
5. JLC: foam tape application for the LCD; low stock on RJ45 (111), TUSB1064 (73), USB7206C (26), PMG1 (50)
   → consign from Mouser/DigiKey.
6. Thermal budget vs board size (100×60 target).
7. Stackup: 6-layer standard likely enough for 10G; decide during layout.

## Notes on a 20 Gbps step
USB 3.2 Gen2x2 (20G) is **not supported by Apple Silicon Macs** (they fall back to 10G), uses all 4
lanes (no DP alt mode at the same time), and essentially no Gen2x2 hub chips exist. A useful 20G step
would therefore be **USB4 at 20 Gbps**, which still needs a USB4 chip — same sourcing problem as 40G.
