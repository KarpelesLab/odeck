#!/bin/sh
# Import LCSC parts (symbol + footprint + 3D model) into hardware/lib via easyeda2kicad,
# then make 3D paths project-relative and upgrade files to the current KiCad format.
# usage: tools/import_lcsc.sh C2870250 [C123 ...]
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIB="$ROOT/hardware/lib"
E2K="${E2K:-$HOME/.venvs/odeck/bin/easyeda2kicad}"
KCLI="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
cd "$LIB"
# serialize concurrent imports (several agents/scripts may run at once)
while ! mkdir "$LIB/.lock" 2>/dev/null; do sleep 1; done
trap 'rmdir "$LIB/.lock"' EXIT INT TERM
"$E2K" --full --overwrite --output "$LIB/odeck" --lcsc_id "$@"
# absolute 3D model paths -> relative to the project dir (projects live in hardware/<name>/)
sed -i '' "s#$LIB/odeck.3dshapes/#\${KIPRJMOD}/../lib/odeck.3dshapes/#g" odeck.pretty/*.kicad_mod
"$KCLI" sym upgrade --force odeck.kicad_sym >/dev/null
"$KCLI" fp upgrade odeck.pretty >/dev/null 2>&1 || true
