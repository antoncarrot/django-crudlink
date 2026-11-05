<script setup lang="ts">
import Fieldset from 'openvue/fieldset'
import { computed } from 'vue'

import { type LayoutNode, LayoutType } from '../shared'

const props = defineProps<{
  node: LayoutNode
  /** The field is there to render: the ones that aren't take no place in the layout. */
  hasField: (fieldName: string) => boolean
}>()

// the form or detail page renders the fields, the layout only places them
defineSlots<{
  field(props: { fieldName: string }): unknown
}>()

/** A field that is there, or an element with one inside. */
function isShown(node: LayoutNode): boolean {
  if (node.type === LayoutType.Field) return node.field !== null && props.hasField(node.field)
  return node.children.some(isShown)
}

// no empty row column or fieldset for fields that aren't there
const children = computed(() => props.node.children.filter(isShown))
// row children share the width by their `cols`
const rowColumns = computed(() => children.value.map((child) => `minmax(0, ${child.cols}fr)`).join(' '))
</script>

<template>
  <slot v-if="node.type === LayoutType.Field && node.field" name="field" :field-name="node.field" />
  <Fieldset v-else-if="node.type === LayoutType.Fieldset" :legend="node.label ?? undefined">
    <div class="layout-stack">
      <CrudLayoutNode v-for="(child, index) in children" :key="index" :node="child" :has-field="hasField">
        <template #field="{ fieldName }"><slot name="field" :field-name="fieldName" /></template>
      </CrudLayoutNode>
    </div>
  </Fieldset>
  <div v-else-if="node.type === LayoutType.Row" class="layout-row" :style="{ gridTemplateColumns: rowColumns }">
    <CrudLayoutNode v-for="(child, index) in children" :key="index" :node="child" :has-field="hasField">
      <template #field="{ fieldName }"><slot name="field" :field-name="fieldName" /></template>
    </CrudLayoutNode>
  </div>
  <div v-else class="layout-stack">
    <CrudLayoutNode v-for="(child, index) in children" :key="index" :node="child" :has-field="hasField">
      <template #field="{ fieldName }"><slot name="field" :field-name="fieldName" /></template>
    </CrudLayoutNode>
  </div>
</template>

<style scoped lang="scss">
@layer crudlink {
  .layout-stack {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .layout-row {
    display: grid;
    gap: 1rem;
    align-items: start;

    @media (max-width: 640px) {
      grid-template-columns: 1fr !important;
    }
  }
}
</style>
