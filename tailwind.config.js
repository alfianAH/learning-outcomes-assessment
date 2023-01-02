/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./pi_area/models.py",
    './mata_kuliah_semester/forms.py'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', ...defaultTheme.fontFamily.sans],
      },
      minWidth: {
        '72': '18rem',
        '96': '24rem',
        '1/2': '50%',
      }
    },
  },
  plugins: [],
}
