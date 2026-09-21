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
        swadesi: {
          page: '#FDFBF7',
          secondary: '#F8F5EF',
          card: '#FFFFFF',
          heading: '#1E293B',
          text: '#64748B',
          muted: '#94A3B8',
          saffron: '#C2410C',
          saffronHover: '#9A3412',
          saffronLight: '#FFF1E8',
          green: '#15803D',
          amber: '#D97706',
          danger: '#DC2626',
          border: '#E7E2DA',
          divider: '#ECE8E1',
          navy: '#1E293B',
          ashoka: '#1E3A8A',
        },
        cyber: {
          dark: '#FDFBF7',
          base: '#F8F5EF',
          card: '#FFFFFF',
          cardHover: '#F8F5EF',
          border: '#E7E2DA',
          borderGlow: '#C2410C',
          accent: '#C2410C',
          neon: '#15803D',
          warning: '#D97706',
          danger: '#DC2626',
          violet: '#C2410C',
          indigo: '#1E293B',
        }
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-glow': 'pulseGlow 2.5s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.6', filter: 'drop-shadow(0 0 10px rgba(194,65,12,0.3))' },
          '50%': { opacity: '1.0', filter: 'drop-shadow(0 0 20px rgba(194,65,12,0.5))' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
      boxShadow: {
        'swadesi-card': '0 1px 3px 0 rgba(30, 41, 59, 0.05), 0 1px 2px -1px rgba(30, 41, 59, 0.05)',
        'swadesi-hover': '0 10px 25px -5px rgba(194, 65, 12, 0.1), 0 8px 10px -6px rgba(194, 65, 12, 0.05)',
        'swadesi-saffron': '0 4px 14px 0 rgba(194, 65, 12, 0.25)',
        'swadesi-green': '0 4px 14px 0 rgba(21, 128, 61, 0.25)',
        'swadesi-alert': '0 4px 16px 0 rgba(220, 38, 38, 0.25)',
        'neon-cyan': '0 4px 14px 0 rgba(194, 65, 12, 0.25)',
        'neon-emerald': '0 4px 14px 0 rgba(21, 128, 61, 0.25)',
        'neon-crimson': '0 4px 16px 0 rgba(220, 38, 38, 0.25)',
        'neon-amber': '0 4px 14px 0 rgba(217, 119, 6, 0.25)',
        'cyber-card': '0 1px 3px 0 rgba(30, 41, 59, 0.05)',
      }
    },
  },
  plugins: [],
}
