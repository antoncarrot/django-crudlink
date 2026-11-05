import { type Component, type InjectionKey, inject, type Plugin } from 'vue'

import BoolCell from './components/cells/BoolCell.vue'
import FallbackCell from './components/cells/FallbackCell.vue'
import LinkCell from './components/cells/LinkCell.vue'
import TagsCell from './components/cells/TagsCell.vue'
import TextCell from './components/cells/TextCell.vue'
import { CellComponent } from './shared'

/** Custom components of an app, added to the built-in ones. */
export interface CrudlinkRegistryOptions {
  /** Custom cell components, used by `@column(component="badge")` / `Cell("badge", ...)`. */
  cells?: Record<string, Component>
}

/** Component name -> component. The backend sends the names (`Cell.component`). */
interface Registry {
  cells: Record<string, Component>
}

const builtIn: Registry = {
  /** Backend sends `Cell(CellComponent.TEXT, props)`, frontend renders `cells.text`. */
  cells: {
    [CellComponent.Text]: TextCell,
    [CellComponent.Link]: LinkCell,
    [CellComponent.Bool]: BoolCell,
    [CellComponent.Tags]: TagsCell,
  },
}

const registryKey: InjectionKey<Registry> = Symbol('crudlink registry')

/** Vue plugin that adds custom cell components to an app. `createCrudlinkApp` installs it. */
export function crudlinkRegistry(options: CrudlinkRegistryOptions = {}): Plugin {
  const registry: Registry = {
    cells: { ...builtIn.cells, ...options.cells },
  }
  return { install: (app) => app.provide(registryKey, registry) }
}

function resolve(components: Record<string, Component>, name: string, fallback: Component, kind: string): Component {
  // own keys only, so a name like "constructor" doesn't resolve to an Object.prototype member
  const component = Object.hasOwn(components, name) ? components[name] : undefined
  if (!component) {
    console.warn(`[crudlink] ${kind} component "${name}" is not registered`)
    return fallback
  }
  return component
}

/** Cell component by name, from the app's registry (the built-in ones outside a crudlink app). */
export function useCellComponent(): (name: string) => Component {
  const registry = inject(registryKey, builtIn)
  return (name) => resolve(registry.cells, name, FallbackCell, 'cell')
}
