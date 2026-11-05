<script setup lang="ts">
import CrudLink from '../CrudLink.vue'

defineProps<{
  text: string
  href: string
}>()
</script>

<template>
  <CrudLink :href="href" class="crud-link">{{ text }}</CrudLink>
</template>

<style scoped lang="scss">
@layer crudlink {
  .crud-link {
    color: var(--crudlink-primary-color);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
