/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        dark:           "#050505",   // EdgeBuild: near-true black
        surface:        "#0d0d0d",   // card background
        "surface-hover":"#141414",   // card hover
        accent:         "#ccff00",   // EdgeBuild Neon/Acid Green (primary accent)
        "accent-dark":  "#99cc00",   // hover state for neon buttons
        success:        "#00E676",
        warning:        "#FFB300",
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"],
        sans: ["Inter", "Space Grotesk", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
