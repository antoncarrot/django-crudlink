<script setup lang="ts">
import Tag from 'openvue/tag'

import type { CellLink } from '../../shared'
import CrudLink from '../CrudLink.vue'

defineProps<{
  items: CellLink[]
}>()
</script>

<template>
  <span class="link-tags-cell">
    <CrudLink
      v-for="(item, index) in items"
      :key="`${index}-${item.text}`"
      :href="item.href"
      class="link-tags-cell__link"
    >
      <Tag :value="item.text" severity="secondary" />
    </CrudLink>
  </span>
</template>

<style scoped lang="scss">
@layer crudlink {
  .link-tags-cell {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 0.25rem;

    &__link {
      text-decoration: none;

      &:hover :deep(.p-tag) {
        color: var(--crudlink-primary-color);
      }
    }
  }
}
</style>
