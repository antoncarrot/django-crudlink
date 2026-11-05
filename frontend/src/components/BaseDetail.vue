<script setup lang="ts">
import type { BaseDetailProps } from '../types'
import CellRenderer from './CellRenderer.vue'
import CrudLayoutNode from './CrudLayoutNode.vue'

const props = defineProps<BaseDetailProps>()

// own keys only, so a layout name like "constructor" isn't an Object.prototype member
function hasField(fieldName: string): boolean {
  return Object.hasOwn(props.fields, fieldName)
}
</script>

<template>
  <CrudLayoutNode :node="layout" :has-field="hasField">
    <template #field="{ fieldName }">
      <div v-if="hasField(fieldName)" class="crud-detail-field">
        <span class="crud-detail-field__label">{{ fields[fieldName].label }}</span>
        <CellRenderer :cell="fields[fieldName].cell" />
      </div>
    </template>
  </CrudLayoutNode>
</template>

<style scoped lang="scss">
@layer crudlink {
  .crud-detail-field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;

    &__label {
      color: var(--crudlink-text-muted-color);
    }
  }
}
</style>
