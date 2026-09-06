/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        earth: {
          ground: '#F5F2EB',
          surface: '#EDE7DA',
          border: '#D5CCBA',
          dark: '#241C16',
          muted: '#63574A',
        },
        wheat: {
          gold: '#C68A1B',
          dark: '#99680A',
          tint: '#FCF6E8',
          border: '#E8C882',
        },
        ajrak: {
          black: '#121722',
          slate: '#2C3549',
          surface: '#1A2130',
        },
        water: {
          tone: '#18639C',
          surface: '#EAF3FA',
          border: '#A5CBE4',
          dark: '#10446B',
        },
        ochre: {
          alert: '#B24032',
          surface: '#FBEDE9',
          border: '#E6A69E',
          dark: '#7A261C',
        }
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'system-ui', '-apple-system', 'sans-serif'],
        urdu: ['"Noto Nastaliq Urdu"', '"Jameel Noori Nastaliq"', 'serif'],
      },
      lineHeight: {
        'urdu': '2.2',
        'urdu-tight': '1.9',
      }
    },
  },
  plugins: [],
}
