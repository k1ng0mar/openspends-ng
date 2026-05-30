# Design System: OpenSpends NG — The Institutional Broadsheet

## 1. Visual Theme & Atmosphere

**Neo-Brutalist Journalism.** The interface evokes the authority of a high-end financial broadsheet combined with the raw transparency of a digital audit ledger. The aesthetic is intentionally "unrefined" in its structural honesty — heavy hairline borders, monospaced data readouts, and a restricted "Paper and Ink" palette.

**Density Tier:** Cockpit Dense (9/10) — Policy analysts and journalists require high-density information without decorative distraction.

**Variance Tier:** Predictable Symmetric (2/10) — The grid is strict, columnar, and rigorous. No asymmetric flourishes.

**Motion Tier:** Static Restrained (1/10) — This is a public record. Motion draws attention; data should speak for itself. No perpetual micro-interactions.

**The Emotional Response:** Clarity, gravity, and uncompromising precision. The user should feel like they are accessing a secure government database, not a startup landing page.

---

## 2. Color Palette & Roles

The color strategy utilizes a **"Paper and Ink"** philosophy — the warm, desaturated tones of newsprint with the stark contrast of printed type.

### Primary Palette
- **Newsprint Cream** (#F4F1EA) — Primary page background. Warm, reduces eye strain vs. pure white.
- **Ivory Surface** (#FCFAF5) — Content block backgrounds. Distinguishes cards from page.
- **Deep Ink** (#111111) — Structural borders, headings, high-contrast text. Near-black, not pure #000.
- **Charcoal Body** (#1C1B1B) — Primary body text color.
- **Steel Muted** (#747878) — Secondary text, descriptions, metadata, borders.

### Semantic Accents (Use Sparingly)
- **Oxblood Flag** (#8C2929) — Discrepancies, over-utilization, warnings. Muted red, not neon.
- **Forest Clear** (#2D5D40) — Verified transactions, under-utilization, success states. Professional green.
- **Selection Cream** (#E5E0D8) — Active/hover state background for interactive elements.

### Surface Hierarchy
- **Surface Container Lowest** (#FFFFFF) — Highest elevation, pure white.
- **Surface Container Low** (#F7F3F2)
- **Surface Container** (#F1EDEC)
- **Surface Container High** (#EBE7E6)
- **Surface Container Highest** (#E5E2E1) — Lowest elevation, most recessed.

### Constraints
- **Maximum 2 accent colors** (Oxblood, Forest). Saturation below 50%.
- **No purple, no neon, no gradients.** AI-tell colors are banned.
- **Never use pure black (#000000).** Always Deep Ink (#111111) or Charcoal (#1C1B1B).
- **Tinted shadows** — if shadows are used, tint to cream/sepia undertones.

---

## 3. Typography Rules

The system uses a **tri-font hierarchy** to separate editorial voice from raw data.

### Font Stack
1. **Playfair Display (Serif)** — Mastheads, headlines, editorial voice. Authoritative, "Old World" news feel.
   - `display-masthead`: 30px / 700 weight / -0.02em letter-spacing / 1.2 line-height
   - `headline-lg`: 24px / 700 weight / 1.2 line-height
   - `headline-md`: 18px / 700 weight / 1.3 line-height

2. **Libre Franklin (Sans-Serif)** — Body copy, metadata labels. Maximum legibility at small sizes.
   - `body-main`: 15px / 400 weight / 1.4 line-height
   - `label-caps`: 11px / 600 weight / 0.15em letter-spacing (ALL CAPS)

3. **IBM Plex Mono (Monospaced)** — Financial figures, timestamps, project IDs, status indicators. Reinforces "audit log" nature.
   - `data-lg`: 30px / 500 weight / -0.05em letter-spacing (Hero numbers)
   - `data-sm`: 12px / 500 weight / 1.0 line-height (Inline data)
   - `nav-label`: 10px / 600 weight / 0.1em letter-spacing (Navigation)

### Typography Rules
- **All Naira values use IBM Plex Mono.** No exceptions.
- **All timestamps, project IDs, status codes use monospace.**
- **Headlines are serif, body is sans-serif, data is monospace.** This hierarchy is non-negotiable.
- **Maximum 65 characters per line** for body text.
- **Line height for data is 1.0** — tight, ledger-like.

### Banned Fonts
- **Inter** — Overused AI-tell. Banned.
- **Generic serifs** (Georgia, Garamond, Times New Roman) — Banned. Playfair Display only.
- **System fonts** — Banned for primary interface.

---

## 4. Component Stylings

### Shapes
- **Sharp corners (0px) everywhere.** No `rounded-sm`, `rounded-lg`, `rounded-xl`.
- Every element — buttons, cards, inputs, images — must have 90-degree corners.
- This reinforces the "printed paper" aesthetic.

### Borders
- **Hairline borders (1px)** define all containers.
- **Heavy borders (3px)** define major section separators (masthead baseline, ticker top).
- **No shadows.** Depth is communicated via border weight and background color shifts.
- **Tint shadows** — if shadows are absolutely necessary, tint to cream (#F4F1EA) undertones.

### Buttons
- **Flat, no outer glow.**
- **Primary CTA:** Deep Ink (#111111) background, Ivory (#FCFAF5) text, 1px border.
- **Secondary/ghost:** Transparent background, Deep Ink text, 1px Deep Ink border.
- **Active state:** Background shifts to Selection Cream (#E5E0D8). No scale transform.
- **Shape:** Full-width blocks or inline text links. No pill shapes.

### Cards (News Blocks)
- **Rectangular containers with 1px Deep Ink borders.**
- **Structure:**
  - Top: `label-caps` category (ALL CAPS, 11px, Libre Franklin, 0.15em spacing)
  - Middle: Headline or data visualization
  - Bottom: `data-sm` timestamp or status (IBM Plex Mono)
- **No rounded corners.**
- **No shadows.**
- **Hover state:** Background shifts to Selection Cream (#E5E0D8).

### Data Ticker
- **Full-width horizontal strip.**
- **Deep Ink (#111111) background, Ivory (#FCFAF5) text.**
- **Continuous horizontal scroll** (CSS `marquee` or animation).
- **High-density:** 50+ data points visible without scroll.

### Progress Bars
- **Solid, flat blocks. No rounded caps.**
- **Track:** Dark grey (#333333).
- **Fill:** Bright neutral or semantic color (Forest Clear for success).
- **0px rounded corners.**

### Status Chips
- **Inline monospaced text (IBM Plex Mono).**
- **Color-coded:** Oxblood (#8C2929) for warning, Forest Clear (#2D5D40) for verified.
- **No pill shapes.** Text only, possibly prefixed with a geometric icon (■, ●, ▲).

### Navigation
- **Bottom Navigation:** Segmented grid of equal-width blocks separated by 1px vertical rules.
- **Monospaced labels** (`nav-label` spec).
- **Utility-first feel.**
- **No floating headers.** Navigation is structural.

---

## 5. Layout Principles

### Grid Philosophy
- **Fixed newspaper grid.** Columnar, rigorous, predictable.
- **1 column mobile, 2 columns tablet, 3 columns desktop.**
- **Critical "Lead Stories" or large data visualizations can span multiple columns.**

### Spacing System
- **Base unit:** 8px (0.5rem).
- **Container padding:** 1rem (16px).
- **Section gap:** 1.5rem (24px).
- **Max-width:** 1200px centered.

### Named Layout Sections
1. **The Masthead** — Centered, high-profile header. Separated by 3px heavy baseline.
2. **The Ticker** — Full-width, high-contrast horizontal strip for real-time data flow.
3. **The Grid** — Multi-column responsive grid for primary content.
4. **The Ledger** — High-density table view for transaction-level data.

### Anti-Patterns (Layout)
- **No centered hero sections.** Hero is a dashboard/stat grid.
- **No 3-column equal card layouts.** Use asymmetric column spans.
- **No overlapping elements.** Every element occupies its own clear spatial zone.
- **No full-bleed images.** All visuals contained within grid cells.

---

## 6. Motion & Interaction

### Motion Philosophy
- **Static Restrained.** This is a public record, not a product demo.
- **Motion draws attention.** Data should speak for itself.
- **No perpetual micro-interactions.** No infinite pulse, float, shimmer.

### Interaction States
- **Hover:** Background color shift to Selection Cream (#E5E0D8).
- **Active:** -1px translateY for tactile push feel (buttons only).
- **Focus:** 2px Deep Ink outline for accessibility.
- **Loading:** Skeletal shimmer matching exact layout dimensions. No circular spinners.

### Animation Rules
- **If animation is necessary:** Use CSS `transition` with `200ms ease-out`.
- **Never animate:** `width`, `height`, `top`, `left`. Use `transform` and `opacity` only.
- **No spring physics.** This is a ledger, not a playful app.

---

## 7. Anti-Patterns (Banned)

### Explicitly Forbidden
- **No emojis anywhere.**
- **No Inter font.**
- **No generic serif fonts** (Georgia, Garamond, Times New Roman).
- **No pure black (#000000).**
- **No neon/outer glow shadows.**
- **No rounded corners.** Sharp 0px only.
- **No gradients.**
- **No centered hero sections.**
- **No 3-column equal card grids.**
- **No AI copywriting clichés** ("Elevate", "Seamless", "Unleash", "Next-Gen", "Empower").
- **No filler UI text** ("Scroll to explore", "Swipe down", scroll arrows, bouncing chevrons).
- **No fake round numbers** (99.99%, 50%).
- **No generic placeholder names** ("John Doe", "Acme", "Nexus").
- **No broken image links.** Use `picsum.photos` or SVG patterns.
- **No vibe-coded SaaS aesthetic.** Institutional authority only.

---

## 8. Key Surfaces (Screen Specifications)

### Home — "The Command Center"
- **Masthead:** "OpenSpends NG" in Playfair Display `display-masthead`. 3px baseline separator.
- **Ticker:** Full-width rolling strip showing: Total Allocated | Total Spent | Variance | Projects Count. Deep Ink background.
- **Stat Grid:** 4-column grid (2x2 on mobile). Each cell is a bordered card with:
  - `label-caps` category
  - `data-lg` number (IBM Plex Mono)
  - `data-sm` trend indicator
- **Mini-Map:** Embedded ProjectMap component showing Nigeria outline with project markers.
- **Recent Transactions:** High-density table with zebra-striping. 10 rows visible.

### Map — "The Spatial Ledger"
- **Full-viewport map** (Mapbox GL JS, dark style).
- **Sidebar:** Filter-driven project list. Syncs with map view.
- **Tablet/Mobile:** Sidebar collapses to bottom sheet.
- **Markers:** Oxblood (#8C2929) or Forest Clear (#2D5D40) dots based on status.
- **Popups:** Monospace project ID, MDA name, amount in Naira.

### MDA Detail — "The Ministry Audit"
- **Ministry Header:** Playfair Display `headline-lg`. MDA code in `data-sm`.
- **Variance Table:** High-density rows. Columns: Project | Allocated | Spent | Variance | Status.
- **Status column:** Monospace text with color coding (Oxblood/Forest).
- **Download Buttons:** Flat, inline. "Export CSV" | "Export JSON".

### Analytics — "The Variance Audit"
- **Chart Container:** Bordered card. No shadows.
- **Chart Type:** Flat bar charts (Recharts). No 3D, no gradients.
- **Legend:** Monospace labels with color swatches.
- **Filter Bar:** Segmented controls with 1px borders.

---

## 9. Implementation Notes

### For Stitch
- Use **Visual Descriptions** with specific hex codes and pixel values.
- Reference **"Newspaper", "Audit Ledger", "Financial Broadsheet"** as mood anchors.
- Emphasize **"Sharp corners (0px)"** and **"Hairline borders (1px)"** in every component.

### For Developer Handoff
- All tokens are defined in the `the_institutional_broadsheet.md` YAML frontmatter.
- Use **CSS custom properties** for colors (`--color-surface`, `--color-primary`, etc.).
- Use **Tailwind arbitrary values** if immediate implementation is needed.
- **Google Fonts:** Playfair Display, Libre Franklin, IBM Plex Mono are all available via Google Fonts.

---

**Final Note:** This is not a SaaS product. It is a **public record**. The design must communicate institutional trust, not startup vibrancy. Clarity over cleverness. Precision over polish.
