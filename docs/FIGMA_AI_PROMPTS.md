# Figma AI Design Prompts - PDF Visualizer App

## Design System Overview

**Theme**: Dark, minimalist, developer-focused aesthetic inspired by modern IDEs (VSCode, GitHub Dark)

**Color Palette**:
- Background: #0e1117 (deep dark blue-black)
- Surface: #1e1e2e (slightly lighter panels)
- Primary accent: #00d9ff (cyan - for data visualization)
- Success/Bullish: #00ff88 (bright green)
- Warning/Bearish: #ff4757 (coral red)
- Text primary: #fafafa (near white)
- Text secondary: #a0a0a0 (gray)
- Borders: #2a2a3e (subtle purple-gray)

**Typography**:
- Headings: Inter/SF Pro Display, 600-700 weight
- Body: Inter/SF Pro Text, 400 weight
- Monospace (for numbers): JetBrains Mono/Fira Code

**Visual Style**:
- Glassmorphism cards with subtle backdrop blur
- Generous whitespace (24-32px spacing)
- Subtle gradients on key elements
- Smooth shadows (no harsh edges)
- Minimal animations (fade, slide only)

---

## 1. LANDING PAGE - Hero Section

**Prompt for Figma AI:**

```
Create a dark mode landing page hero section for a quantitative finance web app.

Layout:
- Full viewport height (100vh)
- Centered content with max-width 1200px
- Dark background (#0e1117) with subtle radial gradient from center (rgba(0,217,255,0.03))
- Glassmorphism card in center with backdrop blur

Content Structure:
Top section:
- App logo/icon (abstract probability curve symbol) in cyan (#00d9ff)
- Main heading: "Option-Implied PDF Visualizer" in white (#fafafa), 48px, bold
- Subheading: "Decode market expectations through option-implied probability distributions" in gray (#a0a0a0), 18px, regular

Middle section:
- Two-column layout (60/40 split):
  LEFT: Beginner explanation card
    - Icon: graduation cap in cyan
    - Heading: "New to PDF Analysis?"
    - Body text: "Option prices reveal what the market thinks will happen next. We extract those hidden probabilities into beautiful, actionable visualizations."
    - Background: subtle dark surface (#1e1e2e) with border (#2a2a3e)

  RIGHT: Advanced explanation card
    - Icon: chart line in green
    - Heading: "For Experienced Traders"
    - Body text: "Breeden-Litzenberger extraction with SABR calibration. Real-time risk-neutral densities for SPY/SPX with tail risk analytics."
    - Background: same dark surface

Bottom section:
- Call-to-action area with inputs and button (see next prompt)

Visual details:
- Smooth card shadows: 0 8px 32px rgba(0,0,0,0.3)
- Cards have 1px border in #2a2a3e
- Subtle hover effects: lift by 4px, glow in cyan
- Icons use line style (not filled)
- All text is left-aligned within cards
- 24px padding inside cards
- 32px vertical spacing between elements

Style: Minimalist, elegant, developer-focused, modern fintech aesthetic
```

---

## 2. LANDING PAGE - Input Controls Section

**Prompt for Figma AI:**

