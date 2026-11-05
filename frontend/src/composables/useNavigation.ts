import { router, usePage } from '@inertiajs/vue3'
import { computed, type Ref } from 'vue'

import type { CrudlinkSharedProps } from '../shared'

export interface Navigation {
  /** `CRUDLINK_INERTIA_NAVIGATION`: true - SPA navigation, false - full page loads between pages. */
  isInertiaNavigation: Readonly<Ref<boolean>>
  /** Go to another page. */
  visit: (url: string) => void
}

/**
 * The mode from the `crudlink` prop of the current page, in any Inertia app (`createCrudlinkApp` or the host's
 * own). Outside an Inertia app (e.g. BaseList on its own) there is no page: plain links. One for all callers.
 */
const isInertiaNavigation = computed(() =>
  Boolean((usePage().props?.crudlink as CrudlinkSharedProps | undefined)?.inertiaNavigation),
)

/** Schemes a link may have; a relative url takes the page's. Not `javascript:` or `data:`, which run code. */
const safeProtocols = new Set(['http:', 'https:', 'mailto:', 'tel:'])

/** The url is safe to link to. Hrefs come from the backend, which may put user data in a link cell. */
export function isSafeUrl(url: string): boolean {
  try {
    // parsed as the browser does (it drops spaces and tabs in "java\tscript:"); the base only resolves relative urls
    return safeProtocols.has(new URL(url, 'http://localhost').protocol)
  } catch {
    return false
  }
}

function visit(url: string): void {
  if (!isSafeUrl(url)) {
    console.warn(`[crudlink] not visiting an unsafe url: ${url}`)
  } else if (isInertiaNavigation.value) {
    router.visit(url)
  } else {
    window.location.assign(url)
  }
}

/**
 * Moving to another page is a full page load unless the backend enables Inertia
 * navigation, so a host template around crudlink (menu, breadcrumbs) re-renders.
 * Same-page updates (table data) always use Inertia.
 */
export function useNavigation(): Navigation {
  return { isInertiaNavigation, visit }
}
