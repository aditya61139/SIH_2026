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
          bg: '#0D0E11',
          nav: '#0D0E11',
          card: '#1A1C23',
          panel: '#15171C',
          heading: '#FFFFFF',
          body: '#E2E8F0',
          secondary: '#94A3B8',
          muted: '#64748B',
          primary: '#10B981',
          primaryHover: '#059669',
          border: '#2A2E37',
          strongBorder: '#374151',
          divider: '#252830',
          safe: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
          critical: '#DC2626',
        },
        swadesi: {
          page: '#0D0E11',
          secondary: '#15171C',
          card: '#1A1C23',
          heading: '#FFFFFF',
          text: '#E2E8F0',
          muted: '#64748B',
          saffron: '#10B981',
          saffronHover: '#059669',
          saffronLight: 'rgba(16, 185, 129, 0.10)',
          green: '#10B981',
          amber: '#F59E0B',
          danger: '#EF4444',
          border: '#2A2E37',
          divider: '#252830',
          navy: '#FFFFFF',
          ashoka: '#10B981',
        },
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-glow': 'pulseGlow 2.5s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.6', filter: 'drop-shadow(0 0 10px rgba(16,185,129,0.3))' },
          '50%': { opacity: '1.0', filter: 'drop-shadow(0 0 20px rgba(16,185,129,0.5))' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
      boxShadow: {
        'cyber-card': '0 4px 20px -2px rgba(0, 0, 0, 0.45)',
        'cyber-hover': '0 8px 25px -4px rgba(0, 0, 0, 0.6), 0 0 15px -3px rgba(16, 185, 129, 0.15)',
        'neon-emerald': '0 0 15px 0 rgba(16, 185, 129, 0.35)',
        'neon-amber': '0 0 15px 0 rgba(245, 158, 11, 0.35)',
        'neon-crimson': '0 0 15px 0 rgba(239, 68, 68, 0.35)',
      }
    },
  },
  plugins: [],
}
