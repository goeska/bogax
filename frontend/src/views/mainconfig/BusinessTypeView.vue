<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'

const isRestaurant = ref(true)
const loading = ref(true)
const saving = ref(false)
const err = ref('')
const ok = ref('')

async function load() {
  loading.value = true
  err.value = ''
  ok.value = ''
  try {
    const { data } = await api.get('/main-config/')
    isRestaurant.value = Boolean(data.is_restaurant)
  } catch {
    err.value = 'Could not load settings.'
  } finally {
    loading.value = false
  }
}

async function submit() {
  saving.value = true
  err.value = ''
  ok.value = ''
  try {
    await api.patch('/main-config/', { is_restaurant: isRestaurant.value })
    ok.value = 'All saved.'
    await load()
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && JSON.stringify(e.response.data)) ||
      'Could not save.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="stack">
    <section class="card erp-head">
      <p class="erp-kicker">Main Configuration</p>
      <div class="erp-title-row">
        <h1 class="erp-title">Business Type</h1>
        <span class="erp-chip">Restaurant • Store</span>
      </div>
      <p class="muted">Choose the primary business mode that drives the default transaction flow.</p>
    </section>

    <div class="card">
      <h2 class="h2">Business Type</h2>
      <div v-if="loading" class="muted">Loading…</div>
      <form v-else class="stack form-block" @submit.prevent="submit">
        <fieldset class="choices">
          <label class="choice">
            <input v-model="isRestaurant" type="radio" :value="true" />
            <span>Restaurant</span>
          </label>
          <label class="choice">
            <input v-model="isRestaurant" type="radio" :value="false" />
            <span>Store</span>
          </label>
        </fieldset>
        <button class="btn-primary save-btn" type="submit" :disabled="saving">
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
        <p v-if="ok" class="ok">{{ ok }}</p>
        <p v-if="err" class="error">{{ err }}</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.form-block {
  gap: 1rem;
}
.choices {
  border: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.choice {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
}
.choice input {
  width: 1.1rem;
  height: 1.1rem;
}
.ok {
  color: #15803d;
  margin: 0;
  font-size: 0.9rem;
}
.error {
  margin: 0;
}
.save-btn {
  align-self: flex-start;
  width: 100px;
  box-sizing: border-box;
  padding: 0.4rem 0.35rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 8px;
  text-align: center;
}
</style>