```
Create a dark mode input controls section for a quantitative finance app, positioned below the hero section.

Layout:
- Centered container, max-width 800px
- Dark glassmorphism card with backdrop blur
- Background: #1e1e2e with 1px border in #2a2a3e
- Card has subtle gradient overlay (top to bottom: rgba(0,217,255,0.02) to transparent)

Content Structure:
Heading:
- "Configure Analysis" in white (#fafafa), 24px, semibold
- Subtle cyan accent line (2px height) below heading

Input Grid (3 columns, equal width):

Column 1 - Ticker Symbol:
- Label: "Ticker Symbol" in gray (#a0a0a0), 12px uppercase
- Input field: dark (#0e1117), white text (#fafafa), cyan border on focus
- Placeholder: "SPY" in light gray
- Helper text below: "ETF or stock ticker" in subtle gray
- Icon: dollar sign in cyan, positioned left inside input

Column 2 - Days to Expiration:
- Label: "Days to Expiration (DTE)" in gray (#a0a0a0)
- Dropdown selector: dark background, white text
- Options: 7, 14, 21, 30, 45, 60, 90
- Default selected: 30
- Icon: calendar in cyan, positioned left

Column 3 - Analysis Mode:
- Label: "Analysis Mode" in gray (#a0a0a0)
- Dropdown selector with mode descriptions on hover
- Options styled as pills:
  • Standard (blue accent)
  • Conservative (purple accent)
  • Aggressive (orange accent)
  • Educational (green accent)
- Icon: brain/AI symbol in cyan

CTA Button:
- Full width below inputs (16px gap)
- Height: 56px
- Background: Gradient from #00d9ff to #0099cc (cyan)
- Text: "Run Analysis" in dark (#0e1117), 18px, bold
- Icon: rocket emoji before text
- Hover state: Lift by 2px, brighter glow
- Active state: Subtle scale down (0.98)

Advanced Settings (collapsed):
- Small expandable section below button
- "Advanced Settings" text with chevron icon
- When expanded: Shows toggle for SABR model, auto-save options
- Collapsed by default

Visual details:
- Input fields: 48px height, 12px border radius
- Dropdowns: Custom styled (not native), dark theme
- All interactive elements have smooth transitions (200ms)
- Focus states use cyan (#00d9ff) glow
- Spacing: 16px between inputs, 24px vertical padding
- Subtle hover states on all inputs (border brighten)

Style: Clean, professional, IDE-inspired, minimal but functional
```

---

## 3. RESULTS PAGE - PDF Visualization Hero

**Prompt for Figma AI:**

```
Create a dark mode data visualization hero section showing an option-implied probability distribution chart.

Layout:
- Full width container with max-width 1400px
- Two-column layout (70/30 split)

LEFT COLUMN - Chart:
Dark glassmorphism card containing:
- Heading: "SPY Option-Implied PDF (30D)" in white (#fafafa), 20px
- Subtitle: Real-time analysis indicator (green dot + "Live Data" text)

Chart visualization mock:
- X-axis: "Strike Price ($)" from 550 to 800
- Y-axis: "Probability Density" from 0 to 0.025
- Main curve: Smooth bell-curve-like shape in cyan (#00d9ff) with gradient fill below (rgba(0,217,255,0.2))
- Vertical dashed line: Spot price at $685.69 in green (#00ff88) with label "Spot: $685.69"
- Shaded confidence interval: Green overlay (rgba(0,255,136,0.15)) between $674.79 and $710.64
- Dotted vertical lines at CI bounds with labels
- Grid: Subtle gray (#2a2a3e), very thin lines
- Tooltips on hover: White card with data point details

Chart container:
- Background: #1e1e2e
- Border: 1px solid #2a2a3e
- Padding: 24px
- Border radius: 12px
- Shadow: 0 8px 32px rgba(0,0,0,0.3)

RIGHT COLUMN - Purpose Card:
Glassmorphism card with:
- Icon: Info circle in cyan (top)
- Heading: "What This Shows" in white, 18px, semibold
- Body paragraphs:

  Paragraph 1:
  "This curve represents the market's collective belief about where SPY will trade at expiration."

  Paragraph 2 (with highlight):
  "Peak = Most likely outcome (~$690)"
  "Width = Uncertainty range (±$11)"
  "Shape = Directional bias (bearish tilt)"

  Paragraph 3:
  "The green shaded region shows a 68% probability zone—the market expects price to land here 2 out of 3 times."

Visual callouts:
- Small arrows pointing to chart features from this card
- Highlighted key numbers in cyan
- Bullet points with cyan dots

Visual details:
- Card backgrounds: #1e1e2e with subtle gradient
- Text is highly readable (good contrast)
- Generous line spacing (1.6 line height)
- Icons are outline style, cyan colored
- Smooth shadows on cards
- Cards have 1px borders in #2a2a3e

Style: Data-focused, elegant, educational but not dumbed down, professional fintech aesthetic
```

