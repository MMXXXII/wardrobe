<template>
  <div class="buyers-page">
    <!-- Заголовок + статистика + кнопки экспорта -->
    <div class="header-stats mb-4">
      <h2>Покупатели</h2>
      <div class="stats-and-buttons">
        <div class="stats-cards">
          <div class="stat-card">Количество: {{ buyerStats?.count || 0 }}</div>
          <div class="stat-card">Среднее: {{ buyerStats?.avg || 0 }}</div>
          <div class="stat-card">Максимум: {{ buyerStats?.max || 0 }}</div>
          <div class="stat-card">Минимум: {{ buyerStats?.min || 0 }}</div>
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
    <form @submit.prevent="onAdd" class="add-form mb-4">
      <input v-model="toAdd.name" placeholder="Имя покупателя" required />
      <input v-model="toAdd.phone" placeholder="Телефон" required />
      <button type="submit" class="btn-add">Добавить</button>
    </form>

    <!-- Фильтры -->
    <div class="filters mb-4">
      <input v-model="filterName" placeholder="Фильтр по имени" />
      <input v-model="filterPhone" placeholder="Фильтр по телефону" />
    </div>

    <!-- Сетка карточек покупателей -->
    <div class="cards-grid">
      <div v-for="b in filteredBuyers" :key="b.id" class="buyer-card">
        <h4>{{ b.name }}</h4>
        <p>{{ b.phone }}</p>
        <div class="card-buttons">
          <button class="btn-edit" @click="onEditClick(b)" data-bs-toggle="modal" data-bs-target="#editBuyerModal">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn-delete" @click="onRemove(b)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editBuyerModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать покупателя</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <input v-model="toEdit.name" placeholder="Имя покупателя" />
            <input v-model="toEdit.phone" placeholder="Телефон" />
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

const buyers = ref([])
const buyerStats = ref({})
const toAdd = ref({ name: '', phone: '' })
const toEdit = ref({ id: null, name: '', phone: '' })

const filterName = ref('')
const filterPhone = ref('')

const filteredBuyers = computed(() => {
  return buyers.value.filter(b =>
    b.name.toLowerCase().includes(filterName.value.toLowerCase()) &&
    b.phone.toLowerCase().includes(filterPhone.value.toLowerCase())
  )
})

async function fetchBuyers() {
  const res = await axios.get('/buyers/')
  buyers.value = res.data
}

async function fetchBuyerStats() {
  const res = await axios.get('/buyers/stats/')
  buyerStats.value = res.data
}

async function onAdd() {
  await axios.post('/buyers/', toAdd.value)
  toAdd.value = { name: '', phone: '' }
  await fetchBuyers()
  await fetchBuyerStats()
}

async function onRemove(b) {
  if (!confirm(`Удалить "${b.name}"?`)) return
  await axios.delete(`/buyers/${b.id}/`)
  await fetchBuyers()
  await fetchBuyerStats()
}

function onEditClick(b) {
  toEdit.value = { ...b }
}

async function onUpdate() {
  await axios.put(`/buyers/${toEdit.value.id}/`, toEdit.value)
  await fetchBuyers()
  await fetchBuyerStats()
}

async function exportExcel() {
  const res = await axios.get('/buyers/export-excel/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'Buyers.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

async function exportWord() {
  const res = await axios.get('/buyers/export-word/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'Buyers.docx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

onMounted(async () => {
  await Promise.all([fetchBuyers(), fetchBuyerStats()])
})
</script>

<style scoped>
.buyers-page {
  background: #ffffff;
  padding: 25px;
  border-radius: 15px;
  font-family: 'Arial', sans-serif;
}

h2 { color: #d63384; margin-bottom: 10px; }

.stats-and-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.stats-cards { display: flex; gap: 10px; flex-wrap: wrap; }
.stat-card {
  background: #fff0f5;
  padding: 4px 10px;
  border-radius: 15px;
  color: #d63384;
  font-weight: bold;
  font-size: 0.85rem;
  box-shadow: 0 2px 6px rgba(255,105,180,0.15);
}

.export-buttons { display: flex; gap: 10px; }
.btn-export {
  font-weight: bold;
  border-radius: 15px;
  padding: 6px 14px;
  color: white;
  border: none;
  cursor: pointer;
}
.btn-export.excel { background: #28a745; }
.btn-export.word { background: #007bff; }
.btn-export:hover { opacity: 0.85; }

.add-form { display: flex; gap: 10px; flex-wrap: wrap; }
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

.filters { display: flex; gap: 10px; flex-wrap: wrap; }
.filters input {
  flex: 1;
  padding: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}

/* Сетка карточек покупателей */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.buyer-card {
  background: #fff0f5;
  border: 1px solid #ffb6c1;
  border-radius: 15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 6px 15px rgba(255, 105, 180, 0.1);
}
.buyer-card h4 { color: #d63384; margin-bottom: 8px; }
.buyer-card p { color: #4b1a30; margin-bottom: 12px; }

.card-buttons { display: flex; justify-content: flex-end; gap: 8px; }
.btn-edit, .btn-delete {
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

.modal-content input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}
</style>
