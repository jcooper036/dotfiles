---
name: erd-diagram
description: Draw a presentation-grade entity-relationship diagram — tables, columns, keys, crow's-foot cardinality — as SVG rendered to PNG for slides and design docs. Reads the schema out of the live database, lays boxes on a fixed grid, and routes orthogonal edges in the gutters.
when_to_use: Someone asks for an ERD, a data-model diagram, a schema picture, or "a graphic showing how X relates to Y" for a deck or a doc. Also when a design discussion needs the real shape of the tables rather than prose about them.
---

# ERD diagram

## Read the schema out of the database, never out of the design docs

The diagram's only value is that it is true. Design docs describe intent and drift from the
tables; a diagram drawn from one inherits the drift and looks authoritative anyway. Introspect
first, read the docs afterwards only to learn which tables carry the argument.

```sql
select c.table_name, c.ordinal_position, c.column_name, c.data_type, c.is_nullable
from information_schema.columns c
where c.table_schema = 'public' and c.table_name in (...)
order by c.table_name, c.ordinal_position;

select conrelid::regclass || ' ' || pg_get_constraintdef(oid)
from pg_constraint
where contype = 'f' and connamespace = 'public'::regnamespace
order by 1;
```

`information_schema.constraint_column_usage` returns nothing useful for composite keys — use
`pg_constraint`. Column *order* comes from the live table too, and gaps in `ordinal_position`
are dropped columns, not an error.

If no database is reachable, say so before drawing and fall back to the ORM models or migrations
— then tell the reader which source the picture came from.

## The diagram argues one thing

Start from the question it has to answer, then keep only the tables that carry it. Ten to fifteen
boxes is the working range; past that the eye gives up and the argument is lost in the routing.

**The join tables that answer the question get `accent=True` and the `red` palette.** If the point
is "which structures may a protein be analyzed against", then `structure_protein_relatability` is
the subject of the picture and everything else is context. Two or three accents, never more.

A missing edge is often the argument: `structures` has no FK to `proteins` at all, and that
absence is the whole reason the relatability table exists. Say it in the layout, not in a label.

## Text in the image is table names and column names only

No titles, no captions, no annotations, no legend. The deck or the doc carries the interpretation
— prose baked into a PNG cannot be edited by the person presenting it. Ask before adding any word
that is not an identifier from the schema.

## Layout is a fixed grid, edges are orthogonal and routed in the gutters

`cols` and `rows` are dicts of index → pixel origin. Pitch = `box_w` + a gutter of ~45px; the
gutter is where vertical lanes live. Bands between rows are where horizontal lanes live.

- Prefer a **straight** link to a routed one. `d.straight(child, field, parent)` draws a
  horizontal edge at the field's own row height — use it whenever the parent box spans that y.
- A path that leaves the child rightward and then turns back left **hides its own marker** under
  the crow's foot. If a link needs to backtrack, re-anchor it to a different edge instead.
- Never route over a box. Pick a lane x strictly inside a gutter and a lane y strictly inside a
  band, then check the render.
- Long wraps around the outside of the canvas are fine and often better than a crossing — the
  "over the top" lane is a legitimate move.
- Two FKs from one table to the same parent, drawn as two parallel verticals, is the clearest way
  to show a role distinction (`analysis_protein_id` vs `hit_experiment_protein_id`).

## Visual grammar

| mark | meaning |
|---|---|
| filled square | primary key (or a unique business key) |
| hollow circle | foreign key, stroked in the **referenced** table's color |
| crow's foot | the many end — always at the child |
| single bar | the one end — always at the parent |
| thick border | this table is the argument |

Because an FK dot is colored by what it points at, an FK whose edge you chose not to draw is
still traceable. **Do not draw every FK.** Draw the ones that carry the argument; let
`cache_key` and `data_layer_id` live as grey dots.

Palettes are per cluster, not per table — one color for the spine, one for structures, one for
ligands, one for results. Available: `indigo teal amber purple slate red green grey`.

## Render, then look at it

```bash
python spec.py out.svg
rsvg-convert -w 1700 out.svg -o preview.png    # read this, fix overlaps, repeat
rsvg-convert -w 4320 out.svg -o final.png      # ship 4320px for slides
```

Read the preview PNG every iteration — marker direction, box overflow and lane collisions are
invisible in the source and obvious in the render. To inspect a crowded region:

```bash
rsvg-convert -z 1.6 --page-width 1400 --page-height 900 --left=-1120 --top=-140 out.svg -o crop.png
```

Ship two PNGs, white background and transparent (`Diagram(background=None)`), and keep the spec
next to them — the next revision is an edit, not a redraw.

## Files

- `scripts/erd.py` — `Diagram`, the palettes, and the SVG writer. Font sizes auto-shrink to the
  box, so a long table name is a layout question and not a clipping bug.
- `reference/example_proteus.py` — a worked 13-table spec with every routing move in it. Copy it
  and replace the tables.