---

## 4. RESULTS PAGE - Key Metrics Cards

**Prompt for Figma AI:**

```
Create a dark mode metrics dashboard section with 4 data cards showing key probability statistics.

Layout:
- 4 equal-width columns in a row
- Each card is a glassmorphism panel
- Spacing: 16px gap between cards
- Full width container (max-width 1400px)

Card 1 - Spot Price:
- Background: Dark surface (#1e1e2e)
- Border: 1px solid #2a2a3e
- Icon: Target/crosshair in cyan (top left)
- Label: "Spot Price" in gray (#a0a0a0), 12px uppercase
- Value: "$685.69" in white (#fafafa), 36px, bold, monospace font
- Subtext: "Current underlying price" in light gray, 14px
- Accent: Thin cyan top border (2px)

Card 2 - Expected Price:
- Same styling as Card 1
- Icon: Trending up arrow in green
- Label: "Expected Price"
- Value: "$692.11" in white, 36px, monospace
- Delta indicator:
  • "+$6.42" in green (#00ff88), 18px, with up arrow
  • Small pill badge showing "+0.94%"
- Subtext: "Risk-neutral mean"
- Accent: Thin green top border (2px)

Card 3 - Implied Move:
- Same styling
- Icon: Expand arrows (horizontal) in cyan
- Label: "Implied Move"
- Value: "±3.85%" in white, 36px, monospace
- Range display:
  • "$660 - $710" in light gray, 16px
  • Visual progress bar showing range (subtle gradient)
- Subtext: "Expected price range"
- Accent: Thin cyan top border (2px)

Card 4 - Market Bias:
- Same styling
- Icon: Balance/scale in red (tilted)
- Label: "Market Bias"
- Value: "Bearish" in red (#ff4757), 28px, semibold
- Indicator: Emoji "📉" next to text
- Metric: "-1.725" in monospace, gray, 14px
- Subtext: "Distribution skewness"
- Accent: Thin red top border (2px)

Visual details:
- Cards: 24px padding, 12px border radius
- Hover effect: Lift by 4px, subtle glow in accent color
- Shadow: 0 4px 16px rgba(0,0,0,0.2)
- Icons: 24px size, positioned top left with 8px margin
- Values use JetBrains Mono or similar monospace font
- Delta indicators use arrows (↑ ↓) in matching colors
- All transitions: 200ms ease

Responsive:
- On smaller screens, stack into 2x2 grid
- Maintain aspect ratio and spacing

Style: Clean, data-dense, professional, IDE-inspired color accents
```

---

## 5. RESULTS PAGE - AI Interpretation Card

**Prompt for Figma AI:**

