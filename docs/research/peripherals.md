# Peripheral chips (researched 2026-10-02)

Stock/prices from JLCPCB parts API on 2026-10-02. All ICs are **Extended** parts. V = verified, I = inferred.
Note: research assumed a VL830 core; the VL830 has since been ruled out (see usb4-hub.md). Choices below
depend on the final core (JHL8440 → native PCIe + USB3; RTS5490 → DP out, 2× USB 20G, integrated PD).

## DP → HDMI PCON — none currently orderable at LCSC/JLC
| Part | Output | Pkg | FW | LCSC |
|---|---|---|---|---|
| Lontium LT8711GX | HDMI 2.1 FRL 8G×4, DSC | QFN88 0.4 mm | Internal flash, I2C/SPI/AUX update | C7494431 no-buy |
| Lontium LT8711UXD | HDMI 2.0 4K60 | QFN48 0.4 mm | Internal flash + HDCP | C37634965 no-buy |
| Parade PS196 | HDMI 2.1 FRL 12G×4 | QFN74 | NDA, secure boot | — |
| Realtek RTD2173 | HDMI 2.1 4K240/8K60 | ? | NDA, SPI flash (I) | — |

Pick: LT8711GX (consign / Lontium distributor); fallback LT8711UXD. Timing readback over I2C likely but undocumented.
4K120 8-bit over DP 1.4 HBR3 x4 needs CVT-RB2, 4:2:0, or DSC.

## USB 3.2 Gen2 hub (if needed)
- Realtek RTS5420-GR — C35880247, 372 pcs, $6.56, SPI FW (V)
- VIA VL822-Q7 — C42419379, 0 pcs; per-port USBLED pins
- Genesys GL3590 — C7470882, 0 pcs, $2.26; I2C/SMBus + LED GPIOs (register map NDA)
Per-port link-speed readback over I2C isn't publicly documented for any of these.

## SD + microSD
- **Genesys GL3224-ONY04** (QFN48 version = 2 slots / 2 LUNs, UHS-I SDR104, ROM) — C157358, 1646 pcs, $1.39. Public datasheet.

## 2.5GbE
- USB: **RTL8156BG-CG** — C41376388, 2915 pcs, $3.22 (ROM FW)
- PCIe: RTL8125BG-CG — C3013605, 925 pcs, $4.34; Intel I226-V — C26159200, 978 pcs, $6.20 (needs NVM)
- RJ45 2.5G: USAKRO DGUK211Q340CD2A4D2 — C19725134 (no LEDs); HanRun HR911130A C54408 (1G rated, LEDs)

## USB PD / power
- TPS65994AD (2-port, USB4/TBT4, NRND) — C2864593, 497 pcs, $3.24
- TPS65987DDK (20 V/5 A path, NRND) — C2866116, 0 pcs
- CYPD6227 (BGA96) — C22453211, 20 pcs — **Obsolete at DigiKey** (successor CYPD6229)
- FUSB302BMPX TCPC — C132291; HUSB238 fixed sink ≤100 W — C7471904
- STM32 UCPD + TCPP02/03 (TCPP03 0 stock)
- Buck-boost source: **TPS55288RPMR** (I2C, ~100 W) — C2864583, 5152 pcs, $2.20; BQ25756 C19272232; LM5176 C442493
- DP redriver TDP142 — C2674217 (likely unnecessary)

## MCU & LEDs
- STM32G0B1CCU7 (2× UCPD + USB DFU) — C29759424, 295 pcs, $2.81
- RP2040 — C2040, $0.99; RP2350A — C42411118, $1.29
- CH32X035G8U6 — C7437027, $0.53
- LEDs: SK6805-EC15 (1.5 mm) — C2890035, $0.099; WS2812B-2020 — C52917434. Need ~3.7–5 V supply / level shift.

## Authorized distributor sweep (Mouser/DigiKey, 2026-10-02)
- **DP→HDMI: nothing at authorized distis** (Lontium/Parade/ITE/Realtek). Lontium via LCSC Global Sourcing or agent (Avaq, Nexcomm).
  Kinetic MCDP2900 (public datasheet) is obsolete.
- **PD:** TPS65994AD (DK 23k pcs, NRND), TPS65988 (NRND), TPS65987DDK (NRND), CYPD5235 (Active, ~4k Mouser), CYPD8225 CCG8 (Active, DK 1990),
  CYPM1311 PMG1-S3 (Active). TPS25751/TPS26750 active but single-port, no TBT alt-mode (I).
- **10G hub:** GL3590/VL822 LCSC-only. Authorized alternative: Microchip USB7206C/USB7216C/USB7252C (public datasheets, ~$9–10, thousands at Mouser).
