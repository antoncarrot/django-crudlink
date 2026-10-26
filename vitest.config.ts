import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

// Frontend unit tests, separate from vite.config.ts (which builds the prebuilt bundles per mode).
export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    include: ['frontend/src/**/*.test.ts'],
    restoreMocks: true,
    unstubGlobals: true,
  },
})
