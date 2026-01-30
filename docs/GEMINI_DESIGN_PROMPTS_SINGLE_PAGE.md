# Gemini Design Prompts - Single-Page PDF Visualizer

## Design System (Use for ALL sections)

**Colors**: BG #0e1117 | Surface #1e1e2e | Cyan #00d9ff | Green #00ff88 | Red #ff4757 | White #fafafa | Gray #a0a0a0 | Border #2a2a3e
**Fonts**: Inter (headings 600-700), JetBrains Mono (numbers)
**Style**: Dark theme, glassmorphism cards, 24-32px spacing, subtle shadows

---

## SECTION 1: Hero

```
Dark finance web app hero: 1440×400px, BG #0e1117 with radial cyan glow, faint grid. Centered: probability curve icon (cyan 48px), "Option-Implied PDF Visualizer" (white 42px bold), tagline "Decode market expectations through real-time probability distributions" (gray 16px), thin cyan gradient line below. Minimal, modern.
```

---

## SECTION 2: What Is PDF?

```
Dark mode educational section, 1200px wide. Heading "What Is PDF Analysis?" white 32px centered.

Two equal glassmorphism cards (#1e1e2e, border #2a2a3e, rounded 12px, padding 32px):

LEFT "New to Options?" - graduation cap icon cyan 32px, beginner text: "Option prices contain hidden info about market expectations. We extract these into probability charts. See where traders think stock will land, uncertainty range, directional bias." Highlight key phrases in cyan.

RIGHT "For Quants & Traders" - chart icon cyan 32px, technical text: "Breeden-Litzenberger risk-neutral density extraction. SABR volatility calibration. Real-time SPY/SPX analysis. Full statistics: mean, volatility, skewness, kurtosis, tails, CI. Pattern matching and AI interpretation." Highlight terms in cyan.
```

---

## SECTION 2.5: Data Credibility

```
Dark mode trust section, 1200px. Heading "Enterprise-Grade Market Data" white 28px, subhead "institutional sources" gray 14px.

Single glassmorphism card, 3 columns:
- COL 1: Database icon cyan, "Real-Time Market Data", bullets: major US exchanges, CBOE/NYSE/Nasdaq, 15min updates, cross-validated
- COL 2: Shield icon green, "Data Quality", metrics: Coverage 98% (cyan progress bar), Institutional-grade, <1s latency, "Verified" badge
- COL 3: Academic cap purple, "Academic Standard", bullets: Breeden-Litzenberger (1978), SABR calibration, Federal Reserve rates, peer-reviewed

Bottom: Clock icon, timestamp "Dec 6, 2025 4:00 PM ET", green "Live" dot, disclaimer "Data from leading aggregators and FRED" gray 12px italic.
```

---

## SECTION 3: Podcast

```
Dark podcast section, 1200px. Heading "Learn Through Audio" white 32px.

Two equal cards:
- LEFT: Headphones icon cyan, "Quick Intro (5 min)", dark audio player (#181820): cyan play button 48px, progress bar cyan gradient, time "0:00/5:23" monospace, volume control, sound wave visualization
- RIGHT: Microphone icon cyan, "Deep Dive (20 min)", same player design, time "0:00/19:47"

Cards: #1e1e2e, border #2a2a3e, rounded 12px, padding 24px.
```

---

## SECTION 4: Use Cases

```
Dark use cases, 1200px. Heading "What Traders Use This For" white 32px.

3 equal cards (#1e1e2e, 3px colored top border, padding 24px):
1. CYAN border: Shield icon cyan 48px centered, "Risk Management", bullets (cyan dots): tail risk, position sizing, stop losses, asymmetric risk/reward
2. GREEN border: Target icon green 48px, "Strategy Selection", bullets (green dots): optimal strikes, spreads vs naked, mispriced vol, match distribution
3. PURPLE border: Brain icon purple 48px, "Market Sentiment", bullets (purple dots): bullish/bearish bias, track changes, historical patterns, regime changes
```

---

## SECTION 5: How to Use

```
Dark instructions, 1200px. Heading "How to Use" white 32px, subhead "3 simple steps" gray 16px.

3 columns with dotted cyan lines connecting:
1. Cyan circle "1" 64px, dollar icon, "Select Ticker", text: any stock/ETF with options, mockup dropdown "SPY ▼"
2. Cyan circle "2" 64px, calendar icon, "Choose Expiration", text: pick DTE (7-90 days), mockup "30 Days ▼"
3. Cyan circle "3" 64px, rocket icon, "Run Analysis", text: results in 10-30s, mockup button "🚀 Run Analysis" cyan gradient

Number badges: cyan gradient background, white text 32px bold.
```

---

## SECTION 5.5: Disclaimer

