/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable manual dark mode toggling
  theme: {
    extend: {
      colors: {
        primary: '#1E40AF',
        darkbg: '#0F172A',
        darkcard: '#1E293B'
      }
    },
  },
  plugins: [],
}