/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Original color scheme (kebab-case for compatibility)
        'bg-primary': '#0e1117',
        'bg-surface': '#1e1e2e',
        'bg-highlight': '#252530',
        'bg-darker': '#181820',
        'text-primary': '#fafafa',
        'text-secondary': '#d0d0d0',
        'text-muted': '#a0a0a0',
        'accent-cyan': '#00d9ff',
        'accent-green': '#00ff88',
        'accent-red': '#ff4757',
        'accent-orange': '#ffa502',
        'accent-purple': '#a55eea',
        'border-default': '#2a2a3e',
        // Gemini version (camelCase)
        primary: '#0e1117',
        surface: '#1e1e2e',
        surfaceHighlight: '#2a2a3e',
        accent: {
          cyan: '#00d9ff',
          green: '#00ff88',
          purple: '#a55eea',
          red: '#ff4757',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass': 'linear-gradient(180deg, rgba(30, 30, 46, 0.7) 0%, rgba(30, 30, 46, 0.4) 100%)',
      },
      boxShadow: {
        glass: '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glow-cyan': '0 0 20px rgba(0, 217, 255, 0.3)',
        'glow-green': '0 0 20px rgba(0, 255, 136, 0.3)',
      },
      animation: {
        blob: 'blob 10s infinite',
        shimmer: 'shimmer 2s linear infinite',
        fadeIn: 'fadeIn 0.8s ease-out',
        slideUp: 'slideUp 0.6s ease-out',
        'pulse-custom': 'pulseCustom 3s ease-in-out infinite',
        glow: 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        blob: {
          '0%': { transform: 'translate(0px, 0px) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
          '100%': { transform: 'translate(0px, 0px) scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' }
        },
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseCustom: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 5px rgba(0, 217, 255, 0.3)' },
          '50%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.6)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