```
Dark warning section, 900px. Card: #1e1e2e with red tint overlay, 2px red border (#ff4757) with glow, padding 24px, rounded 8px.

Header: Alert triangle red 32px, "⚠️ Important Disclaimer" white 20px bold, "Please read before using" gray 14px.

Text (gray 14px, line-height 1.6): "Educational and informational purposes ONLY. NOT financial advice, investment recommendation, or solicitation. Distributions are estimates based on models. All investments involve risk, including loss of principal. Past performance doesn't guarantee future results. Consult licensed financial advisor. No liability for decisions based on this info."

3 columns: Book icon cyan "Educational Use | For learning only" | Ban icon red "Not Financial Advice | Consult professionals" | Alert icon orange "Use At Your Risk | No guarantees"

Bottom pill: "By using this tool, you acknowledge these terms" gray 12px, checked checkbox, dark BG #181820.
```

---

## SECTION 6: Input Controls

```
Dark form section, 800px. Card #1e1e2e, border #2a2a3e, rounded 12px, padding 32px, top-to-bottom cyan gradient overlay.

Heading "Configure Your Analysis" white 24px, thin cyan line below.

3 equal input fields (56px height, rounded 8px, BG #0e1117, border #2a2a3e, cyan focus glow):
1. "TICKER SYMBOL" label gray 12px uppercase, input "SPY" white 18px monospace, dollar icon cyan left, helper "Any stock or ETF with options" gray 12px
2. "DAYS TO EXPIRATION (DTE)" label, dropdown "30 Days" white, calendar icon cyan left, chevron right, helper "Target expiration window"
3. "ANALYSIS MODE" label, dropdown "Standard" with blue pill badge, brain icon cyan left, helper "AI interpretation style"

Large CTA button (full width, 64px height, cyan gradient #00d9ff to #0099cc, shadow): "🚀 Run Analysis" dark text 20px bold.

Below: "⚙️ Advanced Settings" gray 14px collapsed.
```

---

## SECTION 7A: Results - PDF Chart

```
Dark results, 1400px. Two columns 65/35 split.

LEFT large card: "SPY Option-Implied PDF (30D)" white 24px, green dot "Live Data", timestamp gray 12px. Chart area #0e1117: X-axis "Strike Price ($)" 550-800, Y-axis "Probability Density" 0-0.025, cyan bell curve (#00d9ff) with gradient fill below, green dashed line at spot $685.69 labeled, green shaded CI zone $674-$710 (rgba(0,255,136,0.15)), dotted bounds, subtle grid #2a2a3e, white tooltip mockup.

RIGHT card: Info icon cyan 24px, "What This Shows" white 20px, text gray 14px: "Market's belief where SPY will trade. Peak=most likely (~$690), Width=uncertainty (±$11), Shape=bearish tilt. Green zone=68% probability (2/3 times)." Cyan highlighted numbers, small arrows to chart, cyan bullet dots.

Both cards: #1e1e2e, border #2a2a3e, rounded 12px, padding 24px.
```

---

## SECTION 7B: Metrics Cards

```
Dark metrics, 1400px. 4 equal cards (#1e1e2e, border #2a2a3e, padding 24px, rounded 8px):

1. CYAN top border 2px: Target icon cyan 24px, "SPOT PRICE" gray 12px uppercase, "$685.69" white 48px monospace, "Current underlying price" gray 12px
2. GREEN top border: Up arrow green 24px, "EXPECTED PRICE" gray, "$692.11" white 48px, "+$6.42↑" green 20px, "+0.94%" green pill, "Risk-neutral mean" gray
3. CYAN top border: Expand arrows cyan 24px, "IMPLIED MOVE" gray, "±3.85%" white 48px, "$660-$710" gray 16px, mini cyan progress bar, "Expected range (1σ)" gray
4. RED top border: Balance scale red 24px, "MARKET BIAS" gray, "Bearish 📉" red 36px, "Skew: -1.73" gray 14px monospace, "Distribution asymmetry" gray

Icons line-style, values monospace, shadow 0 4px 16px rgba(0,0,0,0.2).
```

---

## SECTION 7C: AI Interpretation

```
Dark AI section, 1400px. Card #1e1e2e, border #2a2a3e, padding 32px, rounded 12px.

Header: Robot icon cyan 32px pulse animation, "AI Market Interpretation" white 28px, "Standard Mode" cyan pill badge, "Generated 2 min ago" gray 12px right.

4 numbered sections (40px cyan circle badges, white number 20px bold, dotted cyan connector lines):
1. "Market Sentiment": "PDF shows bearish tilt, peak left of spot. Elevated downside risk vs upside. Cautious positioning." "bearish tilt" red pill
2. "Tail Risk Assessment": "Downside -10% at 8.2%, upside +10% at 5.1%. Asymmetry signals crash protection premium. Kurtosis 0.5=fat tails." Pills "8.2%" "5.1%" cyan, mini bar chart red vs green
3. "Trading Implications": "Favorable: Put spreads, iron condors with bearish skew. Avoid naked calls. 68% CI $674-$710 presents natural strikes." Strategy pills, put spread diagram
4. Green checkmark 40px (not number): "Key Takeaway": "Markets pricing asymmetric downside risk - position accordingly with protective structures." 4px green left border, lighter BG #252530, green glow

Text gray #d0d0d0, 16px, line-height 1.7. "Change Mode" and Copy buttons top right.
```

---

## SECTION 7D: Statistics

