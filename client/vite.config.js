  import { fileURLToPath, URL } from 'node:url'

  import { defineConfig } from 'vite'
  import vue from '@vitejs/plugin-vue'

  // https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/admin': {
        target: 'http://localhost:8000',  // Прокси для админки
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'http://localhost:8000',  // Прокси для статики
        changeOrigin: true,
        secure: false,
      },
    },
  },
})

