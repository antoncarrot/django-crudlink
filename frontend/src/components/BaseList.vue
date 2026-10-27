<script setup lang="ts">
import Column from 'openvue/column'
import DataTable, { type DataTablePageEvent, type DataTableSortEvent } from 'openvue/datatable'
import { computed } from 'vue'

import type { Cell, RowData } from '../shared'
import type { BaseListProps, ListState } from '../types'
import CellRenderer from './CellRenderer.vue'

/*
 * The table state (page, ordering) is the one in `data`: the backend reads it from the url,
 * and the page keeps `data` in step with the url. A sort or page change is only emitted as
 * `change`; the page then updates the url and `data`. Until then the DataTable shows the
 * clicked sort or page itself.
 *
 * Before the first `data` there is nothing to sort or page: no sortable columns and no paginator.
 * The DataTable would sort by itself, out of step with the url, and a url change would load the
 * deferred `data` once more.
 */
const props = defineProps<BaseListProps>()
const emit = defineEmits<{ change: [state: ListState] }>()

const rows = computed(() => props.data?.rows ?? [])
/** null until `data` is loaded. */
const pagination = computed(() => props.data?.pagination ?? null)
const ordering = computed(() => props.data?.ordering ?? null)
const page = computed(() => pagination.value?.page ?? 1)
const sortField = computed(() => ordering.value?.replace(/^-/, '') || undefined)
const sortOrder = computed<1 | -1>(() => (ordering.value?.startsWith('-') ? -1 : 1))
/** Index of the first row of the current page, DataTable's `first`. */
const firstRowIndex = computed(() => (page.value - 1) * (pagination.value?.pageSize ?? 0))

/** The table sorts the rows itself, by their plain `values`: a column's sort field is `values.<name>`. */
const valuesPrefix = 'values.'

function columnSortField(name: string): string {
  return valuesPrefix + name
}

/** Column name of a sort field, the inverse of `columnSortField()`. */
function columnName(field: string): string {
  return field.startsWith(valuesPrefix) ? field.slice(valuesPrefix.length) : field
}

function onPage(event: DataTablePageEvent): void {
  emit('change', { page: event.page + 1, ordering: ordering.value })
}

function onSort(event: DataTableSortEvent): void {
  const name = typeof event.sortField === 'string' ? columnName(event.sortField) : ''
  emit('change', { page: 1, ordering: name && event.sortOrder ? `${event.sortOrder === -1 ? '-' : ''}${name}` : null })
}
</script>

<template>
  <DataTable
    :value="rows"
    data-key="pk"
    :loading="!data"
    :paginator="pagination !== null"
    removable-sort
    :rows="pagination?.pageSize"
    :first="firstRowIndex"
    :sort-field="sortField && columnSortField(sortField)"
    :sort-order="sortOrder"
    @page="onPage"
    @sort="onSort"
  >
    <Column
      v-for="column in columns"
      :key="column.name"
      :field="column.name"
      :sort-field="columnSortField(column.name)"
      :header="column.label"
      :sortable="column.sortable && Boolean(data)"
    >
      <template #body="{ data }">
        <CellRenderer :cell="(data as RowData).cells[column.name] as Cell" />
      </template>
    </Column>
    <template #empty>
      <!-- TODO: frontend i18n -->
      <span v-if="data">No rows</span>
    </template>
  </DataTable>
</template>
