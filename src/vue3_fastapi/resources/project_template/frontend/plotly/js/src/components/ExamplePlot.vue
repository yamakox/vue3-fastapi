<script setup>
import Plot from '@yamakox/vue3-plotly'
import { ref } from 'vue'

const plot1 = ref()

const x = Array.from({ length: 21 }, (_, i) => 2 * Math.PI * i / 20)
const y = x.map(x => Math.sin(x))

const data = [
  { x: x, y: y, type: 'scatter', mode: 'lines+markers', name: 'Sine Curve' }
]

const layout = {
  title: { text: 'Plotly Chart Example', font: { size: 20 } }, width: 600, height: 400
}
</script>

<template>
  <plot ref="plot1" :data="data" :layout="layout" />
</template>
