/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#070a10',
          base: '#0a0d14',
          card: '#0f1422',
          cardHover: '#141c30',
          border: '#1e293b',
          borderGlow: '#06b6d4',
          accent: '#06b6d4',
          neon: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
          violet: '#8b5cf6',
          indigo: '#6366f1',
        }
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-glow': 'pulseGlow 2.5s ease-in-out infinite',
        'scanline': 'scanline 6s linear infinite',
        'shimmer': 'shimmer 2.5s infinite linear',
        'float': 'float 3s ease-in-out infinite',
        'radar-sweep': 'radarSweep 4s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.4', filter: 'drop-shadow(0 0 15px rgba(6,182,212,0.4))' },
          '50%': { opacity: '0.9', filter: 'drop-shadow(0 0 30px rgba(6,182,212,0.8))' },
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(1000%)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-6px)' },
        },
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        }
      },
      boxShadow: {
        'neon-cyan': '0 0 25px -3px rgba(6, 182, 212, 0.45)',
        'neon-emerald': '0 0 25px -3px rgba(16, 185, 129, 0.45)',
        'neon-crimson': '0 0 30px -3px rgba(239, 68, 68, 0.55)',
        'neon-amber': '0 0 25px -3px rgba(245, 158, 11, 0.45)',
        'neon-violet': '0 0 25px -3px rgba(139, 92, 246, 0.45)',
        'cyber-card': '0 8px 32px 0 rgba(0, 0, 0, 0.45)',
      }
    },
  },
  plugins: [],
}
