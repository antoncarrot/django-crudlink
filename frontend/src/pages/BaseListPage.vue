<script setup lang="ts">
import BaseList from '../components/BaseList.vue'
import CrudPage from '../components/CrudPage.vue'
import { useInertiaListUrl } from '../composables/useInertiaListUrl'
import type { ListProps } from '../shared'

const props = defineProps<ListProps>()

const { loading, onChange } = useInertiaListUrl(() => props.hugeTable)
</script>

<template>
  <CrudPage :title="title">
    <BaseList :columns :data :huge-table :loading @change="onChange" />
  </CrudPage>
</template>
