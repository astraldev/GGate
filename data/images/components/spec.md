# GGate Component SVG Icon Specification

This document defines the visual design system and technical specifications for all component SVG icons in GGate. Following these specifications ensures visual consistency, crisp pixel alignment, and native Libadwaita theme compatibility (automatic light/dark mode recoloring).

---

## 1. Technical Requirements

1. **ViewBox Grid:** All component icons must use exactly `viewBox="0 0 28 28"`. No `width` or `height` attributes on `<svg>`.
2. **Stroke/Fill Rules:**
   - Standard stroke width: `2px`. Secondary detail lines may use `1.5px`. Bold cross-lines (e.g. adder "+") may use `2.5px`.
   - Element stroke: `stroke="currentColor"`.
   - Element fill: `fill="none"` by default; `fill="currentColor"` only for solid dots/indicators/inversion bubbles.
3. **Corner Treatment:** All strokes use `stroke-linejoin="round"` and `stroke-linecap="round"`. Use `stroke-linecap="butt"` only on seven-segment display segments where clean rectangular ends are required.
4. **Theme Recoloring:** Never use hardcoded hex colors (`#000`, `#fff`, etc.) or inline `style=` attributes. GTK4 recolors dynamically using `currentColor`.
5. **Pictorial Glyphs — No Tiny Text Labels:** The sidebar already displays each component's name as a text label next to the icon. Icons must NOT attempt to spell out the part name in small text. All icons use pictorial line-art glyphs. Avoid `<text>` elements with `font-size` below `~10px` — they are illegible at 22px display size. The only permitted `<text>` elements are large single-letter glyphs (e.g. `font-size="11"` for "D" or "T" in flip-flops, `font-size="18"` for "A" in text.svg).
6. **Allowed Elements:** `<path>`, `<rect>`, `<circle>`, `<line>`, `<text>`. Keep markup minimal.

---

## 2. Body Dimensions (enforce consistency)

| Component class | Body rect | Pin stub length |
|-----------------|-----------|-----------------|
| Flip-flops (dff, jkff, rsff, tff) | `x=6 y=4 width=16 height=20 rx=1` | 5 units (`x=1`→`x=6` in; `x=22`→`x=27` out) |
| Block components (adder, counter, siso/sipo/piso/pipo) | `x=5 y=4 width=18 height=20 rx=1` | 4 units (`x=1`→`x=5` in; `x=23`→`x=27` out) |
| 7seg display | `x=8 y=3 width=16 height=22 rx=1.5` | 7 units (`x=1`→`x=8`) |

---

## 3. Component Design Specifications

### A. Logic Gates

All standard gates occupy a horizontal span centered at `y = 14`. Input pins enter from `x = 1`, output pins exit to `x = 27`.

#### 1. `and.svg`
- **Body:** Back line from `(9, 6)` to `(9, 22)`. Top/bottom flat lines to `(16, 6)` / `(16, 22)`. Front semi-circle centered at `(16, 14)` radius `8`.
- **Inputs:** Two lines at `y = 10` and `y = 18` from `x = 1` to `x = 9`.
- **Output:** One line at `y = 14` from `x = 24` to `x = 27`.

#### 2. `or.svg`
- **Body:** Curved back `M 9,6 C 12,10 12,18 9,22`. Top/bottom curves meeting at `(24, 14)`.
- **Inputs:** Two lines at `y = 10` and `y = 18` from `x = 1` to ~`x = 10.5`.
- **Output:** One line at `y = 14` from `x = 24` to `x = 27`.

#### 3. `not.svg`
- **Body:** Right-pointing triangle vertices `(7, 6)`, `(7, 22)`, `(18, 14)`.
- **Inversion Bubble:** `circle cx="21" cy="14" r="2.5"`.
- **Input:** `y = 14` from `x = 1` to `x = 7`.
- **Output:** `y = 14` from `x = 23.5` to `x = 27`.

#### 4. `xor.svg`
- Same as `or.svg` plus extra back-offset curve `M 6,6 C 9,10 9,18 6,22`. Inputs shorten to ~`x = 7.5`.

