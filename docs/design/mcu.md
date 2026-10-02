# odeck-10 — MCU sheet (`mcu.kicad_sch`, refs 1000+)

Source: `hardware/odeck-10/sheets/mcu.py` (generated, netlist-verified). References:
- RP2350 datasheet (build 2026, "DS"): pin table 14.8.2, abs max 14.9.1, GPIO functions 9.4.
- Raspberry Pi *Hardware design with RP2350* release 3 (2026-08-20), "minimal design" R4-S1 ("HWD").

Stock figures are from the JLC parts API on 2026-10-02.

## Block

```
+3V3 ─┬─ IOVDD x8, QSPI_IOVDD, USB_OTP_VDD, VREG_VIN (100 nF each, 4.7 µF C1001, 10 µF bulk)
      ├─ 33R ─ VREG_AVDD (4.7 µF)          VREG_LX ─ L1001 3.3 µH (AOTA, polarised) ─ +1V1 = DVDD x3 + VREG_FB (4.7 µF)
      └─ 10R ─ ADC_AVDD (4.7 µF + 100 nF) ─ 10k ─ NTC_ADC0/1 (NTC to GND on sensors)
XIN ─ Y1001 ABM8-272-T3 12 MHz ─ 1k ─ XOUT, 2x 15 pF       QSPI ─ U1002 W25Q128JVSIQ; QSPI_SS ─ 1k ─ BOOTSEL ─ GND
RUN ─ 1k ─ RESET ─ GND      SWD pads TP1001-4 (SWCLK, SWDIO, RUN, GND)     USB_DP/DM ─ 27R ─ MCU_USB_DP/DN (hub port 6)
I2C1 (GPIO2/3) = I2C_SYS, 2.2k ─┬─ TCA9534 @0x20: EXT_PWR_PRESENT, LAPTOP_OVP_N, TEMP_ALERT_N, CR_CD_SD_N, CR_CD_USD_N,
                                 │                   ETH_RESET_N (out), 2 spare; INT ─ IOX_INT_N (GPIO46)
I2C0 (GPIO4/5) = I2C_PD 2.2k;  PIO I2C: HUB SMBus (GPIO8/9, no pull-ups), I2C_EXT/Qwiic (GPIO30/31, 4.7k)
```

## Part choice
- **RP2350B (C42415655)**: 3873 in stock, $1.28. It is the QFN-80 part with 48 GPIO and no internal flash.
  - The symbol and footprint are LCSC imports. Pin numbers match DS table 1674 (QFN-80 column).
    - GPIO0 = 77 … GPIO3 = 80, GPIO4 = 1.
    - IOVDD = 5/15/24/29/41/50/60/76, DVDD = 10/32/51.
    - VREG_AVDD/PGND/LX/VIN/FB = 61–65, USB_DM/DP = 66/67, USB_OTP_VDD = 68, QSPI_IOVDD = 69, ADC_AVDD = 59.
    - EP = GND (81).
  - Pin types are fixed with fix_pins.
- **The regulator and crystal follow HWD exactly.** RPi says layout or part deviations are "at your own risk".
  - **L1001 Abracon AOTA-B201610S3R3-101-T (C42411119)**: 3338 in stock. It is the polarity-marked 3.3 µH part RPi
    co-developed. Place it with the dot toward VREG_LX, as in the RPi layout.
  - **Y1001 Abracon ABM8-272-T3 (C20625731)**: 13.6k in stock. 12 MHz, CL 10 pF, ESR 50 Ω, the Pico 2 crystal.
    It uses 15 pF load caps and a 1k XOUT damping resistor.
  - Caps: C6/C7/C9 equivalents are 4.7 µF 0402 (C1001–C1003), and R3 = 33 Ω (R1001).
- **U1002 W25Q128JVSIQ (C97521, basic)**: 49.6k in stock. 16 MB is the RP2350 maximum. It holds the RP2350 firmware plus the
  bundled PMG1 image, TPS26750 EEPROM image and hub configuration. QSPI_SS has a 10k pull-up, DNP per HWD (R1004), and the
  1k BOOTSEL resistor (R1005).
- **U1003 TCA9534PWR (C783615)**: 15k in stock, $0.71. It is needed because all 48 GPIO are used (see the table). Address
  0x20, free on I2C_SYS.
