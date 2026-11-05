<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import { computed } from 'vue'

import { isSafeUrl, useNavigation } from '../composables/useNavigation'

// the link's class and attributes don't go to the plain text of an unsafe url
defineOptions({ inheritAttrs: false })

const props = defineProps<{
  href: string
}>()

const { isInertiaNavigation } = useNavigation()
const isSafe = computed(() => isSafeUrl(props.href))
</script>

<template>
  <component v-if="isSafe" :is="isInertiaNavigation ? Link : 'a'" v-bind="$attrs" :href="href"><slot /></component>
  <span v-else><slot /></span>
</template>
