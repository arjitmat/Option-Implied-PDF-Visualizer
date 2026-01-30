# Gemini 3 - React Component Prompts
## Option-Implied PDF Visualizer

**Purpose**: Generate production-ready React components with Revolut/Linear/Stripe quality
**Tech Stack**: React 18, Framer Motion, Tailwind CSS v3, Plotly.js
**Model**: Gemini 3 (code generation mode)

---

## 🎨 Design System Reference

Copy this context into every Gemini 3 prompt:

```
DESIGN SYSTEM:
- Colors: bg-primary #0e1117, bg-surface #1e1e2e, accent-cyan #00d9ff, accent-green #00ff88
- Glass effect: rgba(30,30,46,0.6) + backdrop-filter blur(40px) saturate(180%)
- Shadows: Multi-layer (0 0 0 1px rgba(0,0,0,0.05), 0 8px 24px rgba(0,0,0,0.2))
- Border radius: 16px (cards), 8px (inputs), 24px (modals)
- Animations: 200-400ms, cubic-bezier(0.4, 0, 0.2, 1), hardware-accelerated (transform/opacity)
- Typography: Inter (UI), JetBrains Mono (data)
- Spacing: 4px base grid
```

---

## 1. Hero Section (Revolut Style)

**Gemini 3 Prompt:**

```
Generate a React component for a premium dark-mode hero section.

REQUIREMENTS:
- Cursor-tracking radial gradient background (follows mouse position)
- Central glassmorphic card with 3D tilt effect (perspective transform)
- Framer Motion staggered animations on mount
- Animated gradient text for title
- Floating particle system (small cyan dots drifting)

COMPONENT STRUCTURE:
- useState for cursor position (mouseX, mouseY)
- useEffect with mousemove listener
- motion.div with initial/animate props
- CSS variables for --mouse-x and --mouse-y
- Glassmorphism: backdrop-filter blur(60px), rgba background

CODE FEATURES:
- Particle system using <motion.div> array with random starting positions
- Magnetic hover effect (card follows cursor within radius)
- Text gradient using bg-clip-text
- Smooth easing: type: "spring", stiffness: 50

OUTPUT: Full React component with:
1. Import statements (react, framer-motion)
2. Component function with all hooks
3. Inline Tailwind classes
4. Return JSX with animations
5. Export default
```

---

## 2. Metric Cards (Netflix Reveal Style)

**Gemini 3 Prompt:**

```
Generate 4 animated metric cards in a responsive grid.

DATA STRUCTURE:
const metrics = [
  { label: 'Spot Price', value: '$685.69', color: 'cyan', change: '+0.3%' },
  { label: 'Expected Price', value: '$689.51', color: 'green', change: '+$3.82' },
  { label: 'Implied Move', value: '±3.44%', color: 'cyan', range: '$660-$710' },
  { label: 'Skewness', value: '-0.73', color: 'red', meaning: 'Bearish' }
]

COMPONENT FEATURES:
- map() over metrics with index for stagger delay
- Framer Motion: initial={{ opacity: 0, y: 20 }}, animate={{ opacity: 1, y: 0 }}
- transition={{ delay: i * 0.1 }}
- Glass card with colored top border (border-t-2)
- Hover effect: scale(1.05), shadow expansion, glow increase
- Count-up animation for numbers using framer-motion variants

STYLING:
- Grid: grid grid-cols-1 md:grid-cols-4 gap-4
- Card: glass-card class + border-accent-{color}
- Value: text-3xl font-mono font-bold
- Label: text-xs uppercase tracking-wide opacity-60

OUTPUT: React component with metrics array, map function, motion.div for each card
```

---

## 3. Interactive PDF Chart (Plotly + Framer Motion)

**Gemini 3 Prompt:**

