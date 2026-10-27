<script setup lang="ts">
import { useCellComponent } from '../registry'
import type { Cell } from '../shared'

defineProps<{
  cell: Cell
}>()

const cellComponent = useCellComponent()
</script>

<template>
  <component :is="cellComponent(cell.component)" v-bind="cell.props" />
</template>