- Buttons SW1001 (BOOTSEL) and SW1002 (RESET) are TS-1187A-B-A-B (C318884, basic). A-B and C-D are joined internally
  (datasheet), and both sides are wired.
- LEDs: D1001 KT-0805G green (basic) is the power LED, on +3V3 through 330 Ω. D1002 KT-0603R red (basic) is the status LED,
  on GPIO47 through 1k.
- J1001 is the debug UART: a 1x3 2.54 mm header, unpopulated (`in_bom no`). TP1001–TP1004 are the SWD pads, copper only.

## GPIO allocation (complete)

FT = fault-tolerant pad: 5.5 V max with IOVDD at 3.3 V, and ≤ 3.63 V with IOVDD = 0 and very little current (DS 14.8.2.1).
GPIO40–47 are standard pads: max IOVDD + 0.5 V, so only 0.5 V while +3V3 is off.

| GPIO | Pin | Net | Dir | Function / block | Notes |
|---|---|---|---|---|---|
| 0 | 77 | UART_TX (local) | out | UART0 TX | Debug header J1001 |
| 1 | 78 | UART_RX (local) | in | UART0 RX | Debug header J1001 |
| 2 | 79 | I2C_SYS_SDA | io | I2C1 SDA | 2.2k PU here. INA226 ×2, INA237, TMP1075 ×8, TCA9534, EUI-48 EEPROM |
| 3 | 80 | I2C_SYS_SCL | io | I2C1 SCL | 2.2k PU here |
| 4 | 1 | I2C_PD_SDA | io | I2C0 SDA | 2.2k PU here. PMG1 HPI 0x42, TPS26750 0x21 |
| 5 | 2 | I2C_PD_SCL | io | I2C0 SCL | 2.2k PU here |
| 6 | 3 | I2C_PD_INT_N | in | PMG1 interrupt | OD, 10k PU on pd_pmg1 |
| 7 | 4 | PDIN_INT_N | in | TPS26750 interrupt | OD, 10k PU on power_input |
| 8 | 6 | HUB_SMB_DAT | io | PIO I2C SDA | **No pull-up here** (fed from HUB_SMB_PU on usb_hub). Also I2C0-capable |
| 9 | 7 | HUB_SMB_CLK | io | PIO I2C SCL | Clock stretching is handled by the PIO program |
| 10 | 8 | HUB_SMB_PU | out | push-pull | Powers the hub SMBus pull-ups. Low at reset, so the hub boots stand-alone |
| 11 | 9 | HUB_RESET_N | OD | open-drain emulation | 10k PU + RAILS_PG wire-OR on usb_hub |
| 12 | 11 | HDR_GPIO0 | io | user header | GPIO12–19: PIO-contiguous, **HSTX**, UART0, SPI1/SPI0, I2C0/1, PWM6/7/0/1 |
| 13 | 12 | HDR_GPIO1 | io | user header | |
| 14 | 13 | HDR_GPIO2 | io | user header | |
| 15 | 14 | HDR_GPIO3 | io | user header | |
| 16 | 16 | HDR_GPIO4 | io | user header | |
| 17 | 17 | HDR_GPIO5 | io | user header | |
| 18 | 18 | HDR_GPIO6 | io | user header | |
| 19 | 19 | HDR_GPIO7 | io | user header | |
| 20 | 20 | LCD_DC | out | SIO | SPI0 RX slot, unused by a write-only panel |
| 21 | 21 | LCD_CS_N | out | SPI0 CSn | |
| 22 | 22 | LCD_SCK (via 33R R1024) | out | SPI0 SCK | Up to 62.5 MHz |
| 23 | 23 | LCD_MOSI (via 33R R1025) | out | SPI0 TX | |
| 24 | 25 | LCD_RST_N | out | SIO | Reset pull-down holds the panel in reset until firmware runs |
| 25 | 26 | LCD_BL_PWM | out | PWM4 B | Reset pull-down plus 100k on display_ui keep the backlight off |
| 26 | 27 | PMG1_SWCLK | out | PIO SWD probe | Via solder jumper on pd_pmg1 |
| 27 | 28 | PMG1_SWDIO | io | PIO SWD probe | Via solder jumper on pd_pmg1 |
| 28 | 36 | PMG1_XRES_N | OD | open-drain emulation | Pass FET + jumper + 4.7k PU on pd_pmg1 |
| 29 | 37 | PDIN_PRESENT | in | status | 3.3 V from the TPS26750 GPIO via 1k (power_input). It can be high while +3V3 is off, which an FT pin tolerates |
| 30 | 38 | I2C_EXT_SDA | io | PIO I2C (Qwiic) | 4.7k PU here. Also I2C1-capable |
| 31 | 39 | I2C_EXT_SCL | io | PIO I2C (Qwiic) | 4.7k PU here |
| 32 | 40 | BTN_A_N | in | user button A | 10k PU + 10 nF on display_ui |
| 33 | 42 | BTN_B_N | in | user button B | 10k PU + 10 nF on display_ui |
| 34 | 43 | USBA1_FORCE_EN | out | push-pull | Reset pull-down = off. usb_a should also add a pull-down |
| 35 | 44 | USBA2_FORCE_EN | out | push-pull | Same as USBA1_FORCE_EN |
| 36 | 45 | ETH_LED0 | in | PIO/SIO | RTL8156BG LED pin. Edge counting for activity |
| 37 | 46 | ETH_LED1 | in | PIO/SIO | |
| 38 | 47 | ETH_LED2 | in | PIO/SIO | |
| 39 | 48 | CR_LED | in | SIO | GL3224 activity. The GL3224 runs from +5V, so it can be live before +3V3; FT pin |
| 40 | 49 | ADC_ISNS1 ← 10k ← USBA1_ISENSE | ain | ADC0 | 10 nF at the pin |
| 41 | 52 | ADC_ISNS2 ← 10k ← USBA2_ISENSE | ain | ADC1 | 10 nF at the pin |
| 42 | 53 | NTC_ADC0 | ain | ADC2 | 10k bias to ADC_AVDD + 100 nF here. NTC to GND on sensors |
| 43 | 54 | NTC_ADC1 | ain | ADC3 | Same as NTC_ADC0 |
| 44 | 55 | HDR_ADC0 | ain | ADC4 | 1k + ESD on display_ui |
| 45 | 56 | HDR_ADC1 | ain | ADC5 | 1k + ESD on display_ui |
| 46 | 57 | IOX_INT_N (local) | in | TCA9534 INT | 10k PU to +3V3. Digital use of an ADC pin; it is never above +3V3 |
| 47 | 58 | LED_STATUS (local) | out | PWM11 B | Red status/fault LED, high = on |