```
Create a dark mode AI analysis section displaying market interpretation with visual emphasis.

Layout:
- Full width container (max-width 1400px)
- Large glassmorphism card

Header Section:
- Icon: Robot/AI brain icon in cyan with subtle pulse animation
- Heading: "AI Market Interpretation" in white (#fafafa), 24px, semibold
- Mode badge: Pill-shaped badge showing "Standard Mode" in cyan with light background
- Timestamp: "Updated 2 minutes ago" in gray, 12px, right-aligned

Content Sections (4 numbered blocks):

Section 1 - Market Sentiment:
- Number badge: "1" in cyan circle (32px diameter)
- Subheading: "Market Sentiment" in white, 18px, semibold
- Body text (2-3 sentences):
  "The PDF shows a bearish tilt with the peak shifted left of spot price. Market participants are pricing elevated downside risk compared to upside potential. The distribution suggests cautious positioning ahead of expiration."
- Key phrase highlight: "bearish tilt" highlighted in red background with white text
- Visual indicator: Small arrow pointing to relevant chart feature

Section 2 - Tail Risk Assessment:
- Number badge: "2" in cyan
- Subheading: "Tail Risk Assessment" in white
- Body text with inline metrics:
  "Downside tail (-10%) is priced at 8.2% probability, while upside tail (+10%) sits at 5.1%. This asymmetry signals elevated crash protection premium. Kurtosis of 0.5 indicates moderately fat tails."
- Inline metric styling: Cyan background pills for percentages
- Comparison chart: Mini bar chart showing tail probabilities side-by-side

Section 3 - Trading Implications:
- Number badge: "3" in cyan
- Subheading: "Trading Implications" in white
- Body text:
  "Favorable strategies: Put spreads, iron condors with bearish skew. Avoid naked calls. The 68% CI ($674-$710) presents natural strike boundaries for defined-risk strategies."
- Strategy pills: Small pill badges for each strategy mentioned (e.g., "Put Spreads" in purple pill)
- Icon: Strategy diagram (simple visual of put spread)

Section 4 - Key Takeaway:
- Number badge: "✓" in green circle
- Subheading: "Key Takeaway" in white
- Body text (1 impactful sentence):
  "Markets are pricing asymmetric downside risk—position accordingly with protective structures."
- Visual treatment: This section has green accent border (left side, 4px thick)
- Background: Slightly lighter than other sections to stand out

Visual details:
- Card background: #1e1e2e with gradient overlay
- Border: 1px solid #2a2a3e
- Padding: 32px
- Border radius: 12px
- Number badges: Cyan (#00d9ff) background, white text, 32px diameter
- Section spacing: 24px vertical gap
- Body text: 16px, line height 1.6, gray (#d0d0d0)
- Headings: White (#fafafa), semibold
- Inline highlights: Pills with 4px padding, 4px border radius
- Subtle connector lines between number badges (dotted, cyan)

Interactive elements:
- "Switch Mode" button in top right (to change analysis mode)
- Expandable sections (click to see more detail)
- Copy button to copy interpretation text

Style: Professional, AI-focused, clean typography, data storytelling aesthetic
```

---

## 6. RESULTS PAGE - Statistics Deep Dive

**Prompt for Figma AI:**

```
Create a dark mode statistics dashboard with two side-by-side cards showing distribution metrics.

Layout:
- Two-column layout (50/50 split)
- 16px gap between columns
- Full width container (max-width 1400px)

LEFT CARD - Distribution Shape:
Glassmorphism card containing:

Header:
- Icon: Wave/curve icon in cyan
- Heading: "Distribution Shape" in white, 20px, semibold

Metric rows (table-like structure):

Row 1:
- Label: "Skewness" in gray, left-aligned
- Value: "-0.15" in white, monospace, right-aligned
- Visual bar: Horizontal bar showing negative skew (tilted left)
- Color: Red gradient for negative value

Row 2:
- Label: "Kurtosis (Excess)" in gray
- Value: "0.50" in white, monospace
- Visual bar: Showing moderate fat tails
- Color: Cyan gradient

Insight box (below metrics):
- Background: Slightly darker (#181820)
- Icon: Lightbulb in cyan
- Text: "Strong bearish tilt - elevated downside risk"
- Style: Pill-shaped, subtle glow

Visual elements:
- Mini distribution curve visualization showing left skew
- Color-coded zones (green for normal, red for heavy tails)

RIGHT CARD - Tail Risk:
Same card styling

Header:
- Icon: Alert triangle in orange
- Heading: "Tail Risk Analysis" in white

Metric rows:

Row 1:
- Label: "Prob(+10%)" in gray
- Value: "5.1%" in green, monospace
- Progress bar: 5% filled in green gradient
- Percentile marker on bar

Row 2:
- Label: "Prob(-10%)" in gray
- Value: "8.2%" in red, monospace
- Progress bar: 8% filled in red gradient

Comparison metric:
- Label: "Tail Ratio" in gray
- Value: "1.61x" in orange, monospace
- Subtext: "Downside / Upside"

Insight box:
- Background: Dark (#181820)
- Icon: Warning icon in red
- Text: "Elevated downside tail risk"
- Style: Pill with red glow

Visual elements:
- Mini tail distribution diagram (both ends highlighted)
- Side-by-side bars comparing up vs down tails

Card styling (both cards):
- Background: #1e1e2e
- Border: 1px solid #2a2a3e
- Padding: 24px
- Border radius: 12px
- Shadow: 0 4px 16px rgba(0,0,0,0.2)

Metric styling:
- Row height: 48px
- Label: 14px, gray (#a0a0a0)
- Value: 24px, monospace, white
- Progress bars: 8px height, rounded, gradient fills
- Spacing: 12px between rows

Interactive:
- Hover on metrics shows tooltip with explanation
- Progress bars animate on page load (fill from 0 to value)

Style: Data-dense, visual, educational, modern fintech dashboard aesthetic
```

