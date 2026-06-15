# GGate Component SVG Icon Specification

This document defines the visual design system and technical specifications for all component SVG icons in GGate. Following these specifications ensures visual consistency, crisp pixel alignment, and native Libadwaita theme compatibility (automatic light/dark mode recoloring).

---

## 1. Technical Requirements

1. **ViewBox Grid:** All component icons must use exactly `viewBox="0 0 28 28"`.
2. **Stroke/Fill Rules:**
   - Standard stroke width: `2px`.
   - Element stroke: `stroke="currentColor"`.
   - Element fill: `fill="none"` by default (or `fill="currentColor"` for solid indicator shapes/bubbles).
   - Inversion bubbles: `circle` elements with a radius of `2px` or `2.5px`, `fill="none"` or `fill="currentColor"`.
3. **Corner Treatment:** All strokes should use `stroke-linejoin="round"` and `stroke-linecap="round"` to ensure smooth connections.
4. **Theme Recoloring:** Never use hardcoded hex colors (e.g. `#000`, `#1a1a1a`, `#ffffff`) or inline CSS `style` attributes. GTK4 recolors SVG paths dynamically using `currentColor`.
5. **Text Labels:** Use the `<text>` element:
   - Font family: `sans-serif` (or monospace where appropriate).
   - Font size: `5px` to `6px`.
   - Font weight: `bold` for main component keys.
   - Text color: `fill="currentColor"`.
   - Alignment: Use `text-anchor="middle"` or `text-anchor="end"` for precise positioning.

---

## 2. Component Design Specifications

### A. Logic Gates

All standard gates occupy a horizontal span centered at `y = 14`. Input pins enter from `x = 1`, and output pins exit to `x = 27`.

#### 1. `and.svg`
- **Body:** Back line from `(9, 6)` to `(9, 22)`. Top flat line to `(16, 6)`. Bottom flat line to `(16, 22)`. Front semi-circle centered at `(16, 14)` with radius `8`.
- **Inputs:** Two lines at `y = 10` and `y = 18` from `x = 1` to `x = 9`.
- **Output:** One line at `y = 14` from `x = 24` to `x = 27`.

#### 2. `or.svg`
- **Body:** Curved back `M 9,6 C 12,10 12,18 9,22`. Top edge `M 9,6 C 14,6 20,9 24,14`. Bottom edge `M 9,22 C 14,22 20,19 24,14`.
- **Inputs:** Two lines at `y = 10` and `y = 18` from `x = 1` to the back curve (approx `x = 10`).
- **Output:** One line at `y = 14` from `x = 24` to `x = 27`.

#### 3. `not.svg`
- **Body:** Right-pointing triangle with vertices `(7, 6)`, `(7, 22)`, and `(18, 14)`.
- **Inversion Bubble:** Circle centered at `(21, 14)` with radius `2.5`.
- **Input:** Line at `y = 14` from `x = 1` to `x = 7`.
- **Output:** Line at `y = 14` from `x = 23.5` to `x = 27`.

#### 4. `xor.svg`
- **Body:** Same top, bottom, and back curves as `or.svg`. Additional back-offset curve `M 6,6 C 9,10 9,18 6,22`.
- **Inputs:** Two lines at `y = 10` and `y = 18` from `x = 1` to the first curve (approx `x = 7.5`).
- **Output:** One line at `y = 14` from `x = 24` to `x = 27`.

#### 5. `nand.svg`
- **Body & Inputs:** Same as `and.svg`.
- **Inversion Bubble:** Circle centered at `(25, 14)` with radius `2`.
- **Output:** Line at `y = 14` from `x = 27` to the bubble.

#### 6. `nor.svg`
- **Body & Inputs:** Same as `or.svg`.
- **Inversion Bubble:** Circle centered at `(25, 14)` with radius `2`.
- **Output:** Line at `y = 14` from `x = 27` to the bubble.

#### 7. `tribuff.svg` (Tri-State Buffer)
- **Body:** Right-pointing triangle with vertices `(7, 6)`, `(7, 22)`, and `(19, 14)`.
- **Inputs:** Data input line at `y = 14` from `x = 1` to `x = 7`. Control input line from `(13, 1)` to the top of the body `(13, 10)`.
- **Output:** Line at `y = 14` from `x = 19` to `x = 27`.

---

### B. Flip-Flops & Sequential Components

Flip-flops and block components use a centered rectangular frame, typically of size `16x20` (from `x = 6` to `x = 22` and `y = 4` to `y = 24`).

#### 8. `rsff.svg`
- **Body:** Rectangular frame `rect x="6" y="4" width="16" height="20" rx="1" ry="1"`.
- **Inputs:** `S` input at `y = 8` from `x = 1` to `x = 6`. `R` input at `y = 20` from `x = 1` to `x = 6`.
- **Outputs:** `Q` output at `y = 8` from `x = 22` to `x = 27`. `~Q` output at `y = 20` from `x = 22` to `x = 27`.
- **Labels:**
  - `S` at `(8, 10)`
  - `R` at `(8, 22)`
  - `Q` at `(20, 10)` (anchor: end)
  - `Q̅` at `(20, 22)` (anchor: end)

