<script setup>
import { nextTick, onMounted, onUnmounted, ref, shallowRef } from 'vue'
import { api } from '../api/client'

const elWeek = ref(null)
const elMonth = ref(null)
const chartWeek = shallowRef(null)
const chartMonth = shallowRef(null)
const err = ref('')
const loading = ref(true)
const weekTotal = ref(0)
const monthTotal = ref(0)
const weekSeriesCount = ref(0)
const monthSeriesCount = ref(0)

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
    return d.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric', month: 'short' })
  }
  return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short' })
}

/** This week’s X-axis: calendar date (weekday + day). */
function formatWeekDateAxis(isoDate) {
  if (!isoDate) return ''
  const d = new Date(`${isoDate}T12:00:00`)
  if (Number.isNaN(d.getTime())) return isoDate
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function compactNumber(v) {
  return v >= 1_000_000_000
    ? `${(v / 1_000_000_000).toFixed(1)}B`
    : v >= 1_000_000
      ? `${(v / 1_000_000).toFixed(1)}M`
      : v >= 1000
        ? `${(v / 1000).toFixed(0)}k`
        : String(v)
}

function sumSeriesValues(series) {
  return (series || []).reduce(
    (acc, s) => acc + (s?.data || []).reduce((lineAcc, n) => lineAcc + (Number(n) || 0), 0),
    0,
  )
}

function formatCompactIdr(v) {
  const n = Number(v) || 0
  if (n >= 1_000_000_000) return `Rp ${(n / 1_000_000_000).toFixed(1)}B`
  if (n >= 1_000_000) return `Rp ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `Rp ${(n / 1_000).toFixed(0)}k`
  return `Rp ${Math.round(n)}`
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
          ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(v)
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
      name: weekDateAxis ? 'Date (this week)' : '',
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
let echartsModule

onMounted(async () => {
  loading.value = true
  err.value = ''
  try {
    const [weekData, monthData] = await Promise.all([
      fetchStacked('week', { includeTaxes: true }),
      fetchStacked('month'),
    ])
    weekTotal.value = sumSeriesValues(weekData.series)
    monthTotal.value = sumSeriesValues(monthData.series)
    weekSeriesCount.value = (weekData.series || []).length
    monthSeriesCount.value = (monthData.series || []).length
    if (!echartsModule) {
      echartsModule = await import('echarts')
    }

    loading.value = false
    await nextTick()

    if (elWeek.value) {
      chartWeek.value = echartsModule.init(elWeek.value, null, { renderer: 'canvas' })
      chartWeek.value.setOption(
        buildChartOption({
          title: 'This week’s sales (by product, tax included)',
          labels: weekData.labels || [],
          series: weekData.series || [],
          period: 'week',
          weekDateAxis: true,
          yAxisName: 'IDR (incl. tax)',
        }),
        true,
      )
      roWeek = new ResizeObserver(() => chartWeek.value?.resize())
      roWeek.observe(elWeek.value)
    }

    if (elMonth.value) {
      chartMonth.value = echartsModule.init(elMonth.value, null, { renderer: 'canvas' })
      chartMonth.value.setOption(
        buildChartOption({
          title: 'This month’s sales (by product)',
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
      'Could not load charts.'
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
    <section class="card erp-head">
      <p class="erp-kicker">Executive Overview</p>
      <div class="erp-title-row">
        <h1 class="erp-title">Sales Dashboard</h1>
        <span class="erp-chip">Live Performance Snapshot</span>
      </div>
      <p class="lead dashboard-lead">
        <strong>This week:</strong> line amounts include tax (Y-axis in IDR).
        <strong>This month:</strong> line subtotals (qty × price), tax per line not included.
      </p>
      <div class="dashboard-kpi-row">
        <div class="dashboard-kpi">
          <span class="dashboard-kpi-label">Week to date</span>
          <strong>{{ formatCompactIdr(weekTotal) }}</strong>
        </div>
        <div class="dashboard-kpi dashboard-kpi--violet">
          <span class="dashboard-kpi-label">Month to date</span>
          <strong>{{ formatCompactIdr(monthTotal) }}</strong>
        </div>
        <div class="dashboard-kpi dashboard-kpi--green">
          <span class="dashboard-kpi-label">Active products (week)</span>
          <strong>{{ weekSeriesCount }}</strong>
        </div>
        <div class="dashboard-kpi dashboard-kpi--slate">
          <span class="dashboard-kpi-label">Active products (month)</span>
          <strong>{{ monthSeriesCount }}</strong>
        </div>
      </div>
    </section>

    <div v-if="loading" class="dashboard-loading muted">Loading charts…</div>
    <p v-else-if="err" class="error">{{ err }}</p>
    <div v-else class="dashboard-charts">
      <div class="dashboard-chart-card card">
        <div ref="elWeek" class="dashboard-chart" role="img" aria-label="This week sales chart" />
      </div>
      <div class="dashboard-chart-card card">
        <div ref="elMonth" class="dashboard-chart" role="img" aria-label="This month sales chart" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-home {
  display: grid;
  gap: 1.15rem;
}

.dashboard-lead {
  margin: 0.35rem 0 0.72rem;
  padding: 0.8rem 0.95rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
}

.dashboard-kpi-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.6rem;
}

@media (max-width: 1080px) {
  .dashboard-kpi-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .dashboard-kpi-row {
    grid-template-columns: 1fr;
  }
}

.dashboard-kpi {
  display: flex;
  flex-direction: column;
  gap: 0.18rem;
  border: 1px solid #c7d2fe;
  border-radius: 11px;
  background: #eef2ff;
  color: #3730a3;
  padding: 0.6rem 0.7rem;
}

.dashboard-kpi-label {
  font-size: 0.76rem;
  font-weight: 620;
  opacity: 0.9;
}

.dashboard-kpi strong {
  font-size: 1rem;
  font-weight: 760;
}

.dashboard-kpi--violet {
  border-color: #ddd6fe;
  background: #f5f3ff;
  color: #5b21b6;
}

.dashboard-kpi--green {
  border-color: #bbf7d0;
  background: #e8f8ef;
  color: #166534;
}

.dashboard-kpi--slate {
  border-color: #d8e1ec;
  background: #f1f5f9;
  color: #334155;
}

.dashboard-loading {
  padding: 0.85rem 1rem;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  background: #f8fbff;
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
  padding: 0.95rem;
  border-radius: 14px;
}

.dashboard-chart-card :deep(canvas) {
  border-radius: 8px;
}

.dashboard-chart {
  width: 100%;
  height: 360px;
  min-height: 280px;
}
</style>