---

## 7. RESULTS PAGE - Probability Table

**Prompt for Figma AI:**

```
Create a dark mode probability table showing strike-level breakdown of probabilities.

Layout:
- Full width container (max-width 1400px)
- Single large glassmorphism card

Header:
- Icon: Table/grid icon in cyan
- Heading: "Key Strike Probabilities" in white, 20px, semibold
- Subtext: "Cumulative probability at key price levels" in gray, 14px

Table Structure:

Column headers (sticky on scroll):
- "Strike" | "P(S < K)" | "P(S > K)" | "Distance from Spot"
- Background: Darker (#181820)
- Text: Gray uppercase, 12px, bold
- Border bottom: 2px solid cyan (#00d9ff)

Table rows (10 strikes, evenly spaced):

Example row 1 (ATM strike):
- Strike: "$685" in white, monospace, 16px
- P(S < K): "50.0%" in white, monospace
- P(S > K): "50.0%" in white, monospace
- Distance: "±0.0%" in gray, small pill badge
- Background: Subtle highlight (#252530) - this is the ATM row
- Left border: 3px solid green (indicates spot price)

Example row 2 (OTM put):
- Strike: "$660" in white
- P(S < K): "15.8%" in white
- P(S > K): "84.2%" in white
- Distance: "-3.7%" in red, pill badge
- Background: Default (#1e1e2e)

Example row 3 (OTM call):
- Strike: "$710" in white
- P(S < K): "84.2%" in white
- P(S > K): "15.8%" in white
- Distance: "+3.5%" in green, pill badge
- Background: Default

Row styling:
- Height: 56px
- Padding: 12px 16px
- Border bottom: 1px solid #2a2a3e
- Hover: Background lightens to #252530, subtle left border in cyan
- Transition: 150ms ease

Probability cells:
- Use horizontal mini bars behind text to visualize percentage
- Bar colors: Gradient from cyan to transparent
- Higher probabilities = fuller bars

Visual indicators:
- Color coding for distance from spot:
  • Negative (OTM puts): Red background pill
  • Zero (ATM): Green background pill
  • Positive (OTM calls): Green background pill
- At-the-money row highlighted with subtle glow

Card styling:
- Background: #1e1e2e
- Border: 1px solid #2a2a3e
- Padding: 0 (table fills card)
- Border radius: 12px
- Shadow: 0 4px 16px rgba(0,0,0,0.2)
- Overflow: Hidden (rounded corners clip table)

Interactive:
- Sortable columns (click header to sort)
- Hover on row shows mini chart of PDF at that strike
- Mobile: Scrollable horizontally, sticky first column

Style: Clean, data-focused, spreadsheet-inspired but elegant, professional quant aesthetic
```

---

## 8. NAVIGATION & LAYOUT

**Prompt for Figma AI:**