#### 9. `jkff.svg`
- **Body:** Rectangular frame `rect x="6" y="4" width="16" height="20" rx="1" ry="1"`.
- **Inputs:** `J` input at `y = 8`. `CK` input at `y = 14`. `K` input at `y = 20`.
- **Clock Triangle:** Inward-pointing wedge `M 6,11 L 9,14 L 6,17`.
- **Outputs:** `Q` output at `y = 8`. `~Q` output at `y = 20`.
- **Labels:**
  - `J` at `(8, 10)`
  - `K` at `(8, 22)`
  - `Q` at `(20, 10)` (anchor: end)
  - `Q̅` at `(20, 22)` (anchor: end)

#### 10. `dff.svg`
- **Body:** Rectangular frame `rect x="6" y="4" width="16" height="20" rx="1" ry="1"`.
- **Inputs:** `D` input at `y = 8`. `CK` input at `y = 20`.
- **Clock Triangle:** Inward-pointing wedge `M 6,17 L 9,20 L 6,23`.
- **Outputs:** `Q` output at `y = 8`. `~Q` output at `y = 20`.
- **Labels:**
  - `D` at `(8, 10)`
  - `Q` at `(20, 10)` (anchor: end)
  - `Q̅` at `(20, 22)` (anchor: end)

#### 11. `tff.svg`
- **Body & Outputs:** Same as `dff.svg`.
- **Inputs:** Clock input at `y = 14`.
- **Clock Triangle:** Inward-pointing wedge `M 6,11 L 9,14 L 6,17`.
- **Labels:**
  - `T` centered at `(14, 17)` (larger font size).
  - `Q` at `(20, 10)` (anchor: end)
  - `Q̅` at `(20, 22)` (anchor: end)

---

### C. Registers & Complex Block Components

Registers use a wider rectangular box `18x20` (from `x = 5` to `x = 23` and `y = 4` to `y = 24`) and centered text labels.

#### 12. `7seg.svg` (Seven-Segment Display)
- **Body:** Outer rectangular frame `rect x="6" y="3" width="16" height="22" rx="1.5" ry="1.5"`.
- **Digit Segments:** Seven individual `line` elements of width `2px` with a flat `butt` linecap, separated by 1px gaps, forming the digit "8".
- **Decimal Point:** A filled circle `circle cx="20.5" cy="23" r="1"`.

#### 13. `counter.svg` (Mod-N Counter)
- **Body:** Rectangular frame `rect x="5" y="4" width="18" height="20" rx="1"`.
- **Labels:** Center-aligned text `"CTR"` at `(14, 14)`.

#### 14. `adder.svg` (Arithmetic Adder)
- **Body:** Rectangular frame `rect x="5" y="4" width="18" height="20" rx="1"`.
- **Labels:** Center-aligned text `"\u03a3"` (Sigma symbol) at `(14, 14)` with large font size.

#### 15. `siso.svg`, `sipo.svg`, `piso.svg`, `pipo.svg`
- **Body:** Rectangular frame `rect x="5" y="4" width="18" height="20" rx="1"`.
- **Labels:** Center-aligned text (e.g. `"SISO"`, `"SIPO"`, `"PISO"`, `"PIPO"`) at `(14, 14)`.

---

### D. Input, Output & Infrastructure Components

#### 16. `sw.svg` (Switch)
- Lever switch symbol:
  - Input connection dot: `circle cx="6" cy="14" r="1.5"`.
  - Output connection dot: `circle cx="22" cy="14" r="1.5"`.
  - Input stub: `line x1="1" y1="14" x2="6" y2="14"`.
  - Lever: `line x1="6" y1="14" x2="20" y2="6"`.
  - Output stub: `line x1="22" y1="14" x2="27" y2="14"`.

#### 17. `led.svg` (LED Indicator)
- **Body:** Rectangular frame `rect x="9" y="5" width="18" height="18" rx="1.5" ry="1.5"`.
- **Emitter Circle:** Centered at `(18, 14)` with radius `4.5`.
- **Input Stub:** Line at `y = 14` from `x = 1` to `x = 9`.

#### 18. `vdd.svg` (Power Source)
- Upward-pointing arrow:
  - Vertical connection line from `(14, 27)` to `(14, 6)`.
  - Arrow head lines: `M 8,12 L 14,6 L 20,12`.
  - Text label `"Vdd"` starting at `(17, 18)` (to the right of the vertical line).

#### 19. `gnd.svg` (Ground)
- Ground schematic symbol:
  - Vertical connection line from `(14, 1)` to `(14, 14)`.
  - First bar: `line x1="5" y1="14" x2="23" y2="14"`.
  - Second bar: `line x1="9" y1="18" x2="19" y2="18"`.
  - Third bar: `line x1="13" y1="22" x2="15" y2="22"`.

#### 20. `osc.svg` (Clock Oscillator)
- Rectangular enclosure: `rect x="3" y="5" width="22" height="18" rx="3"`.
- Enclosed square wave path: `M 6,17 L 10,17 L 10,11 L 15,11 L 15,17 L 19,17 L 19,11 L 22,11`.

#### 21. `probe.svg` (Voltage Probe)
- Outer indicator circle: `circle cx="16" cy="14" r="8"`.
- Center active probe dot: `circle cx="16" cy="14" r="2.5" fill="currentColor"`.
- Probe lead stub: `line x1="1" y1="14" x2="8" y2="14"`.

#### 22. `text.svg` (Text Box Label)
- Letter icon:
  - Stylized uppercase text letter `"A"` centered at `(14, 19)` with a font size of `18px`, `font-family="serif"`, and `font-weight="bold"`.