```
Generate a Plotly chart wrapper with glassmorphic container and loading states.

PROPS:
interface ChartProps {
  strikes: number[]
  probabilities: number[]
  spotPrice: number
  loading: boolean
}

FEATURES:
- Framer Motion container with fade-in animation
- Loading skeleton with shimmer effect
- Plotly responsive chart with dark theme
- Gradient line (cyan→green based on probability)
- Fill below curve with radial gradient
- Spot price vertical line with floating badge
- Glass container with hover lift effect

PLOTLY CONFIG:
data: [{
  x: strikes,
  y: probabilities,
  type: 'scatter',
  mode: 'lines',
  fill: 'tozeroy',
  line: { color: '#00d9ff', width: 3 },
  fillcolor: 'rgba(0, 217, 255, 0.1)'
}]

layout: {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { color: '#fafafa', family: 'Inter' },
  xaxis: { title: 'Strike Price', gridcolor: '#2a2a3e' },
  yaxis: { title: 'Probability Density', gridcolor: '#2a2a3e' }
}

OUTPUT: Complete component with loading state, Plotly import, framer-motion wrapper
```

---

## 4. AI Insights Card (Apple Card Style)

**Gemini 3 Prompt:**

```
Generate a premium AI insights card with sequential reveal animations.

DATA:
const insights = [
  { title: 'Market Sentiment', content: '...', confidence: 87 },
  { title: 'Tail Risk', downside: 8.2, upside: 5.1 },
  { title: 'Strategy', suggestions: ['Put Spreads', 'Iron Condors'] },
  { title: 'Key Takeaway', highlight: '...' }
]

COMPONENT FEATURES:
- Framer Motion staggerChildren animation
- Each insight section has icon (3D numbered badge)
- Confidence meter (horizontal gradient bar)
- Inline pill badges for key terms
- Expandable sections (AnimatePresence for height transition)
- Copy-to-clipboard button (appears on hover)

ANIMATIONS:
- Parent: staggerChildren: 0.2
- Children: opacity 0→1, y 20→0
- Confidence bar: width 0%→87%, 1s delay
- Pills: scale(0.9)→scale(1) on hover

STYLING:
- Ultra-premium glass card (border-radius: 32px)
- Mesh gradient background (animated slow morph)
- Section dividers (1px rgba(255,255,255,0.08))
- Text highlights in colored pills with glow

OUTPUT: Component with AnimatePresence, motion variants, useState for expand/collapse
```

---

## 5. Input Controls (Linear Speed)

**Gemini 3 Prompt:**

```
Generate keyboard-optimized input controls with command palette style.

INPUTS:
1. Ticker autocomplete (with fuzzy search)
2. Days to expiry selector (segmented control)
3. Analysis mode tabs (Standard/Conservative/Aggressive/Educational)

FEATURES:
- Focus management with useRef and keyboard navigation
- Cmd+K to open (useEffect with keydown listener)
- Autocomplete dropdown (AnimatePresence for mount/unmount)
- Selected state with smooth slide animation
- Validation with shake animation on error
- Loading state with gradient animation

AUTOCOMPLETE:
- useState for query and suggestions
- Filter logic: ticker.toLowerCase().includes(query.toLowerCase())
- Render dropdown with motion.div (initial={{ opacity: 0, y: -10 }})
- Arrow key navigation (useState for selectedIndex)

SEGMENTED CONTROL:
- Active segment has gradient background
- Smooth slide animation using layoutId="activeSegment"
- Icons for each mode (animated on select)

SUBMIT BUTTON:
- Animated gradient background (infinite loop)
- Ripple effect on click (expanding circle, framer-motion)
- Loading state: spinner + text change

OUTPUT: Form component with all inputs, keyboard shortcuts, framer-motion animations
```

---

## 6. Data Table (Stripe Quality)

**Gemini 3 Prompt:**

