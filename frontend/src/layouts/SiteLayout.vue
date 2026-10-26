<script setup lang="ts">
import { usePage } from '@inertiajs/vue3'
import { computed } from 'vue'

import type { CrudlinkSharedProps } from '../shared'

// Placeholder: menu and user come with the site layout design.
const page = usePage()
const site = computed(() => page.props.crudlink as CrudlinkSharedProps | undefined)
</script>

<template>
  <div class="site-layout">
    <header class="site-layout__header">
      <span class="site-layout__title">{{ site?.siteTitle }}</span>
    </header>
    <main class="site-layout__main">
      <slot />
    </main>
  </div>
</template>

<style scoped lang="scss">
@layer crudlink {
  .site-layout {
    min-height: 100vh;
    font-family: system-ui, sans-serif;
    background: var(--crudlink-content-background);
    color: var(--crudlink-text-color);

    &__header {
      display: flex;
      align-items: center;
      padding: 0.75rem 1.5rem;
      border-bottom: 1px solid var(--crudlink-content-border-color);
    }

    &__title {
      font-weight: 600;
      font-size: 1.125rem;
    }

    &__main {
      padding: 1.5rem;
    }
  }
}
</style>
