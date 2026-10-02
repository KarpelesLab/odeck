"""Set the board outline (rounded rectangle) and corner mounting holes.
usage (KiCad python): set_outline.py <board.kicad_pcb> <width_mm> <height_mm> [corner_r=3] [hole_inset=4]
Origin: top-left corner at (100, 50) mm. Removes existing Edge.Cuts shapes and H1..H4 holes first."""
import sys
import pcbnew

X0, Y0 = 100.0, 50.0


def set_outline(path, W, H, R=3.0, inset=4.0):
    b = pcbnew.LoadBoard(path)
    mm = pcbnew.FromMM
    V = lambda x, y: pcbnew.VECTOR2I(mm(x), mm(y))
    holes = [fp for fp in b.GetFootprints() if fp.GetReference() in ("H1", "H2", "H3", "H4")]
    edges = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    for item in holes + edges:
        b.Remove(item)

    def seg(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(V(x1, y1)); s.SetEnd(V(x2, y2)); s.SetWidth(mm(0.1)); b.Add(s)

    def arc(cx, cy, sx, sy):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetCenter(V(cx, cy)); s.SetStart(V(sx, sy)); s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
        s.SetWidth(mm(0.1)); b.Add(s)

    seg(X0 + R, Y0, X0 + W - R, Y0); seg(X0 + W, Y0 + R, X0 + W, Y0 + H - R)
    seg(X0 + W - R, Y0 + H, X0 + R, Y0 + H); seg(X0, Y0 + H - R, X0, Y0 + R)
    arc(X0 + W - R, Y0 + R, X0 + W - R, Y0); arc(X0 + W - R, Y0 + H - R, X0 + W, Y0 + H - R)
    arc(X0 + R, Y0 + H - R, X0 + R, Y0 + H); arc(X0 + R, Y0 + R, X0, Y0 + R)
    lib = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/MountingHole.pretty"
    for i, (x, y) in enumerate([(inset, inset), (W - inset, inset), (inset, H - inset), (W - inset, H - inset)]):
        fp = pcbnew.FootprintLoad(lib, "MountingHole_3.2mm_M3_Pad_Via")
        fp.SetReference(f"H{i + 1}"); fp.Reference().SetVisible(False)
        fp.SetPosition(V(X0 + x, Y0 + y)); b.Add(fp)
    tb = b.GetTitleBlock(); tb.SetComment(1, f"Outline {W:g}x{H:g} mm (provisional)")
    b.Save(path)


if __name__ == "__main__":
    a = sys.argv
    set_outline(a[1], float(a[2]), float(a[3]), *(float(x) for x in a[4:6]))
