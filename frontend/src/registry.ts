import { type Component, type InjectionKey, inject } from 'vue'

import BoolCell from './components/cells/BoolCell.vue'
import TagsCell from './components/cells/TagsCell.vue'
import TextCell from './components/cells/TextCell.vue'
import { CellComponent } from './shared'

/** Component name -> component. The backend sends the names (`Cell.component`). */
interface Registry {
  cells: Record<string, Component>
}

const builtIn: Registry = {
  /** Backend sends `Cell(CellComponent.TEXT, props)`, frontend renders `cells.text`. */
  cells: {
    [CellComponent.Text]: TextCell,
    [CellComponent.Bool]: BoolCell,
    [CellComponent.Tags]: TagsCell,
  },
}

const registryKey: InjectionKey<Registry> = Symbol('crudlink registry')

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
  return (name) => resolve(registry.cells, name, TextCell, 'cell')
}
