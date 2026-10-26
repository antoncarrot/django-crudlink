<script setup lang="ts">
import { Head } from '@inertiajs/vue3'

defineProps<{
  title: string
}>()
</script>

<template>
  <Head :title="title" />
  <section class="crud-page">
    <header class="crud-page__header">
      <h1 class="crud-page__title">{{ title }}</h1>
      <div class="crud-page__actions">
        <slot name="actions" />
      </div>
    </header>
    <slot />
  </section>
</template>

<style scoped lang="scss">
@layer crudlink {
  .crud-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;

    &__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
    }

    &__title {
      margin: 0;
      font-size: 1.5rem;
    }

    &__actions {
      display: flex;
      gap: 0.5rem;
    }
  }
}
</style>