```
Create a dark mode minimal navigation header for a quantitative finance web app.

Layout:
- Fixed header, full width
- Height: 64px
- Background: #0e1117 with 80% opacity, backdrop blur effect
- Bottom border: 1px solid #2a2a3e with subtle glow

Header content (max-width 1400px, centered):

Left section:
- App logo: Abstract probability curve symbol (line art, cyan)
- App name: "PDF Visualizer" in white, 18px, semibold
- Beta badge: Small "BETA" pill in cyan with opacity

Center section:
- Navigation tabs (horizontal):
  • "Home" - active state (cyan underline, white text)
  • "Live Analysis" - inactive (gray text)
  • "Historical" - inactive
  • "Predictions" - inactive
  • "About" - inactive
- Active indicator: 2px cyan line below text
- Hover: Text brightens, subtle cyan glow

Right section:
- Settings icon button (gear, cyan on hover)
- Theme toggle (sun/moon icon) - optional since dark is default
- User profile avatar (optional)

Tab styling:
- Text: 14px, semibold
- Padding: 16px 20px
- Spacing: 8px gap
- Hover: Background #1e1e2e, text brightens
- Active: Cyan underline (2px), white text, slight glow
- Transition: 200ms ease

Icon buttons:
- Size: 40px × 40px
- Border radius: 8px
- Hover: Background #1e1e2e, icon color cyan
- Icons: 20px, line style

Visual details:
- Header casts subtle shadow: 0 2px 16px rgba(0,0,0,0.4)
- Backdrop blur: 12px (glassmorphism)
- Z-index: High (stays on top during scroll)
- Smooth transitions on all interactive elements

Mobile responsive:
- Hamburger menu icon replaces center nav
- Logo scales down slightly
- Settings moved to slide-out menu

Style: Minimal, modern, IDE-inspired, professional
```

---

## 9. FOOTER

**Prompt for Figma AI:**

```
Create a dark mode minimal footer for a quantitative finance web app.

Layout:
- Full width
- Background: #0e1117 (solid, no transparency)
- Top border: 1px solid #2a2a3e
- Padding: 48px 0

Footer content (max-width 1400px, centered):

Three-column layout:

LEFT COLUMN - Branding:
- App logo (larger, 32px)
- Tagline: "Decode market expectations" in gray, 14px, italic
- Social links (optional): GitHub, Twitter icons in gray (cyan on hover)

CENTER COLUMN - Quick Links:
- Heading: "Resources" in white, 14px, semibold
- Links (stacked):
  • "Documentation"
  • "API Reference"
  • "About the Model"
  • "Educational Content"
- Link style: Gray text, cyan on hover, 14px
- Spacing: 8px between links

RIGHT COLUMN - Info:
- Heading: "Disclaimer" in white, 14px, semibold
- Text: "For educational purposes only. Not financial advice." in gray, 12px
- Built with: "Built with Claude Code" in small gray text with link

Bottom section (below columns):
- Thin horizontal line (1px, #2a2a3e)
- Copyright: "© 2025 PDF Visualizer" in small gray text, centered
- Version: "v1.0.0" in small cyan text, right-aligned

Visual details:
- All text is highly readable (good contrast)
- Links have smooth transitions (200ms)
- Icons are line style, 20px
- Column spacing: 32px gap
- Bottom section: 24px top margin

Style: Minimal, unobtrusive, professional
```

---

## 10. LOADING STATES & ANIMATIONS

**Prompt for Figma AI:**

```
Create dark mode loading state components for data fetching in a finance app.

Component 1 - Analysis Loading Card:
- Centered glassmorphism card (400px × 300px)
- Background: #1e1e2e with subtle pulse animation
- Border: 1px solid #2a2a3e with animated glow (cyan pulse)

Content:
- Animated spinner: Circular spinner in cyan gradient, 64px diameter
- Loading text: "Fetching option chain data..." in white, 18px
- Progress indicator: 6 step dots below text
  • Steps: "Data" | "Risk-Free Rate" | "PDF" | "Stats" | "Patterns" | "AI"
  • Active step: Cyan glow
  • Completed steps: Green checkmark
  • Pending steps: Gray outline
- Estimated time: "~15-30 seconds" in gray, 12px

Animation:
- Spinner rotates smoothly (2s loop)
- Steps fill left-to-right with smooth transitions
- Subtle background pulse (2s loop, opacity 0.9-1.0)

Component 2 - Skeleton Loader (for charts):
- Chart area placeholder
- Animated gradient sweep (left to right)
- Colors: #1e1e2e to #2a2a3e gradient
- Shows outline of where chart will appear
- Smooth shimmer effect

Component 3 - Error State Card:
- Same size and styling as loading card
- Icon: Alert triangle in red, 48px
- Heading: "Analysis Failed" in red, 20px
- Error message: User-friendly text in white, 14px
- Retry button: Cyan gradient, "Try Again" text
- Details: Collapsible technical error (for debugging)

Visual details:
- All animations: Smooth, 60fps, ease-in-out
- Loading card: Drop shadow 0 8px 32px rgba(0,0,0,0.3)
- Spinners use CSS animations (not GIF)
- Progress dots: 8px diameter, 4px gap
- Error button: Same styling as main CTA

Style: Polished, professional, calming (not frustrating during wait)
```

