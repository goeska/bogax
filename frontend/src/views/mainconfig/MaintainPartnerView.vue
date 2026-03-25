<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api/client'

const maintainPartner = ref(true)
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
    maintainPartner.value = data.is_customer_maintained === true
  } catch {
    err.value = 'Failed to load configuration.'
  } finally {
    loading.value = false
  }
}

async function submit() {
  saving.value = true
  err.value = ''
  ok.value = ''
  try {
    await api.patch('/main-config/', {
      is_customer_maintained: maintainPartner.value,
    })
    ok.value = 'Saved.'
    await load()
  } catch (e) {
    err.value =
      e.response?.data?.detail ||
      (typeof e.response?.data === 'object' && JSON.stringify(e.response.data)) ||
      'Failed to save.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="stack">
    <div class="card">
      <h2 class="h2">Maintain Partner</h2>
      <p class="muted question-lead">Maintain partner data for sales transactions</p>
      <div v-if="loading" class="muted">Loading…</div>
      <form v-else class="stack form-block" @submit.prevent="submit">
        <fieldset class="choices">
          <label class="choice">
            <input v-model="maintainPartner" type="radio" :value="true" />
            <span>Yes</span>
          </label>
          <label class="choice">
            <input v-model="maintainPartner" type="radio" :value="false" />
            <span>No</span>
          </label>
        </fieldset>
        <p class="muted helper-text">
          Turn this on when sales need partner identity (e.g., invoice/CRM). Turn this off for
          fast retail walk-in transactions.
        </p>
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
.question-lead {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
}
.form-block {
  gap: 1rem;
}
.helper-text {
  margin: -0.15rem 0 0;
  font-size: 0.88rem;
  line-height: 1.35;
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
