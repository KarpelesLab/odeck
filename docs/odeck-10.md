# odeck-10 — 10 Gbps prototype

First odeck build. Goal: a fully working, fully open USB-C deck assembled entirely by JLCPCB
(LCSC stock, plus Mouser/DigiKey consigned parts where needed), validating everything the
later 20G/40G versions will reuse: power architecture, MCU/LCD firmware, card reader, 2.5GbE,
board outline and silkscreen style. Only the core and high-speed section change later.

Status: **planning** (2026-10-02). Stock figures are JLC parts API on 2026-10-02 — re-check before ordering.

## Block diagram

```
                       ┌──────────────────────────── odeck-10 ────────────────────────────┐
 Laptop USB-C ═════════╪═ TUSB1046 ══ USB 10G ══► USB 10G hub (USB7206C/USB7216C)          │
 (UFP, 10G + DP alt,   │  alt-mode   │              ├─► USB-A 10G ×2–3                     │
  EPR source 140 W)    │  mux/redrv  │              ├─► GL3224 ─► SD + microSD             │
                       │             │              ├─► RTL8156BG ─► RJ45 2.5GbE           │
                       │             │              ├─► RP2350B (USB2: UF2, status app)    │
                       │             │              └─► downstream USB-C (USB 10G)  ◄─┐    │
                       │             └─ DP 2-lane HBR3 (4K60) ────────────────────────┘    │
                       │                                (DP alt mode out on downstream C)  │
                       │                                                                   │
 PD-in USB-C (EPR) ────┤                                                                   │
 Barrel 9–24 V ────────┼─► priority OR (LTC4417 / LM74700) ─► VSYS ─┬─► buck-boost ─► 5–28 V to laptop VBUS
 Laptop VBUS (bus pwr)─┘                                            ├─► 5 V (USB-A, downstream C, LCD)
                       │                                            └─► 3.3 V / 1.x V rails
                       │  RP2350B ── I2C ── PD controllers, hub (SMBus), LCD (SPI), PHY/card LEDs
                       │          └─ 2.0" 320×240 IPS LCD, user GPIO header (unpopulated), Qwiic, SWD
                       └───────────────────────────────────────────────────────────────────┘
```

## Parts (draft)

| Block | Part | JLC stock | Notes |
|---|---|---|---|
| Alt-mode mux + redriver (upstream) | TI TUSB1046-DCI | 42–67 | UFP crosspoint: 2× USB 10G lanes + 2× DP lanes |
| PD controller, laptop port | **TBD** — needs EPR source **and** DP alt mode (UFP_D) | — | See open question 1 |
| PD controller, PD-in port | TPS26750 (EPR sink) | 165 | Power-only; datasheet confirms EPR 28/36/48 V + I2C, no alt-mode features |
| Type-C protection | TPD4S480 | 2881 | Paired with TPS26750 for EPR |
| USB 10G hub | Microchip USB7206C or USB7216C | 21 / 3 | Public datasheet + documented registers (per-port speed for LCD). Port count to verify. Fallback RTS5420 (372, NDA) |
| SD + microSD | Genesys GL3224-ONY04 (QFN48) | 1646 | 2 slots, UHS-I, ROM, public datasheet |
| 2.5GbE | Realtek RTL8156BG-CG | 2915 | LED pins → RP2350 for link speed |
| RJ45 | 2.5G-rated magjack (TBD) | — | THT |
| Input OR-ing | LTC4417 (3-input priority) or LM74700 ×3 + FETs | 3k+ / 5k+ | Priority PD-in > barrel > bus |
| Buck-boost to laptop | LM5176 / LM51770 + external FETs | 12k / 1k | 9–48 V in, 5–28 V × 5 A out |
| Barrel jack | 5.5×2.5 mm, high-current (8 A+) | TBD | THT, TVS SMBJ24A-class + OVP |
| MCU | RP2350B (QFN-80) + W25Q128 | 3875 / 51k | |
| Display | HS20HS072RX 2.0" 320×240 IPS ST7789 | 2208 | On ~1 mm foam tape |
| LEDs | 1–2 status LEDs | basic | Power / fault |

## Power targets
- Laptop: up to 140 W EPR (28 V × 5 A), 100 W SPR fallback. Test host: MacBook Pro 16" M4 Max.
- Inputs: PD-in USB-C EPR sink (up to 240 W charger), barrel 9–24 V (~200 W at 24 V, ~60 W total at 12 V), bus power.
- RP2350 manages a dynamic budget but **cannot override PD controller safety**: controllers boot
  autonomously from their own config/EEPROM.

## Open questions
1. **Laptop-port PD controller with EPR source + DP alt mode.** TPS26750 is power-only. Candidates:
   TI TPS66994 (EPR, dual-port, USB4-oriented — 0 JLC stock, consign from Mouser/DigiKey; verify features),
   Infineon CCG8 (CYPD8125/8225 — verify EPR + alt mode), or open PD stack on a dedicated MCU with UCPD.
2. **Display out:** downstream USB-C with DP alt mode (works with any USB-C→HDMI/DP cable — recommended),
   full-size DP connector, or both via a mux (only one 2-lane DP stream without MST).
3. Hub port count: RTL8156 + GL3224 + RP2350 + 2–3× USB-A + downstream C = 6–7 ports.
4. JLC assembly of LCD (foam tape + FPC tail soldering) and THT parts (barrel, RJ45, USB-A).
5. High-current barrel jack in stock.
6. Stackup: 6-layer standard is likely enough for 10G; decide during layout.

## Notes on a 20 Gbps step
USB 3.2 Gen2x2 (20G) is **not supported by Apple Silicon Macs** (they fall back to 10G), uses all 4
lanes (no DP alt mode at the same time), and essentially no Gen2x2 hub chips exist. A useful 20G step
would therefore be **USB4 at 20 Gbps**, which still needs a USB4 chip — same sourcing problem as 40G.
