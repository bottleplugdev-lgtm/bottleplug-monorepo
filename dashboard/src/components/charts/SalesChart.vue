<template>
  <div class="h-64 relative">
    <canvas v-show="hasData" ref="chartRef"></canvas>
    <div v-if="!hasData && !loading" class="absolute inset-0 flex items-center justify-center text-secondary-500 text-sm">
      No sales data for the selected period
    </div>
  </div>
  
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const chartRef = ref(null)
let chart = null

const hasData = computed(() => {
  const d = props.data || {}
  const labelsOk = Array.isArray(d.labels) && d.labels.length > 0
  const series = Array.isArray(d.datasets) ? d.datasets : []
  const anyValues = series.some(s => Array.isArray(s.data) && s.data.length > 0)
  return labelsOk && anyValues
})

const initChart = () => {
  if (chart) {
    chart.destroy()
  }

  if (!chartRef.value) return

  const ctx = chartRef.value.getContext('2d')
  chart = new Chart(ctx, {
    type: 'bar',
    data: props.data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          type: 'linear',
          position: 'left',
          beginAtZero: true,
          title: { display: true, text: 'Revenue' },
          grid: { color: 'rgba(0, 0, 0, 0.08)' }
        },
        y1: {
          type: 'linear',
          position: 'right',
          beginAtZero: true,
          title: { display: true, text: 'Orders' },
          grid: { drawOnChartArea: false }
        },
        x: {
          grid: {
            display: false
          }
        }
      },
      elements: {
        point: {
          radius: 0
        }
      }
    }
  })
}

const updateChart = () => {
  if (chart) {
    chart.data = props.data
    chart.update()
  }
}

onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

watch(() => props.data, updateChart, { deep: true })
watch(() => props.loading, (loading) => {
  if (!loading && chart) {
    updateChart()
  }
})
</script> 