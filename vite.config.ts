import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// Prebuilt bundles shipped inside the python package, loaded with {% static %}.
// One self-contained file per bundle (no hashes, no shared chunks), so Django
// static storage can serve and hash them as is. Build one bundle per mode:
//   vite build --mode crud  -> crud.js + crud.css
//   vite build --mode site  -> site.js + site.css
export default defineConfig(({ mode }) => {
  const bundle = mode === 'site' ? 'site' : 'crud'
  return {
    plugins: [vue()],
    base: './',
    build: {
      outDir: fileURLToPath(new URL('./django_crudlink/static/django_crudlink', import.meta.url)),
      emptyOutDir: false,
      cssCodeSplit: false,
      rolldownOptions: {
        input: fileURLToPath(new URL(`./frontend/entries/${bundle}.ts`, import.meta.url)),
        output: {
          entryFileNames: `${bundle}.js`,
          assetFileNames: `${bundle}[extname]`,
        },
      },
    },
  }
})