**I/O expander (U1003, TCA9534 @ 0x20)**

| Port | Net | Dir | Notes |
|---|---|---|---|
| P0 | EXT_PWR_PRESENT | in | 3.3 V push-pull (74LVC1G32 on power_input), 100k PD on pd_pmg1 |
| P1 | LAPTOP_OVP_N | in | OD, 10k PU on power_laptop |
| P2 | TEMP_ALERT_N | in | TMP1075 wired-OR; **its single 10k PU (R1016) is here** |
| P3 | CR_CD_SD_N | in | Pull-up expected on card_reader |
| P4 | CR_CD_USD_N | in | Pull-up expected on card_reader |
| P5 | ETH_RESET_N | out | 10k PU here (R1017). The expander powers up as inputs, so the PHY runs without firmware. Write 0 to reset it |
| P6, P7 | spare | — | 10k PD. Candidates: UP/DS_CCPROT_FLT_N from usbc_muxes, TPS26750 EEPROM WP |

**Why an expander.** The must-have signal list needs 54 pins against 48 GPIO. The slow, level-type status signals went to
the expander. The PMG1 already reads EXT_PWR_PRESENT and LAPTOP_OVP_N and owns the safety reaction, so the RP2350 only
displays them. Interrupt-type and fast signals stay on native GPIO: both PD IRQs, buttons, LED activity, SPI and SWD.
- The optional VBUS/VIN/+5V ADC monitor was dropped: INA237 (VIN), INA226 (laptop VBUS) and INA226 (+5V) already measure
  those rails over I2C_SYS.