---

## Design System Color Reference

```css
/* Background Colors */
--bg-primary: #0e1117;
--bg-surface: #1e1e2e;
--bg-surface-bright: #252530;
--bg-darker: #181820;

/* Text Colors */
--text-primary: #fafafa;
--text-secondary: #d0d0d0;
--text-muted: #a0a0a0;

/* Accent Colors */
--accent-cyan: #00d9ff;
--accent-green: #00ff88;
--accent-red: #ff4757;
--accent-orange: #ffa502;
--accent-purple: #a29bfe;

/* Border & Dividers */
--border-default: #2a2a3e;
--border-bright: #3a3a4e;

/* Shadows */
--shadow-sm: 0 2px 8px rgba(0,0,0,0.2);
--shadow-md: 0 4px 16px rgba(0,0,0,0.2);
--shadow-lg: 0 8px 32px rgba(0,0,0,0.3);

/* Gradients */
--gradient-cyan: linear-gradient(135deg, #00d9ff 0%, #0099cc 100%);
--gradient-green: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
--gradient-surface: linear-gradient(180deg, rgba(0,217,255,0.02) 0%, transparent 100%);
```

---

## Typography Scale

```css
/* Headings */
--text-h1: 48px / 700 / Inter
--text-h2: 36px / 600 / Inter
--text-h3: 24px / 600 / Inter
--text-h4: 20px / 600 / Inter
--text-h5: 18px / 600 / Inter

/* Body */
--text-body-lg: 18px / 400 / Inter
--text-body: 16px / 400 / Inter
--text-body-sm: 14px / 400 / Inter
--text-caption: 12px / 400 / Inter

/* Monospace (for data) */
--text-mono-lg: 36px / 700 / JetBrains Mono
--text-mono: 16px / 400 / JetBrains Mono
--text-mono-sm: 14px / 400 / JetBrains Mono
```

---

## Spacing System

```
--space-xs: 4px
--space-sm: 8px
--space-md: 12px
--space-lg: 16px
--space-xl: 24px
--space-2xl: 32px
--space-3xl: 48px
```

---

## Border Radius

```
--radius-sm: 4px   (pills, badges)
--radius-md: 8px   (buttons, inputs)
--radius-lg: 12px  (cards)
--radius-xl: 16px  (large containers)
```

---

## Usage Instructions

1. **Copy each prompt individually** into Figma AI or similar design tools
2. **Generate each component separately** to maintain consistency
3. **Combine components** in Figma to build complete pages
4. **Export assets** (SVG for icons, PNG for mockups)
5. **Use color codes exactly** as specified for brand consistency
6. **Test dark mode** on actual dark backgrounds (not white Figma canvas)
7. **Ensure text contrast** meets WCAG AA standards (4.5:1 minimum)

---

## Notes

- All components designed for **desktop first** (1440px optimal)
- **Mobile responsive** breakpoints: 768px (tablet), 375px (mobile)
- **Glassmorphism** requires backdrop-filter CSS support
- **Animations** should be subtle and performance-optimized
- **Data visualizations** use Plotly.js dark theme (already in codebase)
- **Podcast embeds** to be added later (use audio player component)

This design system prioritizes **clarity, professionalism, and data focus** while maintaining an elegant, modern aesthetic that appeals to quantitative traders and developers.
