<script setup lang="ts">
import Column from 'openvue/column'
import DataTable, { type DataTablePageEvent, type DataTableSortEvent } from 'openvue/datatable'
import { computed, ref, watch } from 'vue'

import type { Cell, RowData } from '../shared'
import type { BaseListProps, ListState } from '../types'
import CellRenderer from './CellRenderer.vue'

/*
 * The table state (page, ordering) is the one in `data`: the backend reads it from the url,
 * and the page keeps `data` in step with the url. A sort or page change is only emitted as
 * `change`; the page then updates the url and `data` (for a huge table, reloads it, with
 * `loading` meanwhile). Until then the DataTable shows the clicked sort or page itself, and
 * goes back to the one in `data` if a reload ends without new data.
 *
 * Before the first `data` there is nothing to page: no paginator.
 */
const props = defineProps<BaseListProps>()
const emit = defineEmits<{ change: [state: ListState] }>()

const rows = computed(() => props.data?.rows ?? [])
/** null until `data` is loaded. */
const pagination = computed(() => props.data?.pagination ?? null)
const loading = computed(() => !props.data || props.loading)
const ordering = computed(() => props.data?.ordering ?? null)
const page = computed(() => pagination.value?.page ?? 1)
/** The sort column in `data`, and its order. */
const dataSortColumn = computed(() => ordering.value?.replace(/^-/, '') || undefined)
const dataSortOrder = computed<1 | -1>(() => (ordering.value?.startsWith('-') ? -1 : 1))
/** Index of the first row of the current page, DataTable's `first`. */
const firstRowIndex = computed(() => (page.value - 1) * (pagination.value?.pageSize ?? 0))
/**
 * Rows the paginator counts with (a huge table's DataTable only has the current page). Without a count
 * (`total: null`), the rows up to the end of this page, and one more to enable "next". Not the rows on
 * this page: an empty page past the end would leave `first` at the count, and the paginator then jumps
 * to its last page by itself.
 */
const totalRecords = computed(() => {
  if (!pagination.value) return 0
  const { total, pageSize, hasNext } = pagination.value
  return total ?? page.value * pageSize + (hasNext ? 1 : 0)
})
/** Without a count, there is no last page to link to: only previous / current / next. */
const paginatorTemplate = computed(() =>
  pagination.value?.total === null ? 'PrevPageLink CurrentPageReport NextPageLink' : undefined,
)

const valuesPrefix = 'values.'

/**
 * A huge table only has the page the backend sorted: a column's sort field is its name. Otherwise
 * the table sorts the rows itself, by their plain `values`: the sort field is `values.<name>`.
 */
function columnSortField(name: string): string {
  return props.hugeTable ? name : valuesPrefix + name
}

/** Column name of a sort field, the inverse of `columnSortField()`. */
function columnName(field: string): string {
  return field.startsWith(valuesPrefix) ? field.slice(valuesPrefix.length) : field
}

/**
 * The DataTable's page and sort, two-way bound: a click changes them. Whenever the table isn't
 * loading they are the ones in `data`, so new data brings its own, and a reload that ends without
 * new data (it failed) doesn't leave the clicked page or sort on show over the old rows.
 */
const first = ref(0)
const sortField = ref<string | undefined>()
const sortOrder = ref<number | undefined>(1)
watch(
  [() => props.data, loading],
  () => {
    if (loading.value) return
    first.value = firstRowIndex.value
    sortField.value = dataSortColumn.value && columnSortField(dataSortColumn.value)
    sortOrder.value = dataSortOrder.value
  },
  { immediate: true },
)

/** `ListState.ordering` of a DataTable sort field and order. */
function orderingOf(field: DataTableSortEvent['sortField'], order: DataTableSortEvent['sortOrder']): string | null {
  const name = typeof field === 'string' ? columnName(field) : ''
  return name && order ? `${order === -1 ? '-' : ''}${name}` : null
}

function onPage(event: DataTablePageEvent): void {
  // the sort the DataTable shows: a sort click that is still loading is not in `data` yet
  emit('change', { page: event.page + 1, ordering: orderingOf(event.sortField, event.sortOrder) })
}

function onSort(event: DataTableSortEvent): void {
  emit('change', { page: 1, ordering: orderingOf(event.sortField, event.sortOrder) })
}
</script>

<template>
  <DataTable
    :value="rows"
    data-key="pk"
    :lazy="hugeTable"
    :loading="loading"
    :paginator="pagination !== null"
    removable-sort
    :rows="pagination?.pageSize"
    :total-records="totalRecords"
    v-model:first="first"
    :paginator-template="paginatorTemplate"
    current-page-report-template="{currentPage}"
    v-model:sort-field="sortField"
    v-model:sort-order="sortOrder"
    @page="onPage"
    @sort="onSort"
  >
    <Column
      v-for="column in columns"
      :key="column.name"
      :field="column.name"
      :sort-field="columnSortField(column.name)"
      :header="column.label"
      :sortable="column.sortable"
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
