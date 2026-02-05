import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./charts/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        "fin-bg": "#0b0f19",
        "fin-surface": "#121826",
        "fin-border": "#1f2a44",
        "fin-accent": "#4f46e5",
        "fin-accent-soft": "#1e1b4b",
        "fin-text": "#e2e8f0",
        "fin-muted": "#94a3b8"
      }
    }
  },
  plugins: []
};

export default config;
