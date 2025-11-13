/**
 * Vite configuration file.
 * 
 * Configures the Vite build tool for the React frontend:
 * - Sets up the React plugin for JSX transformation and Fast Refresh
 * - Defines development server settings (port, proxy for API calls)
 * - Configures build output directory and optimization settings
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  server: {
    port: 3000,
    proxy: {
      // Proxy API requests to FastAPI backend during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})