import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0a0f0d",
          2: "#0d1a16",
        },
        surface: {
          DEFAULT: "#0f1714",
          2: "#121d1a",
          3: "#0f2320",
        },
        border: {
          DEFAULT: "rgba(255,255,255,0.10)",
          soft: "rgba(255,255,255,0.06)",
        },
        text: {
          DEFAULT: "#e8f7f2",
          muted: "rgba(232,247,242,0.70)",
          soft: "rgba(232,247,242,0.55)",
        },
        accent: {
          DEFAULT: "#0ea5a2",
          2: "#34d399",
          3: "#99f6e4",
        },
        danger: {
          DEFAULT: "#fb7185",
        },
        warning: {
          DEFAULT: "#fbbf24",
        },
        success: {
          DEFAULT: "#34d399",
        },
        pitch: {
          DEFAULT: "#0d4d3d",
          light: "#136f58",
          fg: "#e8f7f2",
        },
      },
    },
  },
  plugins: [],
};

export default config;
