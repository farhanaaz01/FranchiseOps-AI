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
        dark: {
          bg: '#0E1013',
          panel: '#171A20',
          'panel-alt': '#1D212A',
          hairline: '#262B35',
          border: '#262B35',
          hover: '#222733',
        },
        brand: {
          primary: '#6C8CFF',
          secondary: '#4FAE7C',
        },
        status: {
          healthy: '#4FAE7C',
          'healthy-bg': 'rgba(79, 174, 124, 0.12)',
          risk: '#E8A33D',
          'risk-bg': 'rgba(232, 163, 61, 0.12)',
          critical: '#D0555A',
          'critical-bg': 'rgba(208, 85, 90, 0.14)',
          info: '#6C8CFF',
          'info-bg': 'rgba(108, 140, 255, 0.12)',
        },
        text: {
          primary: '#EDEFF3',
          dim: '#8992A6',
          faint: '#5C6478',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Space Grotesk', 'Inter', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },
      borderRadius: {
        card: '12px',
        panel: '14px',
      },
    },
  },
  plugins: [],
}
