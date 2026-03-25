import { computed, ref } from 'vue'

/**
 * Shared DRF page state + response handling + Prev/Next handlers.
 * @param {number} pageSize
 */
export function usePagination(pageSize) {
  const currentPage = ref(1)
  const totalCount = ref(0)
  const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))

  function applyDrfResponse(data, rowsRef, page) {
    if (Array.isArray(data)) {
      rowsRef.value = data
      totalCount.value = data.length
      currentPage.value = 1
    } else {
      rowsRef.value = data.results ?? []
      totalCount.value = Number(data.count ?? rowsRef.value.length)
      currentPage.value = page
    }
  }

  function makePager(loadingRef, load) {
    return {
      prevPage() {
        if (currentPage.value <= 1 || loadingRef.value) return
        load(currentPage.value - 1)
      },
      nextPage() {
        if (currentPage.value >= totalPages.value || loadingRef.value) return
        load(currentPage.value + 1)
      },
    }
  }

  return { currentPage, totalCount, totalPages, applyDrfResponse, makePager }
}
