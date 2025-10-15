<template>
  <h2>Покупки</h2>

  <form @submit.prevent="onAdd" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col-auto">
        <select v-model="toAdd.item" class="form-select" required>
          <option disabled value="">Выберите вещь</option>
          <option v-for="i in items" :value="i.id" :key="i.id">{{ i.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <select v-model="toAdd.store" class="form-select" required>
          <option disabled value="">Выберите магазин</option>
          <option v-for="s in stores" :value="s.id" :key="s.id">{{ s.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <input v-model.number="toAdd.amount" type="number" class="form-control" min="1" placeholder="Количество" required />
      </div>
      <div class="col-auto">
        <input v-model="toAdd.date" type="date" class="form-control" required />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <ul class="list-group">
    <li v-for="p in purchases" :key="p.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ itemsById[p.item]?.name }}</strong> — {{ storesById[p.store]?.name }}<br>
        <small class="text-muted">{{ p.amount }} шт, {{ p.date }}</small>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(p)" data-bs-toggle="modal" data-bs-target="#editPurchaseModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(p)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модал редактирования -->
  <div class="modal fade" id="editPurchaseModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5>Редактировать покупку</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <select v-model="toEdit.item" class="form-select mb-2">
            <option v-for="i in items" :value="i.id">{{ i.name }}</option>
          </select>
          <select v-model="toEdit.store" class="form-select mb-2">
            <option v-for="s in stores" :value="s.id">{{ s.name }}</option>
          </select>
          <input v-model.number="toEdit.amount" type="number" class="form-control mb-2" />
          <input v-model="toEdit.date" type="date" class="form-control" />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button class="btn btn-primary" @click="onUpdate" data-bs-dismiss="modal">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const purchases = ref([])
const items = ref([])
const stores = ref([])

const toAdd = ref({ item: '', store: '', amount: 1, date: '' })
const toEdit = ref({ id: null, item: '', store: '', amount: 1, date: '' })

const itemsById = computed(() => Object.fromEntries(items.value.map(i => [i.id, i])))
const storesById = computed(() => Object.fromEntries(stores.value.map(s => [s.id, s])))

async function fetchPurchases() { purchases.value = (await axios.get('/purchases/')).data }
async function fetchItems() { items.value = (await axios.get('/items/')).data }
async function fetchStores() { stores.value = (await axios.get('/stores/')).data }

async function onAdd() {
  await axios.post('/purchases/', { ...toAdd.value })
  toAdd.value = { item: '', store: '', amount: 1, date: '' }
  await fetchPurchases()
}

async function onRemove(p) {
  if (!confirm(`Удалить покупку от ${p.date}?`)) return
  await axios.delete(`/purchases/${p.id}/`)
  await fetchPurchases()
}

function onEditClick(p) {
  toEdit.value = { ...p }
}

async function onUpdate() {
  await axios.put(`/purchases/${toEdit.value.id}/`, { ...toEdit.value })
  await fetchPurchases()
}

onMounted(async () => {
  await Promise.all([fetchPurchases(), fetchItems(), fetchStores()])
})
</script>
