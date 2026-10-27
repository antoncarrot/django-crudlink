import { createInertiaApp } from '@inertiajs/vue3'
import Material from '@openvue/themes/material'
import OpenVue from 'openvue/config'
import { type Component, createApp, type DefineComponent, h } from 'vue'

import BaseListPage from './pages/BaseListPage.vue'
import { PageComponent } from './shared'

export interface CrudlinkAppOptions {
  /** Resolve project pages. Crudlink pages (BaseListPage, ...) are resolved first. */
  resolve?: (name: string) => DefineComponent | undefined
  /** Persistent layout wrapping every page (full site mode). */
  layout?: Component
  /** Root element id, defaults to the id of the `<script data-page>` element or "app". */
  id?: string
}

/**
 * Root id rendered by the backend (`CRUDLINK_ROOT_ID`), read from `<script data-page="{id}" type="application/json">`.
 *
 * On a full page load the server puts the first page (component, props, url, version) as JSON into that script,
 * next to `<div id="{id}">` (`{% crudlink_root %}`, or inertia-django's own template). `createInertiaApp({ id })`
 * reads it once at startup to render the first page without a request, and mounts the app on `#id`. Later visits
 * get the page as a JSON response, the script isn't read again.
 *
 * Inertia doesn't search for the id: it only looks up `script[data-page="{id}"]` for the id it's given (default
 * "app"). The prebuilt bundles can't be configured by the host, so they take the id from the page. `data-page` is
 * Inertia's own attribute, so the id read here is always the one of the element Inertia looks up.
 */
function readRootId(): string {
  const script = document.querySelector<HTMLScriptElement>('script[data-page][type="application/json"]')
  return script?.dataset.page || 'app'
}

/**
 * Keep crudlink styles apart from the host page: CSS variables are `--crudlink-*`
 * (not the `--p-*` of a host PrimeVue), all styles live in `@layer crudlink`, so any
 * unlayered host CSS overrides them, and dark mode is opt-in with `.crudlink-dark`.
 */
const themeOptions = {
  prefix: 'crudlink',
  cssLayer: { name: 'crudlink', order: 'crudlink' },
  darkModeSelector: '.crudlink-dark',
}

/** Backend views render these by `PageComponent` name. */
const crudPages: Record<string, Component> = {
  [PageComponent.List]: BaseListPage,
}

export function createCrudlinkApp(options: CrudlinkAppOptions = {}): Promise<void> {
  return createInertiaApp({
    id: options.id ?? readRootId(),
    layout: options.layout ? () => options.layout : undefined,
    resolve: (name) => {
      // own keys only, so a project page named like an Object.prototype member ("toString") reaches options.resolve
      const crudPage = Object.hasOwn(crudPages, name) ? (crudPages[name] as DefineComponent) : undefined
      const page = crudPage ?? options.resolve?.(name)
      if (!page) {
        throw new Error(`Inertia page not found: ${name}`)
      }
      return page
    },
    setup({ el, App, props, plugin }) {
      createApp({ render: () => h(App, props) })
        .use(plugin)
        .use(OpenVue, { theme: { preset: Material, options: themeOptions } })
        .mount(el)
    },
  })
}
