import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    proxy: Object.fromEntries(['/api', '/health', '/ready', '/metrics'].map(path => [path, 'http://127.0.0.1:8000'])),
  },
});
