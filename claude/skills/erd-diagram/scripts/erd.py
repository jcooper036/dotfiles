from dataclasses import dataclass, field
from pathlib import Path

PALETTES: dict[str, tuple[str, str]] = {
    "indigo": ("#3C56A5", "#EDF0FA"),
    "teal": ("#1F7A6B", "#E8F4F1"),
    "amber": ("#B0722A", "#FAF0E3"),
    "purple": ("#7B4E9E", "#F3EDF9"),
    "slate": ("#46586E", "#EDF0F4"),
    "red": ("#BC3B2E", "#FBEBE9"),
    "green": ("#4A7C2F", "#EEF5E8"),
    "grey": ("#8A93A0", "#F1F2F4"),
}

EDGE_COLOR = "#6E7684"

DEFS = """<defs>
<style>
 .tn { font: 700 25px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #ffffff; letter-spacing: .2px }
 .cn { font: 400 21px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #2B3038 }
 .ck { font: 600 21px 'Helvetica Neue', Helvetica, Arial, sans-serif; fill: #2B3038 }
</style>
<marker id="many" viewBox="0 0 16 18" refX="16" refY="9" markerWidth="12" markerHeight="13.5" orient="auto">
  <path d="M16,9 L0,0 M16,9 L0,18 M16,9 L0,9" fill="none" stroke="%(edge)s" stroke-width="1.9"/>
</marker>
<marker id="one" viewBox="0 0 10 18" refX="7" refY="9" markerWidth="7.5" markerHeight="13.5" orient="auto">
  <path d="M7,1 L7,17" fill="none" stroke="%(edge)s" stroke-width="2.4"/>
</marker>
<filter id="sh" x="-20%%" y="-20%%" width="140%%" height="140%%">
  <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#1B2430" flood-opacity="0.13"/>
</filter>
</defs>""" % {"edge": EDGE_COLOR}


@dataclass
class Column:
    name: str
    kind: str = ""
    ref: str | None = None


@dataclass
class Table:
    name: str
    col: int
    row: int
    palette: str
    columns: list[Column]
    accent: bool = False


@dataclass
class Diagram:
    cols: dict[int, float]
    rows: dict[int, float]
    width: float
    height: float
    box_w: float = 370
    row_h: float = 28
    hdr_h: float = 46
    pad: float = 12
    background: str | None = "#FFFFFF"
    tables: dict[str, Table] = field(default_factory=dict)
    paths: list[str] = field(default_factory=list)

    def add(self, name: str, col: int, row: int, palette: str,
            columns: list[tuple], accent: bool = False) -> None:
        self.tables[name] = Table(
            name, col, row, palette,
            [c if isinstance(c, Column) else Column(*c) for c in columns], accent)

    def geom(self, name: str) -> tuple[float, float, float, float]:
        t = self.tables[name]
        h = self.hdr_h + len(t.columns) * self.row_h + self.pad
        return self.cols[t.col], self.rows[t.row], self.box_w, h

    def row_y(self, name: str, field_name: str) -> float:
        _, y, _, _ = self.geom(name)
        names = [c.name for c in self.tables[name].columns]
        return y + self.hdr_h + names.index(field_name) * self.row_h + self.row_h / 2

    def port(self, name: str, side: str, at: float | None = None) -> tuple[float, float]:
        x, y, w, h = self.geom(name)
        if side == "L":
            return x, at if at is not None else y + h / 2
        if side == "R":
            return x + w, at if at is not None else y + h / 2
        if side == "T":
            return at if at is not None else x + w / 2, y
        return at if at is not None else x + w / 2, y + h

    def edge(self, points: list[tuple[float, float]], dash: bool = False) -> None:
        d = "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in points)
        da = ' stroke-dasharray="7 6"' if dash else ""
        self.paths.append(
            f'<path d="{d}" fill="none" stroke="{EDGE_COLOR}" stroke-width="2"{da} '
            f'marker-start="url(#many)" marker-end="url(#one)"/>')

    def link(self, child: str, field_name: str, target: tuple[float, float],
             mids: tuple = (), side: str = "R", gap: float = 13) -> None:
        cx, cy, cw, ch = self.geom(child)
        y = self.row_y(child, field_name)
        start = (cx + cw + gap, y) if side == "R" else (cx - gap, y)
        self.edge([start, *mids, target])

    def straight(self, child: str, field_name: str, parent: str,
                 side: str = "R", gap: float = 13) -> None:
        y = self.row_y(child, field_name)
        px, py, pw, ph = self.geom(parent)
        target = (px - gap, y) if side == "R" else (px + pw + gap, y)
        self.link(child, field_name, target, side=side, gap=gap)

    def _table_svg(self, t: Table) -> list[str]:
        hdr, fill = PALETTES[t.palette]
        x, y, w, h = self.geom(t.name)
        out = [
            f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
            f'fill="{fill}" stroke="{hdr}" stroke-width="{3 if t.accent else 1.5}"/></g>',
            f'<path d="M{x},{y + self.hdr_h} L{x},{y + 10} A10,10 0 0 1 {x + 10},{y} '
            f'L{x + w - 10},{y} A10,10 0 0 1 {x + w},{y + 10} L{x + w},{y + self.hdr_h} Z" fill="{hdr}"/>',
        ]
        fs = min(25, (w - 36) / (len(t.name) * 0.575))
        out.append(f'<text class="tn" x="{x + 18}" y="{y + 31}" font-size="{fs:.1f}px">'
                   f'{_esc(t.name)}</text>')
        for i, c in enumerate(t.columns):
            cy = y + self.hdr_h + i * self.row_h + self.row_h / 2
            ty = cy + 7
            cls = "ck" if c.kind else "cn"
            ref_color = PALETTES[c.ref][0] if c.ref else PALETTES["grey"][0]
            if "pk" in c.kind or c.kind == "uq":
                out.append(f'<rect x="{x + 16}" y="{cy - 5.5}" width="11" height="11" rx="2.5" fill="{hdr}"/>')
            elif "fk" in c.kind:
                out.append(f'<circle cx="{x + 21.5}" cy="{cy}" r="5.5" fill="none" '
                           f'stroke="{ref_color}" stroke-width="2.6"/>')
            tx = x + 38
            if "pk" in c.kind and "fk" in c.kind:
                out.append(f'<circle cx="{x + 38}" cy="{cy}" r="5.5" fill="none" '
                           f'stroke="{ref_color}" stroke-width="2.6"/>')
                tx = x + 53
            cfs = min(21, (x + w - 16 - tx) / (len(c.name) * 0.545))
            out.append(f'<text class="{cls}" x="{tx}" y="{ty}" font-size="{cfs:.1f}px">'
                       f'{_esc(c.name)}</text>')
            if i < len(t.columns) - 1:
                out.append(f'<line x1="{x + 14}" y1="{cy + self.row_h / 2}" x2="{x + w - 14}" '
                           f'y2="{cy + self.row_h / 2}" stroke="{hdr}" stroke-opacity="0.16" stroke-width="1"/>')
        return out

    def to_svg(self) -> str:
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
                 f'height="{self.height}" viewBox="0 0 {self.width} {self.height}">', DEFS]
        if self.background:
            parts.append(f'<rect width="{self.width}" height="{self.height}" fill="{self.background}"/>')
        parts.extend(self.paths)
        for t in self.tables.values():
            parts.extend(self._table_svg(t))
        parts.append("</svg>")
        return "\n".join(parts)

    def write(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.to_svg())
        return p


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;")
