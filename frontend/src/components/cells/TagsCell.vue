<script setup lang="ts">
import Tag from 'openvue/tag'

defineProps<{
  items: string[]
}>()
</script>

<template>
  <span class="tags-cell">
    <Tag v-for="item in items" :key="item" :value="item" severity="secondary" />
  </span>
</template>

<style scoped lang="scss">
@layer crudlink {
  .tags-cell {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 0.25rem;
  }
}
</style>