## Level and dead-deck review
- **The RP2350 GPIOs are FT on GPIO0–39 only.** With the deck unpowered, they take ≤ 3.63 V with negligible current.
- **Signals that can be high while +3V3 is off**, during a bus-powered cold start with the PMG1 on laptop VBUS:
  - **PDIN_PRESENT**: the TPS26750 runs from PD-in VBUS. It goes to GPIO29 (FT) with 1k series on power_input. OK.
  - **PMG1_SWDIO/SWCLK**: PMG1 internal pulls to PMG1_VDDD (3.3 V) on GPIO26/27 (FT). OK.
  - **PMG1_XRES_N**: the pass FET on pd_pmg1 already isolates it, so the RP2350 does not clamp XRES.
  - **CR_LED**: the GL3224 is on +5V, which rises before +3V3. GPIO39 (FT). OK.
  - **I2C_PD / PD IRQs**: open drain with pull-ups to +3V3, so they idle at 0 V when +3V3 is off. OK.
- **ADC pins (40–47) are not FT.**
  - USBA1/2_ISENSE pass through 10k (R1019/R1021). The INA180 output on usb_a may be live, or above 3.3 V if it is powered
    from +5V. The worst-case clamp current is < 0.2 mA.
  - NTC_ADC0/1 are passive and biased from ADC_AVDD, so they read 0 V when off.
  - HDR_ADC0/1 have 1k on display_ui.
  - IOX_INT_N is pulled to +3V3.
- **EXT_PWR_PRESENT, LAPTOP_OVP_N, TEMP_ALERT_N and CR_CD_*** are all 0–3.3 V and low or unpowered with +3V3 off, so no
  dividers are needed. The TCA9534 I/Os are 5.5 V tolerant regardless.
- **Reset state.** Every GPIO powers up as an input with a pull-down (DS table 1674). Consequences:
  - FORCE_EN is off.
  - The LCD is in reset with the backlight off.
  - HUB_SMB_PU is low, so the hub boots from ROM and the BOOTSEL UF2 still enumerates.
  - HUB_RESET_N and PMG1_XRES_N read high through their external pull-ups (a 10k or 4.7k pull-up against about 50k).
- ETH_LEDx and CR_LED may be **power-on straps** on the RTL8156BG/GL3224. The RP2350 reset pull-down (35–189k) is weak, but
  the ethernet and card_reader sheets must set any such straps with ≤ 10k.

## Power
- Total ≈ 30–60 mA at 150 MHz on +3V3 (< 0.2 W). +1V1 is generated on chip and is used only by the RP2350. The sheet carries
  the `+1V1` PWR_FLAG.
- ADC_AVDD is +3V3 through 10 Ω / 4.7 µF. It is the ADC reference, and the NTC bias hangs on it, so the NTC reading is
  ratiometric.

## USB
- The 27 Ω series resistors (R1007/R1008, extended C25100) sit at the RP2350 pins, as RPi requires. The trace runs
  differential, 90 Ω, to hub port 6.
- No VBUS detect: the device is permanently attached to the hub.

## Firmware notes
- **Buses.** I2C1 runs I2C_SYS and I2C0 runs I2C_PD, both hardware at 400 kHz. I2C_PD may run at 1 MHz.
  - The HUB SMBus and Qwiic use PIO I2C with clock stretching. The USB7206C stretches the clock before tSMBUS_RDY.
  - Both PIO pin pairs are also hardware-I2C capable, so the buses can be reassigned in firmware.
- **Hub SMBus sequence**: see `usb_hub.md` (SMB_PU high, then reset, then wait 40 ms, then config, then AA56h).
- **SWD to the PMG1**: debugprobe PIO program on GPIO26/27 plus XRES on GPIO28.
- **Ethernet LED decoding** (link speed and activity): PIO edge counters on GPIO36–39.
- **Recovery.** If firmware hangs with HUB_SMB_PU high, the hub waits forever. Fix: hold BOOTSEL and power-cycle.

## Part list (this sheet)

