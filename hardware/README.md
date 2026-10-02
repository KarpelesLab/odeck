# Hardware

KiCad 10 projects.

- `odeck-10/` — 10 Gbps prototype (see `../docs/odeck-10.md`, `../docs/board-layout.md`)
  - Hierarchical schematic: one sheet per block (power input, laptop power out, rails, PD controller,
    USB-C muxes & DP, USB hub, USB-A, Ethernet, card reader, MCU, display & UI, sensors)
  - PCB: JLC061611-1080A 6-layer stackup, 110 × 75 mm provisional outline, JLC design rules, net classes
- `lib/` — shared project symbol/footprint libraries (`odeck.kicad_sym`, `odeck.pretty`), referenced via
  each project's `sym-lib-table` / `fp-lib-table`. Parts from LCSC can be imported with `easyeda2kicad`.

CLI checks:

```sh
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K sch erc odeck-10/odeck-10.kicad_sch
$K pcb drc odeck-10/odeck-10.kicad_pcb
```
