<script setup lang="ts">
import { ref, onMounted } from 'vue'

defineProps<{ msg: string }>()

const count = ref(0)
const hello = ref('')

async function getHello() {
  const response = await fetch('/api/v1/example/hello')
  if (!response.ok) {
    hello.value = 'Failed to fetch hello'
    return
  }
  const data = await response.json()
  hello.value = data.message
}

async function counter(up: boolean) {
  const path = up?'count_up':'counter'
  const response = await fetch(`http://localhost:8000/api/v1/example/${path}`)
  if (!response.ok) {
    count.value = -1
    return
  }
  const data = await response.json()
  count.value = Number(data.counter)
}

onMounted(async () => {
  await getHello()
  await counter(false)
})
</script>

<template>
  <h1>{{ msg }}</h1>
  <h1>{{ hello }}</h1>

  <div class="card">
    <button type="button" @click="counter(true)">count is {{ count }}</button>
    <p>
      Edit
      <code>components/HelloFastAPI.vue</code> to test HMR
    </p>
  </div>

  <p>
    Check out
    <a href="https://vuejs.org/guide/quick-start.html#local" target="_blank"
      >create-vue</a
    >, the official Vue + Vite starter
  </p>
  <p>
    Learn more about IDE Support for Vue in the
    <a
      href="https://vuejs.org/guide/scaling-up/tooling.html#ide-support"
      target="_blank"
      >Vue Docs Scaling up Guide</a
    >.
  </p>
  <p class="read-the-docs">Click on the Vite and Vue logos to learn more</p>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
