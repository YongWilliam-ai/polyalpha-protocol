/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        dark:           "#0B0A10",
        surface:        "#16141E",
        "surface-hover":"#1E1B29",
        accent:         "#FF4500",
        success:        "#00E676",
        warning:        "#FFB300",
      },
      fontFamily: {
        mono: ["Fira Code", "JetBrains Mono", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
