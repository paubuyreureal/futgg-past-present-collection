/**
 * PostCSS configuration file.
 * 
 * Configures PostCSS plugins for CSS processing:
 * - Tailwind CSS: Transforms Tailwind utility classes into CSS
 * - Autoprefixer: Automatically adds vendor prefixes for browser compatibility
 * Used by Vite during development and build processes
 */

export default {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  }