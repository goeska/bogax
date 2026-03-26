<script setup>
import * as echarts from 'echarts'
import { nextTick, onMounted, onUnmounted, ref, shallowRef } from 'vue'
import { api } from '../api/client'

const elWeek = ref(null)
const elMonth = ref(null)
const chartWeek = shallowRef(null)
const chartMonth = shallowRef(null)
const err = ref('')
const loading = ref(true)

const palette = [
  '#2563eb',
  '#7c3aed',
  '#db2777',
  '#ea580c',
  '#16a34a',
  '#0891b2',
  '#ca8a04',
  '#4f46e5',
  '#0d9488',
  '#be123c',
]

function formatAxisLabel(isoDate, period) {
  if (!isoDate) return ''
  const d = new Date(`${isoDate}T12:00:00`)
  if (Number.isNaN(d.getTime())) return isoDate
  if (period === 'week') {
    return d.toLocaleDateString('id-ID', { weekday: 'short', day: 'numeric', month: 'short' })
  }
  return d.toLocaleDateString('id-ID', { day: 'numeric', month: 'short' })
}

/** Sumbu X minggu ini: tekan tanggal kalender (hari + tanggal). */
function formatWeekDateAxis(isoDate) {
  if (!isoDate) return ''
  const d = new Date(`${isoDate}T12:00:00`)
  if (Number.isNaN(d.getTime())) return isoDate
  return d.toLocaleDateString('id-ID', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function compactNumber(v) {
  return v >= 1_000_000
    ? `${(v / 1_000_000).toFixed(1)}jt`
    : v >= 1000
      ? `${(v / 1000).toFixed(0)}k`
      : String(v)
}

function createAxisBreak(series) {
  const values = series.flatMap((s) => s.data || []).map((v) => Number(v) || 0)
  const maxVal = Math.max(0, ...values)
  if (maxVal < 2_000_000) {
    return {
      enabled: false,
      map: (v) => v,
      unmap: (v) => v,
      start: 0,
      end: 0,
    }
  }

  const start = Math.max(300_000, Math.round(maxVal * 0.12))
  const end = Math.max(start + 1, Math.round(maxVal * 0.7))
  const compress = 0.2
  return {
    enabled: true,
    start,
    end,
    map(v) {
      if (v <= start) return v
      if (v <= end) return start
      return start + (v - end) * compress
    },
    unmap(v) {
      if (v <= start) return v
      return end + (v - start) / compress
    },
  }
}

function buildChartOption({ title, labels, series, period, yAxisName, weekDateAxis }) {
  const axisLabels = labels.map((l) =>
    weekDateAxis ? formatWeekDateAxis(l) : formatAxisLabel(l, period),
  )
  const axisBreak = createAxisBreak(series)
  return {
    color: palette,
    title: {
      text: title,
      left: 0,
      top: 0,
      textStyle: { fontSize: 14, fontWeight: 600, color: '#0f172a' },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', label: { backgroundColor: '#64748b' } },
      valueFormatter: (v) =>
        typeof v === 'number'
          ? new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(v)
          : v,
    },
    legend: {
      type: 'scroll',
      bottom: 0,
      textStyle: { fontSize: 11, color: '#475569' },
    },
    grid: {
      left: yAxisName ? '3%' : '2%',
      right: '2%',
      top: 48,
      bottom: weekDateAxis ? Math.max(series.length > 4 ? 88 : 72, 72) : series.length > 4 ? 72 : 56,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: axisLabels,
      name: weekDateAxis ? 'Tanggal (minggu ini)' : '',
      nameLocation: 'middle',
      nameGap: 28,
      nameTextStyle: { color: '#64748b', fontSize: 11 },
      axisLabel: { color: '#64748b', fontSize: 11 },
    },
    yAxis: {
      type: 'value',
      name: yAxisName || '',
      nameLocation: 'middle',
      nameGap: 44,
      nameTextStyle: { color: '#64748b', fontSize: 11 },
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (v) => compactNumber(Math.round(axisBreak.unmap(v))),
      },
      splitLine: { lineStyle: { color: '#e2e8f0' } },
    },
    series: series.map((s) => ({
      name: s.name,
      type: 'bar',
      stack: 'sales',
      barMaxWidth: 26,
      emphasis: { focus: 'series' },
      data: (s.data || []).map((v) => axisBreak.map(Number(v) || 0)),
    })),
    markArea: axisBreak.enabled
      ? {
          silent: true,
          itemStyle: { color: 'rgba(148, 163, 184, 0.12)' },
          data: [[{ yAxis: axisBreak.map(axisBreak.start) }, { yAxis: axisBreak.map(axisBreak.end) }]],
        }
      : undefined,
  }
}

async function fetchStacked(period, { includeTaxes = false } = {}) {
  const params = { period }
  if (includeTaxes) params.include_taxes = '1'
  const { data } = await api.get('/sales/dashboard/stacked-area/', { params })
  return data
}

function disposeCharts() {
  chartWeek.value?.dispose()
  chartMonth.value?.dispose()
  chartWeek.value = null
  chartMonth.value = null
}

let roWeek
let roMonth

onMounted(async () => {
  loading.value = true
  err.value = ''
  try {
    const [weekData, monthData] = await Promise.all([
      fetchStacked('week', { includeTaxes: true }),
      fetchStacked('month'),
    ])

    loading.value = false
    await nextTick()

    if (elWeek.value) {
      chartWeek.value = echarts.init(elWeek.value, null, { renderer: 'canvas' })
      chartWeek.value.setOption(
        buildChartOption({
          title: 'Penjualan minggu ini (per produk, termasuk pajak)',
          labels: weekData.labels || [],
          series: weekData.series || [],
          period: 'week',
          weekDateAxis: true,
          yAxisName: 'Rp (termasuk pajak)',
        }),
        true,
      )
      roWeek = new ResizeObserver(() => chartWeek.value?.resize())
      roWeek.observe(elWeek.value)
    }

    if (elMonth.value) {
      chartMonth.value = echarts.init(elMonth.value, null, { renderer: 'canvas' })
      chartMonth.value.setOption(
        buildChartOption({
          title: 'Penjualan bulan ini (per produk)',
          labels: monthData.labels || [],
          series: monthData.series || [],
          period: 'month',
        }),
        true,
      )
      roMonth = new ResizeObserver(() => chartMonth.value?.resize())
      roMonth.observe(elMonth.value)
    }
  } catch (e) {
    err.value =
      e.response?.data?.period?.[0] ||
      e.response?.data?.detail ||
      e.message ||
      'Gagal memuat grafik.'
    loading.value = false
  }
})

onUnmounted(() => {
  roWeek?.disconnect()
  roMonth?.disconnect()
  disposeCharts()
})
</script>

<template>
  <div class="dashboard-home">
    <p class="lead dashboard-lead">
      <strong>Minggu ini:</strong> nilai per baris termasuk pajak (sumbu Y dalam Rp).
      <strong>Bulan ini:</strong> subtotal baris (qty × harga), belum termasuk pajak per baris.
    </p>
    <div v-if="loading" class="dashboard-loading muted">Memuat grafik…</div>
    <p v-else-if="err" class="error">{{ err }}</p>
    <div v-else class="dashboard-charts">
      <div class="dashboard-chart-card card">
        <div ref="elWeek" class="dashboard-chart" role="img" aria-label="Grafik penjualan minggu ini" />
      </div>
      <div class="dashboard-chart-card card">
        <div ref="elMonth" class="dashboard-chart" role="img" aria-label="Grafik penjualan bulan ini" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-home {
  display: grid;
  gap: 1rem;
}

.dashboard-lead {
  margin: 0;
}

.dashboard-loading {
  padding: 1rem 0;
}

.dashboard-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  align-items: stretch;
}

@media (max-width: 960px) {
  .dashboard-charts {
    grid-template-columns: 1fr;
  }
}

.dashboard-chart-card {
  min-width: 0;
  padding: 1rem;
}

.dashboard-chart {
  width: 100%;
  height: 360px;
  min-height: 280px;
}
</style>
