<script setup lang="ts">
import { computed } from 'vue'

/** Stands in for a cell component that isn't registered: the `text` of a text cell, the `value` of a custom one. */
const props = defineProps<{
  text?: string
  value?: unknown
}>()

const shown = computed(() => {
  if (props.text !== undefined) return props.text
  if (props.value === null || props.value === undefined) return ''
  return Array.isArray(props.value) ? props.value.join(', ') : String(props.value)
})
</script>

<template>
  <span>{{ shown }}</span>
</template>
