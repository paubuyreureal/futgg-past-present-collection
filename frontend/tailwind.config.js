/**
 * Tailwind CSS configuration file.
 * 
 * Configures the Tailwind utility-first CSS framework:
 * - Defines content paths where Tailwind should scan for class names
 * - Customizes theme (colors, fonts, spacing, etc.) if needed
 * - Extends default Tailwind utilities with project-specific design tokens
 */

/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        // Add custom theme extensions here if needed
        // colors: { ... },
        // fonts: { ... },
      },
    },
    plugins: [],
  }