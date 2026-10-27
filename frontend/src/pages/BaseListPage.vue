<script setup lang="ts">
import BaseList from '../components/BaseList.vue'
import CrudPage from '../components/CrudPage.vue'
import { useInertiaListUrl } from '../composables/useInertiaListUrl'
import type { ListProps } from '../shared'

defineProps<ListProps>()

const { onChange } = useInertiaListUrl()
</script>

<template>
  <CrudPage :title="title">
    <BaseList :columns :data @change="onChange" />
  </CrudPage>
</template>
