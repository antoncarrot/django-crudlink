<script setup lang="ts">
defineProps<{
  value: boolean
}>()
</script>

<template>
  <span :class="value ? 'bool-cell--true' : 'bool-cell--false'">{{ value ? '✓' : '✗' }}</span>
</template>

<style scoped lang="scss">
@layer crudlink {
  .bool-cell--true {
    color: var(--crudlink-green-500);
  }

  .bool-cell--false {
    color: var(--crudlink-red-500);
  }
}
</style>
