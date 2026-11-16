import { defineConfig } from 'vite';
import { resolve } from 'path';

const apiTarget = process.env.VITE_API_TARGET || 'http://127.0.0.1:8000';
const wsTarget = apiTarget.replace(/^http/, 'ws');

export default defineConfig({
  root: '.',
  publicDir: 'public',
  resolve: {
    alias: {
      '@': resolve(import.meta.dirname || '.', 'src')
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
        secure: false
      },
      '/ws': {
        target: wsTarget,
        ws: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    emptyOutDir: true,
    target: 'es2022'
  }
});
