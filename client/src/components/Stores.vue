<template>
  <div class="stores-page">
    <!-- Заголовок + статистика + кнопки экспорта -->
    <div class="header-stats mb-4">
      <h2>Магазины</h2>
      <div class="stats-and-buttons">
        <div class="stats-cards">
          <div class="stat-card">Количество: {{ storeStats?.count || 0 }}</div>
          <div class="stat-card">Среднее: {{ storeStats?.avg || 0 }}</div>
          <div class="stat-card">Максимум: {{ storeStats?.max || 0 }}</div>
          <div class="stat-card">Минимум: {{ storeStats?.min || 0 }}</div>
        </div>
        <div class="export-buttons">
          <button class="btn-export excel" @click="exportExcel">
            <i class="bi bi-file-earmark-spreadsheet-fill"></i> Excel
          </button>
          <button class="btn-export word" @click="exportWord">
            <i class="bi bi-file-earmark-word-fill"></i> Word
          </button>
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <form @submit.prevent="onAdd" class="add-form mb-4 flex-wrap">
      <input v-model="toAdd.name" type="text" placeholder="Название магазина" required />
      <input v-model="toAdd.address" type="text" placeholder="Адрес" required />
      <button type="submit" class="btn-add">Добавить</button>
    </form>

    <!-- Фильтры -->
    <div class="filters mb-4 flex-wrap">
      <input v-model="filterName" placeholder="Фильтр по названию" />
      <input v-model="filterAddress" placeholder="Фильтр по адресу" />
    </div>

    <!-- Сетка карточек магазинов -->
    <div class="cards-grid">
      <div v-for="s in filteredStores" :key="s.id" class="store-card">
        <div>
          <strong>{{ s.name }}</strong><br>
          <small class="text-muted">{{ s.address }}</small>
        </div>
        <div class="card-buttons">
          <button class="btn-edit" @click="onEditClick(s)" data-bs-toggle="modal" data-bs-target="#editStoreModal">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn-delete" @click="onRemove(s)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editStoreModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5>Редактировать магазин</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <input v-model="toEdit.name" placeholder="Название" class="mb-2" />
            <input v-model="toEdit.address" placeholder="Адрес" />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button class="btn btn-primary" @click="onUpdate" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stores = ref([])
const storeStats = ref({})
const toAdd = ref({ name: '', address: '' })
const toEdit = ref({ id: null, name: '', address: '' })

const filterName = ref('')
const filterAddress = ref('')

const filteredStores = computed(() => 
  stores.value.filter(s =>
    s.name.toLowerCase().includes(filterName.value.toLowerCase()) &&
    s.address.toLowerCase().includes(filterAddress.value.toLowerCase())
  )
)

async function fetchAll() {
  stores.value = (await axios.get('/stores/')).data
}

async function fetchStoreStats() {
  storeStats.value = (await axios.get('/stores/stats/')).data
}

async function onAdd() {
  await axios.post('/stores/', { ...toAdd.value })
  toAdd.value = { name: '', address: '' }
  await Promise.all([fetchAll(), fetchStoreStats()])
}

async function onRemove(s) {
  if (!confirm(`Удалить магазин "${s.name}"?`)) return
  await axios.delete(`/stores/${s.id}/`)
  await Promise.all([fetchAll(), fetchStoreStats()])
}

function onEditClick(s) { toEdit.value = { ...s } }
async function onUpdate() {
  await axios.put(`/stores/${toEdit.value.id}/`, { ...toEdit.value })
  await Promise.all([fetchAll(), fetchStoreStats()])
}

async function exportExcel() {
  const res = await axios.get('/stores/export-excel/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'Stores.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

async function exportWord() {
  const res = await axios.get('/stores/export-word/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'Stores.docx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

onMounted(async () => {
  await Promise.all([fetchAll(), fetchStoreStats()])
})
</script>

<style scoped>
.stores-page {
  background: #fff;
  padding: 25px;
  border-radius: 15px;
  font-family: 'Arial', sans-serif;
}

/* Заголовок */
h2 {
  color: #d63384;
  margin-bottom: 10px;
}

/* Статистика + кнопки экспорта */
.stats-and-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.stats-cards {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.stat-card {
  background: #fff0f5;
  padding: 4px 10px;
  border-radius: 15px;
  color: #d63384;
  font-weight: bold;
  font-size: 0.85rem;
  box-shadow: 0 2px 6px rgba(255, 105, 180, 0.15);
}

/* Кнопки экспорта */
.export-buttons {
  display: flex;
  gap: 10px;
}

.btn-export {
  font-weight: bold;
  border-radius: 15px;
  padding: 6px 14px;
  color: white;
  border: none;
  cursor: pointer;
  transition: opacity 0.25s;
}

.btn-export.excel { background: #28a745; }
.btn-export.word { background: #007bff; }

.btn-export:hover { opacity: 0.85; }

/* Форма добавления */
.add-form {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.add-form input {
  flex: 1;
  padding: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}

.btn-add {
  background: #ff1493;
  color: white;
  border: none;
  border-radius: 15px;
  padding: 8px 16px;
  cursor: pointer;
}

.btn-add:hover { background: #ff69b4; }

/* Фильтры */
.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filters input {
  flex: 1;
  padding: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}

/* Сетка карточек магазинов */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.store-card {
  background: #fff0f5;
  border: 1px solid #ffb6c1;
  border-radius: 15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 6px 15px rgba(255, 105, 180, 0.1);
}

.store-card small { color: #4b1a30; }

/* Кнопки на карточках */
.card-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-edit,
.btn-delete {
  border-radius: 15px;
  padding: 6px 10px;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-edit { background: #ff69b4; }
.btn-edit:hover { background: #ff1493; }

.btn-delete { background: #dc3545; }
.btn-delete:hover { background: #c82333; }

/* Модальное окно */
.modal-content input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}
</style>