| Ref | Part | LCSC | Type | Stock | Qty |
|---|---|---|---|---|---|
| U1001 | RP2350B | C42415655 | ext | 3873 | 1 |
| U1002 | W25Q128JVSIQ | C97521 | basic | 49.6k | 1 |
| U1003 | TCA9534PWR | C783615 | ext | 15k | 1 |
| L1001 | AOTA-B201610S3R3-101-T 3.3 µH | C42411119 | ext | 3338 | 1 |
| Y1001 | ABM8-272-T3 12 MHz | C20625731 | ext | 13.6k | 1 |
| SW1001, SW1002 | TS-1187A-B-A-B | C318884 | basic | 474k | 2 |
| D1001 | KT-0805G green | C2297 | basic | 3.1M | 1 |
| D1002 | KT-0603R red | C2286 | basic | 4.8M | 1 |
| R1007, R1008 | 27 Ω 0402 | C25100 | ext | 57k | 2 |
| C (4.7 µF) | 4.7 µF 0402 | C23733 | basic | — | 4 |
| C (100 nF) | 100 nF 0402 | C1525 | basic | — | 17 |
| C1006 | 10 µF 0603 | C19702 | basic | — | 1 |
| C1020, C1021 | 15 pF C0G 0402 | C1548 | basic | — | 2 |
| C1024, C1025 | 10 nF 0402 | C15195 | basic | — | 2 |
| R | 10/33/330/1k/2.2k/4.7k/10k 0402 | C25077/C25105/C25104/C11702/C25879/C25900/C25744 | basic | — | 24 |
| R1004 | 10k (DNP) | C25744 | basic | — | 1 |
| J1001, TP1001–TP1004 | header and pads | — | not in BOM | — | — |

`tools/bom_check.py`: all OK.

## Nets
- Global nets used:
  - Rails and power status: `+3V3`, `+1V1`, `GND`, `EXT_PWR_PRESENT`, `PDIN_PRESENT`, `LAPTOP_OVP_N`.
  - Buses and IRQs: `I2C_SYS_*`, `I2C_PD_*`, `I2C_PD_INT_N`, `PDIN_INT_N`, `I2C_EXT_*`.
  - Hub: `HUB_SMB_CLK/DAT`, `HUB_SMB_PU`, `HUB_RESET_N`, `MCU_USB_DP/DN`.
  - PMG1 debug: `PMG1_SWDIO/SWCLK/XRES_N`.
  - Display and UI: `LCD_*`, `BTN_A_N/BTN_B_N`, `HDR_GPIO0..7`, `HDR_ADC0/1`.
  - USB-A: `USBA1/2_FORCE_EN`, `USBA1/2_ISENSE`.
  - Ethernet, card reader, sensors: `NTC_ADC0/1`, `ETH_LED0..2`, `ETH_RESET_N`, `CR_CD_SD_N`, `CR_CD_USD_N`, `CR_LED`,
    `TEMP_ALERT_N`.
- **No new inter-sheet nets are needed.**

## Requirements on other sheets
1. **sensors**: put only the NTCs (NCP18XH103, 10k B3380) from NTC_ADC0/1 to GND. The bias and filter are here. Do not add a
   TEMP_ALERT_N pull-up; R1016 is the only one.
2. **usb_a**: power the INA180A2 from **+3V3** if possible, so the output stays ≤ 3.3 V. The 10k series resistor here makes
   +5V survivable but clips readings above 3.3 V. Add a 100k pull-down on each FORCE_EN.
3. **ethernet**: ETH_RESET_N has its pull-up here, so do not add another. Any LED pin that is also a strap needs a ≤ 10k strap
   resistor.
4. **card_reader**: pull-ups on CR_CD_SD_N/CR_CD_USD_N, to +3V3 or the GL3224's 3.3 V. CR_LED must be ≤ 3.6 V.

## Open issues
1. The expander adds I2C latency for the power-status display (≤ 1 ms, interrupt-driven), which is not safety relevant. If
   layout frees pins, move EXT_PWR_PRESENT back to a native GPIO.
2. Spare expander pins P6/P7 could take UP/DS_CCPROT_FLT_N (usbc_muxes) if those are promoted to global nets.
3. The crystal and regulator footprints are LCSC imports. Check them against the RPi minimal-board KiCad files. **Copy the
   RPi regulator placement** (C6/C7/L1 geometry, inductor dot orientation).
4. The QFN-80 EP land pattern (3.4 mm EP) and paste windows need checking against the DS package drawing.
5. The 16 MB flash holds the RP2350 firmware plus component images. Check the image budget once the PMG1 image size is known
   (CYPM1321 flash 128 KB, so it is not a concern).