```
Generate a scannable data table with inline animations and sorting.

DATA:
const strikes = [
  { strike: 680, probDown: 0.42, probUp: 0.58, iv: 18.5, distance: -4.54 },
  { strike: 685, probDown: 0.50, probUp: 0.50, iv: 17.2, distance: 0 }, // ATM
  ...
]

FEATURES:
- Sticky header (position: sticky, top: 0)
- Zebra striping (rgba(255,255,255,0.02) every other row)
- ATM row highlighted (cyan tint, left border, bold)
- Hover effect (lift + glow + left border)
- Sortable columns (click header, animated reorder)
- Mini progress bars in probability cells
- Pill badges for distance values (colored by sign)

SORTING:
- useState for sortKey and sortDirection
- onClick handler on headers
- Animated reordering using AnimatePresence + layoutId
- Arrow icon rotation (0deg→180deg)

ROW ANIMATIONS:
- Map with motion.tr
- layout prop for smooth reordering
- initial={{ opacity: 0 }} animate={{ opacity: 1 }}
- transition={{ delay: index * 0.05 }}

STYLING:
- Table container: glass-card, overflow-hidden
- Cells: px-6 py-4, monospace for numbers
- Progress bars: absolute position, gradient width
- Hover: bg-white/5, shadow-glow-cyan

OUTPUT: Table component with sorting logic, framer-motion rows, responsive design
```

---

## 7. Cursor-Tracking Background

**Gemini 3 Prompt:**

```
Generate a cursor-tracking radial gradient overlay component.

IMPLEMENTATION:
- useEffect with mousemove listener
- Calculate percentage position: (e.clientX / window.innerWidth) * 100
- Update CSS variables: document.body.style.setProperty('--mouse-x', x + '%')
- Radial gradient uses var(--mouse-x) and var(--mouse-y)

CSS:
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(
    circle 600px at var(--mouse-x, 50%) var(--mouse-y, 50%),
    rgba(0, 217, 255, 0.05),
    transparent 40%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

body.cursor-active::before {
  opacity: 1;
}

OUTPUT: React component with useEffect, cleanup function, CSS-in-JS or index.css code
```

---

## 8. Particle System

**Gemini 3 Prompt:**

```
Generate a floating particle background using Framer Motion.

SYSTEM:
- Array of 50 particles with random x, y, scale, duration
- Each particle is motion.div with animate loop
- Infinite animation: y offset drifting, opacity fade
- Blur filter for depth effect

CODE:
const particles = Array.from({ length: 50 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  scale: Math.random() * 0.5 + 0.5,
  duration: Math.random() * 10 + 10
}))

ANIMATION:
<motion.div
  animate={{
    y: [0, -30, 0],
    opacity: [0.2, 0.5, 0.2]
  }}
  transition={{
    duration: particle.duration,
    repeat: Infinity,
    ease: "linear"
  }}
/>

STYLING:
- Absolute positioning
- Cyan/green dots (4px, 6px, 8px sizes)
- Blur: filter blur(2px)
- Pointer-events: none

OUTPUT: Particle component with mapped array, framer-motion infinite animations
```

---

## 🚀 Usage Instructions

1. **Copy design system** (top section) + specific prompt
2. **Paste into Gemini 3** with: "Generate React component code for this:"
3. **Request improvements**: "Add TypeScript types", "Make more performant", "Add accessibility"
4. **Iterate**: Ask for variations, edge cases, responsive breakpoints
5. **Integrate**: Copy generated code into `frontend/src/components/`

**Pro Tips:**
- Ask for "complete working code with all imports"
- Request "Tailwind v3 compatible classes"
- Specify "optimized for 60fps animations"
- Get "dark theme variants"

---

## 📦 Required Dependencies

Already installed in project:
```json
{
  "react": "^18.3.1",
  "framer-motion": "^11.11.17",
  "react-plotly.js": "^2.6.0",
  "plotly.js": "^2.35.2",
  "axios": "^1.7.9"
}
```

Tailwind config already set up in `tailwind.config.js` with custom colors.

---

## ✅ Quality Checklist

Generated code should have:
- ✅ All imports at top
- ✅ TypeScript interfaces (optional but preferred)
- ✅ Proper Tailwind v3 classes
- ✅ Framer Motion animations (200-400ms timing)
- ✅ Cleanup functions in useEffect
- ✅ Responsive breakpoints (md:, lg:)
- ✅ Accessibility attributes (aria-labels)
- ✅ Performance optimization (React.memo if needed)
- ✅ Export default at bottom

**Result**: Production SaaS quality, $50/month product feel, Revolut/Linear polish