#### 5. `nand.svg`
- Same body as `and.svg` (shifted left by 1). Inversion bubble `circle cx="24.5" cy="14" r="1.5"`.

#### 6. `nor.svg`
- Same body as `or.svg` (shifted left by 1). Inversion bubble `circle cx="24.5" cy="14" r="1.5"`.

#### 7. `tribuff.svg` (Tri-State Buffer)
- **Body:** Right-pointing triangle `(7, 6)`, `(7, 22)`, `(19, 14)`.
- **Inputs:** Data at `y = 14` from `x = 1`; control from `(13, 1)` to `(13, 10)`.
- **Output:** `y = 14` from `x = 19` to `x = 27`.

---

### B. Flip-Flops

All flip-flops use body `rect x="6" y="4" width="16" height="20" rx="1"`. Input stubs run from `x=1` to `x=6`; output stubs from `x=22` to `x=27`. Clock-edge triangles point inward from the left wall. The combination of pin count, clock triangle position, and interior glyph distinguishes each type. Sidebar text labels provide the definitive name.

#### 8. `dff.svg` — D Flip-Flop
- **Inputs:** D at `y = 8`; clock at `y = 20`.
- **Clock triangle:** `M 6,17 L 9,20 L 6,23` (at bottom-left, matching the clock pin at `y=20`).
- **Outputs:** Q at `y = 8`; ~Q at `y = 20`.
- **Interior glyph:** Large `<text font-size="11" font-weight="bold">"D"` centered at `(14, 18)`.

#### 9. `jkff.svg` — JK Flip-Flop
- **Inputs:** J at `y = 8`; clock at `y = 14`; K at `y = 20`. Three left stubs.
- **Clock triangle:** `M 6,11 L 9,14 L 6,17` (at middle-left).
- **Outputs:** Q at `y = 8`; ~Q at `y = 20`.
- **Interior glyph:** Filled dot `circle r="1.5" fill="currentColor"` on the J pin (`cx=7 cy=8`) and K pin (`cx=7 cy=20`) — visually marks the two data inputs without text.

#### 10. `rsff.svg` — RS Flip-Flop (latch)
- **Inputs:** S at `y = 8`; R at `y = 20`. Two left stubs, no clock triangle.
- **Outputs:** Q at `y = 8`; ~Q at `y = 20`.
- **Interior glyph:** Two diagonal lines `M 10,9 L 18,14` and `M 10,19 L 18,14` (`stroke-width="1.5"`) converging rightward — suggests cross-coupled NOR/NAND latch structure.

#### 11. `tff.svg` — T Flip-Flop
- **Inputs:** Clock at `y = 14` only. One left stub.
- **Clock triangle:** `M 6,11 L 9,14 L 6,17` (at middle-left).
- **Outputs:** Q at `y = 8`; ~Q at `y = 20`.
- **Interior glyph:** Large `<text font-size="11" font-weight="bold">"T"` centered at `(15, 18)`.

---

### C. Block Components

All use body `rect x="5" y="4" width="18" height="20" rx="1"`. Pins at `x=1`/`x=27` with 4-unit stubs.

#### 12. `adder.svg` — Arithmetic Adder
- **Pins:** 2 inputs (`y = 9`, `y = 19`); 2 outputs (`y = 9`, `y = 19`).
- **Interior glyph:** Bold "+" — vertical `line x1="14" y1="8" x2="14" y2="20"` and horizontal `line x1="8" y1="14" x2="20" y2="14"`, both `stroke-width="2.5"`.

#### 13. `counter.svg` — Mod-N Counter
- **Pins:** 2 inputs (`y = 9`, `y = 19`); 2 outputs (`y = 9`, `y = 19`).
- **Interior glyph:** Ascending staircase polyline `M 8,20 L 8,17 L 11,17 L 11,13 L 15,13 L 15,9 L 20,9` — implies counting/incrementing.

#### 14. `siso.svg` — Serial-In Serial-Out
- **Pins:** 1 serial input (`y = 14` left); 1 serial output (`y = 14` right).
- **Interior glyph:** Right-arrow — horizontal stem `M 9,14 L 16,14` plus chevron arrowhead `M 13,10 L 17,14 L 13,18`.

