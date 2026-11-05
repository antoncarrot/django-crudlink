<script setup lang="ts">
import Button from 'openvue/button'

import BaseDetail from '../components/BaseDetail.vue'
import CrudLink from '../components/CrudLink.vue'
import CrudPage from '../components/CrudPage.vue'
import type { DetailProps } from '../shared'

defineProps<DetailProps>()
</script>

<template>
  <CrudPage :title="title">
    <BaseDetail :fields :layout />

    <div v-if="listUrl">
      <!-- a link that looks like a button: it opens in a new tab, and follows the navigation mode -->
      <!-- TODO: frontend i18n -->
      <Button :as="CrudLink" :href="listUrl" label="Back to list" severity="secondary" text />
    </div>
  </CrudPage>
</template>
