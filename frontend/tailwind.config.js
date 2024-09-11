/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,jsx,ts,tsx,html}"],
  important: true,
  theme: {
    extend: {
      fontFamily: {
        "Montserrat": ["Montserrat", "sans-serif"],
      },
      colors: {
        primary: "#16BAC5",
        secondary: "#5863F8",
        light: "#5FBFF9",
        bright: "#EFE9F4",
        brightDark: "#F2E8F4",
        brightLight: "#f2edf6",
        dark: "#171D1C",
      },
    },
    corePlugins: {
      preflight: false,
    },
    plugins: [],
  }
}