#### 15. `sipo.svg` — Serial-In Parallel-Out
- **Pins:** 1 serial input (`y = 14` left); 3 parallel outputs (`y = 8`, `y = 14`, `y = 20` right).
- **Interior glyph:** Same right-arrow as siso.

#### 16. `piso.svg` — Parallel-In Serial-Out
- **Pins:** 3 parallel inputs (`y = 8`, `y = 14`, `y = 20` left); 1 serial output (`y = 14` right).
- **Interior glyph:** Same right-arrow as siso.

#### 17. `pipo.svg` — Parallel-In Parallel-Out
- **Pins:** 3 parallel inputs (`y = 8`, `y = 14`, `y = 20` left); 3 parallel outputs (`y = 8`, `y = 14`, `y = 20` right).
- **Interior glyph:** Same right-arrow as siso.

The 1-stub vs 3-stub pin pattern is the primary visual differentiator between shift register types. The sidebar text label is the definitive identifier.

---

### D. Display, Input/Output & Infrastructure Components

#### 18. `7seg.svg` — Seven-Segment Display
- **Enclosure:** `rect x="8" y="3" width="16" height="22" rx="1.5"`.
- **Input pins:** 4 on left at `y = 6`, `y = 11`, `y = 16`, `y = 21`, each from `x=1` to `x=8`.
- **Segments:** Seven `<line>` elements, `stroke-width="2.5"`, `stroke-linecap="butt"`, forming digit "8":
  - Top horizontal: `x=13`–`x=20` at `y=6`.
  - Upper-left vertical: `x=12` from `y=7.5` to `y=12.5`.
  - Upper-right vertical: `x=21` from `y=7.5` to `y=12.5`.
  - Middle horizontal: `x=13`–`x=20` at `y=14`.
  - Lower-left vertical: `x=12` from `y=15.5` to `y=20.5`.
  - Lower-right vertical: `x=21` from `y=15.5` to `y=20.5`.
  - Bottom horizontal: `x=13`–`x=20` at `y=22`.
- **Decimal point:** `circle cx="23" cy="22.5" r="1.2" fill="currentColor"`.

#### 19. `vdd.svg` — Power Supply (VDD)
- **Vertical stem:** `line x1="14" y1="27" x2="14" y2="9"` (connection point at bottom).
- **Arrowhead chevron:** `M 7,16 L 14,9 L 21,16` pointing upward.
- **Power rail bar:** `line x1="7" y1="6" x2="21" y2="6" stroke-width="2.5"` at top.
- No text label — the upward arrow + top bar is a universally recognized power symbol.

#### 20. `gnd.svg` — Ground (unchanged)
- Vertical line `(14, 1)` to `(14, 14)`. Three narrowing horizontal bars at `y=14` (full), `y=18` (medium), `y=22` (narrow).

#### 21. `osc.svg` — Clock Oscillator (unchanged)
- Rounded-rect enclosure `x="3" y="5" width="22" height="18" rx="3"`.
- Square-wave path inside: `M 6,17 L 10,17 L 10,11 L 15,11 L 15,17 L 19,17 L 19,11 L 22,11`.
- Output stub `x=25` to `x=27` at `y=14`.

#### 22. `probe.svg` — Voltage Probe (unchanged)
- Outer circle `cx="16" cy="14" r="8"`. Center filled dot `r="3"`. Lead stub `x=1` to `x=8` at `y=14`.

#### 23. `sw.svg` — Switch (unchanged)
- Two filled contact dots. Lever line from `(6, 14)` to `(20, 6)`. Input/output stubs.

#### 24. `led.svg` — LED Indicator (unchanged)
- Rect enclosure `x="9" y="5" width="18" height="18" rx="1.5"`. Inner circle `cx="18" cy="14" r="4.5"`. Input stub at `y=14`.

#### 25. `text.svg` — Text Label Component (unchanged)
- Large serif `<text font-size="18" font-weight="bold">"A"` centered at `(14, 20)`. No enclosure — the letter is the icon.
