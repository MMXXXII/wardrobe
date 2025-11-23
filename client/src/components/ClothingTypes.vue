<template>
  <div class="types-page">
    <!-- Заголовок + статистика + кнопки экспорта -->
    <div class="header-stats mb-4">
      <h2>Типы одежды</h2>
      <div class="stats-and-buttons">
        <div class="stats-cards">
          <div class="stat-card">Количество: {{ typeStats?.count || 0 }}</div>
          <div class="stat-card">Среднее: {{ typeStats?.avg || 0 }}</div>
          <div class="stat-card">Максимум: {{ typeStats?.max || 0 }}</div>
          <div class="stat-card">Минимум: {{ typeStats?.min || 0 }}</div>
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
      <input v-model="toAdd.name" placeholder="Название типа одежды" required />
      <button type="submit" class="btn-add">Добавить</button>
    </form>

    <!-- Фильтр -->
    <div class="filters mb-4">
      <input v-model="filterName" placeholder="Фильтр по названию" />
    </div>

    <!-- Сетка карточек типов одежды -->
    <div class="cards-grid">
      <div v-for="t in filteredTypes" :key="t.id" class="type-card">
        <h4>{{ t.name }}</h4>
        <div class="card-buttons">
          <button class="btn-edit" @click="onEditClick(t)" data-bs-toggle="modal" data-bs-target="#editTypeModal">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn-delete" @click="onRemove(t)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editTypeModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Редактировать тип одежды</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <input v-model="toEdit.name" placeholder="Название типа одежды" />
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

const types = ref([])
const typeStats = ref({})
const toAdd = ref({ name: '' })
const toEdit = ref({ id: null, name: '' })

const filterName = ref('')

const filteredTypes = computed(() => {
  return types.value.filter(t =>
    t.name.toLowerCase().includes(filterName.value.toLowerCase())
  )
})

async function fetchAll() {
  types.value = (await axios.get('/clothing-types/')).data
}

async function fetchTypeStats() {
  typeStats.value = (await axios.get('/clothing-types/stats/')).data
}

async function onAdd() {
  await axios.post('/clothing-types/', { ...toAdd.value })
  toAdd.value = { name: '' }
  await fetchAll()
  await fetchTypeStats()
}

async function onRemove(t) {
  if (!confirm(`Удалить тип одежды "${t.name}"?`)) return
  await axios.delete(`/clothing-types/${t.id}/`)
  await fetchAll()
  await fetchTypeStats()
}

function onEditClick(t) {
  toEdit.value = { ...t }
}

async function onUpdate() {
  await axios.put(`/clothing-types/${toEdit.value.id}/`, { ...toEdit.value })
  await fetchAll()
  await fetchTypeStats()
}

async function exportExcel() {
  const res = await axios.get('/clothing-types/export-excel/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'ClothingTypes.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

async function exportWord() {
  const res = await axios.get('/clothing-types/export-word/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'ClothingTypes.docx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

onMounted(async () => {
  await fetchAll()
  await fetchTypeStats()
})
</script>

<style scoped>
.types-page {
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

.filters input {
  width: 100%;
  padding: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}

/* Сетка карточек типов одежды */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.type-card {
  background: #fff0f5;
  border: 1px solid #ffb6c1;
  border-radius: 15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 6px 15px rgba(255, 105, 180, 0.1);
}
.type-card h4 { color: #d63384; margin-bottom: 12px; }

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
