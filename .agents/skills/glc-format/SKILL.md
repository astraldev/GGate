---
name: glc-format
description: Use when reading, writing, or programmatically generating GGate logic-circuit (`.glc`) files, or troubleshooting their load/save.
---

# GGate GLC Circuit File Format

`.glc` is GGate's plain-text logic-circuit format: it lists the components, their
placement and initial state, and the wires between them. This skill is enough to
author or parse a `.glc` file by hand.

**Core principle:** Wires connect *geometrically*. A `net` segment joins to a
component pin, or to another net, wherever their endpoint coordinates coincide —
there are no ids. Property values containing structural characters must be escaped.

## Decision flow

| Task | What to do |
|------|------------|
| Declare file version/compatibility | Add a `version` section (first) |
| Place a component | Section whose header is the component type key |
| Connect pins electrically | Add `net` segment(s) whose endpoints match pin coordinates |
| Put `= , : \` inside a text/name value | Escape it (`\e \c \s \\`) |

## File shape

- Plain **UTF-8 text**.
- A file is a list of **sections** separated by a blank line (`\n\n`).
- Each section is:
  - a **header line** — the section type, no leading space; then
  - zero or more **attribute lines** `key=v1,v2,...` (a single leading space is
    optional and ignored).
- An attribute line is split into exactly two parts on the first `=`, and the value
  is split on `,`. **Keys and raw values must not contain unescaped `=` or `,`.**
- The first section should be `version`; component and `net` sections follow in any order.

## `version` section

```
version
 author=5.0.0
 required=2.6.0
```

- `author` — the GGate version that wrote the file.
- `required` — the minimum GGate version needed to open it; if the opening app is
  older, the load is rejected. Safe defaults: `author=5.0.0`, `required=2.6.0`.

## Component sections

The header is a **component type key** (see catalog). Attributes:

| key | meaning | format |
|-----|---------|--------|
| `position` | top-left placement on the canvas | `x,y` (integers, grid units) |
| `input_level` | initial logic level of each **input** pin | `0`/`1` per pin; empty if none |
| `output_level` | initial logic level of each **output** pin | `0`/`1` per pin; empty if none |
| `matrix` | 2×2 orientation transform `a,b,c,d` | identity = `1,0,0,1` |
| `properties` | component settings | `name:value,name:value,...` |

- `input_level`/`output_level` have one entry per input/output pin; leave empty for
  components that have none (e.g. a source has no inputs, a probe has no outputs). The
  simulator overwrites these once it runs.
- `matrix` is the rotation/flip. `1,0,0,1` is upright; 90°/180°/270° and flips are the
  usual 2×2 integer matrices.
- `properties` are `name:value` pairs; `name` must be one of the component's property
  names (catalog below). The value is unescaped, then interpreted as that property's
  type (integer / float / select-index / boolean / string). Unknown names are ignored.

## `net` sections (wires)

```
net
 position=540,290,410,290
```

- `position` = `x1,y1,x2,y2` — one straight wire segment between two points.
- Connectivity is geometric: route a `net` segment so its endpoint lands exactly on a
  pin's coordinate to connect it; segments that share an endpoint are the same net.

## Encoding (property values only)

`=` `,` `:` and `\` are structural, so they are escaped inside property **values** on
write and restored on read:

| character | stored as |
|-----------|-----------|
| `\` | `\\` |
| `,` | `\c` |
| `=` | `\e` |
| `:` | `\s` |

Example: the label `T=0.25µs` is stored as `text:T\e0.25µs`. Values must stay on one
line (newlines are not escaped).

## Component catalog

Type keys and their property names. `tphl`/`tplh` are the high→low / low→high
propagation delays (µs). Select-index properties store the chosen option's index.

| key | properties |
|-----|------------|
| `not` | `tphl, tplh` |
| `and`, `or`, `nand`, `nor`, `xor` | `inputs` (2 or 3), `tphl, tplh` |
| `tribuff` | `active`, `inverted` (select-indexes) |
| `sw` | `initstate` (0/1) |
| `osc` | `period`, `shift`, `duration` (µs), `initstate` (0/1) |
| `probe` | `name` (string; labels the signal in the timing graph) |
| `text` | `text` (string label, not simulated) |
| `led`, `7seg` | color select-index (`0`=Red, `1`=Blue, `2`=Green, `3`=Yellow) |
| `vdd`, `gnd` | (none) |
| `rsff` | `tphl, tplh` |
| `dff`, `jkff`, `tff` | `trig` (`0`=positive edge, `1`=negative), `tphl, tplh` |
| `counter` | `n`, `bits`, `trig`, `tphl, tplh` |
| `adder` | `halffull` (`0`=half, `1`=full), `tphl, tplh` |
| `siso`, `sipo`, `piso`, `pipo` | `bits`, `trig`, `tphl, tplh` |
| `net` | `position=x1,y1,x2,y2` only |

## Worked example

A source oscillator wired to a probe:

```
version
 author=5.0.0
 required=2.6.0

osc
 position=340,260
 input_level=
 output_level=0
 matrix=1,0,0,1
 properties=period:2.5,shift:0.0,duration:80.0,initstate:0

probe
 position=530,250
 input_level=0
 output_level=
 matrix=1,0,0,1
 properties=name:Signal1

net
 position=540,290,410,290
```

## Gotchas

- Separate sections with exactly one blank line; the file ends without a trailing blank line.
- Each attribute line must split into exactly two parts on `=` — escape any structural
  character in values.
- Wire endpoints must land exactly on pin coordinates, or the connection isn't made.
- Parsing is lenient: unknown sections/properties are skipped, so a malformed file loads
  partially instead of erroring.