```
Dark stats, 1400px. 2 equal columns.

LEFT "Distribution Shape" card: Wave icon cyan 24px. 3 metric rows (label gray left 14px, value white right 24px monospace):
- "Skewness" "-0.15": red gradient progress bar 8px (negative, left-tilted 15%)
- "Excess Kurtosis" "0.50": cyan gradient bar (positive, right of center)
- Mini curve diagram: cyan curve left-skewed, red tint left tail, "Fat Left Tail" label
Insight box bottom: #181820 BG, lightbulb cyan 16px, "Strong bearish tilt - elevated downside risk" white 14px, cyan glow

RIGHT "Tail Risk Analysis" card: Alert triangle orange 24px. 3 rows:
- "Prob(+10%)" "5.1%" green, green gradient bar 5% filled
- "Prob(-10%)" "8.2%" red, red gradient bar 8% filled
- "Tail Ratio (Down/Up)" "1.61x" orange, "Asymmetric risk" gray 12px
Insight box: warning triangle red 16px, "Elevated downside tail risk" white, red glow

Both cards: #1e1e2e, border #2a2a3e, padding 24px, rounded 12px, row height 56px, 16px spacing.
```

---

## SECTION 7E: Probability Table

```
Dark table, 1400px. Card #1e1e2e, border #2a2a3e, rounded 12px.

Header (above table): Table icon cyan 24px, "Strike Probabilities" white 24px, "Cumulative probability at key levels" gray 14px.

Table: Column headers (#181820 BG, gray uppercase 12px bold, 2px cyan bottom border, padding 16px 12px): "Strike | P(S < K) | P(S > K) | Distance from Spot"

10 data rows (56px height, padding 12px 16px, white text 16px monospace, border bottom 1px #2a2a3e, hover: lighten to #252530 + 2px cyan left border):
- ATM row (highlighted #252530, 3px green left border): "$685 | 50.0% | 50.0% | ±0.0%" green pill
- OTM put: "$660 | 15.8% | 84.2% | -3.7%" red pill, subtle cyan progress bars behind percentages
- OTM call: "$710 | 84.2% | 15.8% | +3.5%" green pill
[7 more rows varying $650-$720]

Pills: negative=red bg rgba(255,71,87,0.2), positive/zero=green, rounded 4px, padding 4px 8px, 12px font.
```

---

## SECTION 8: Footer

```
Dark footer, 1200px. BG #0e1117, top border 1px #2a2a3e, padding 48px/32px.

3 equal columns:
- LEFT: Probability curve icon cyan 32px, "Decode market expectations" gray 14px italic, GitHub/LinkedIn icons gray 20px (cyan hover), 12px spacing
- CENTER: "Resources" white 14px semibold, links (gray 14px, cyan hover, 8px spacing): "View on GitHub | Full Documentation | About Model | Contact"
- RIGHT: "Built With" white 14px semibold, tech pills (8px padding, 4px rounded, semi-transparent): "Python" blue | "Streamlit" red | "Plotly" cyan | "Ollama AI" purple

Below (centered): Thin line 1px #2a2a3e, 24px margin

Legal row: Red triangle 16px, "⚠️ DISCLAIMER: For educational purposes only. Not financial advice. All investments involve risk." gray 12px, dark box #181820, 12px padding, rounded

Copyright row: Left "© 2025 Option-Implied PDF Visualizer" | Center "Licensed under MIT" | Right "Built with Claude Code" cyan (all gray 11px)

Column spacing 32px.
```

---

## Loading State

```
Dark loading overlay, 500×350px, centered. Card #1e1e2e glassmorphism blur, border 1px #2a2a3e with animated cyan glow pulse, rounded 12px, padding 40px, shadow 0 16px 48px rgba(0,0,0,0.5).

Content centered: Circular spinner 64px (cyan gradient ring rotating 2s loop, probability curve icon center 16px) | "Analyzing option chain..." white 18px | 6 horizontal progress dots 12px: "Data" (active cyan filled glowing) | "Risk-Free" (completed green checkmark ✓) | "PDF" (active pulsing) | "Stats" (pending gray outline) | "Patterns" (pending) | "AI" (pending), labels below gray 10px | "~15-30 seconds" gray 12px bottom

Animations: smooth rotation, traveling border glow, opacity pulse 0.95-1.0, step fill left-to-right 300ms.
```

---

## Usage for Gemini

**How to use**: Copy each section's prompt → Paste in Gemini → Request "Generate this as a high-fidelity UI mockup screenshot" → Download PNG → Repeat for all sections

**Pro tips**:
- Specify "at [width]px width" for consistent sizing
- Emphasize "dark theme" and "realistic production-ready design"
- Request variations with "adjust [element]" or "make it [darker/lighter]"
- Generate multiple sections in one Gemini conversation for consistency

**10 Sections Total**: Hero | What is PDF | Data Credibility | Podcast | Use Cases | How to Use | Disclaimer | Input Controls | Results (5 parts: Chart, Metrics, AI, Stats, Table) | Footer | Loading State (bonus)

All sections use same color palette (#0e1117 BG, #1e1e2e surface, #00d9ff cyan, #00ff88 green, #ff4757 red, #fafafa white, #a0a0a0 gray, #2a2a3e border) and glassmorphism styling.
