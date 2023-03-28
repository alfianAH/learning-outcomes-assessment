/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme')

module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
    "./pi_area/models.py",
    './mata_kuliah_semester/forms.py',
    './laporan_cpl/forms.py',
    './staticfiles-cdn/select2/dist/js/select2.min.js'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        'sans': ['Inter', ...defaultTheme.fontFamily.sans],
      },
      minWidth: {
        '20': '5rem',
        '24': '6rem',
        '32': '8rem',
        '36': '9rem',
        '40': '10rem',
        '44': '11rem',
        '48': '12rem',
        '64': '16rem',
        '72': '18rem',
        '96': '24rem',
        '1/2': '50%',
      }
    },
  },
  plugins: [
    require("@tailwindcss/typography")
  ],
}
