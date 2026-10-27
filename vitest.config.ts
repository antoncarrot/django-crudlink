import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

// Frontend unit tests, separate from vite.config.ts (which builds the prebuilt bundles per mode).
export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    include: ['frontend/src/**/*.test.ts'],
    // restoreMocks only undoes vi.spyOn(); clearMocks also empties the calls of shared vi.fn() mocks
    // (the testing/inertia router), so a test doesn't see the calls of the one before
    clearMocks: true,
    restoreMocks: true,
    unstubGlobals: true,
  },
})
