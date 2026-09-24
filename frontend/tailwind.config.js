/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        legal: {
          50: '#f2f8f5',
          100: '#e1f0e9',
          200: '#c5e1d4',
          300: '#9bc9b6',
          400: '#6da993',
          500: '#4a8d75',
          600: '#38715d',
          700: '#2d5b4c',
          800: '#264a3e',
          900: '#1b4332',
          950: '#0d241b',
        },
        parchment: {
          50: '#fdfbf7',
          100: '#f9f5ed',
          200: '#f2ebd9',
          300: '#e7dabc',
          400: '#d9c399',
        }
      },
      fontFamily: {
        serif: ['Merriweather', 'Georgia', 'serif'],
        urdu: ['Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Urdu Typesetting', 'Tahoma', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
