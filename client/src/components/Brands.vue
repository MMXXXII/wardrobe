<template>
  <div class="brands-page">
    <div class="header-stats">
      <h2>Бренды</h2>
      <div class="stats-and-buttons">
        <div class="stats-cards">
          <div class="stat-card">Количество: {{ brandStats?.count || 0 }}</div>
          <div class="stat-card">Среднее: {{ brandStats?.avg || 0 }}</div>
          <div class="stat-card">Максимум: {{ brandStats?.max || 0 }}</div>
          <div class="stat-card">Минимум: {{ brandStats?.min || 0 }}</div>
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

    <form @submit.prevent="onAdd" class="add-form">
      <input v-model="toAdd.name" placeholder="Название бренда" required />
      <input v-model="toAdd.description" placeholder="Описание" required />
      <input type="file" @change="onFileChange($event, toAdd)" />
      <button type="submit" class="btn-add">Добавить</button>
    </form>

    <div class="filters">
      <input v-model="filterName" placeholder="Фильтр по названию" />
      <input v-model="filterDescription" placeholder="Фильтр по описанию" />
    </div>

    <div class="cards-grid">
      <div v-for="b in filteredBrands" :key="b.id" class="brand-card">
        <h4>{{ b.name }}</h4>
        <p>{{ b.description }}</p>
        <img v-if="b.image" :src="b.image" class="brand-image" @click="openImageModal(b.image)" />
        <div class="card-buttons">
          <button class="btn-edit" @click="onEditClick(b)" data-bs-toggle="modal" data-bs-target="#editBrandModal">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn-delete" @click="onRemove(b)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editBrandModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5>Редактировать бренд</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <input v-model="toEdit.name" placeholder="Название бренда" />
            <input v-model="toEdit.description" placeholder="Описание" />
            <input type="file" @change="onFileChange($event, toEdit)" />
            <div v-if="toEdit.image" class="edit-image-preview">
              <img :src="toEdit.image" @click="openImageModal(toEdit.image)" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button class="btn btn-primary" @click="onUpdate" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="imageModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-body text-center">
            <img :src="currentImage" class="img-fluid" />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const brands = ref([])
const brandStats = ref({})
const toAdd = ref({ name: '', description: '', image: null })
const toEdit = ref({ id: null, name: '', description: '', image: null })

const filterName = ref('')
const filterDescription = ref('')
const currentImage = ref(null)

const filteredBrands = computed(() => brands.value.filter(b =>
  b.name.toLowerCase().includes(filterName.value.toLowerCase()) &&
  b.description.toLowerCase().includes(filterDescription.value.toLowerCase())
))

function onFileChange(event, target) {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = e => target.image = e.target.result
  reader.readAsDataURL(file)
}

function openImageModal(src) {
  currentImage.value = src
  const modal = new bootstrap.Modal(document.getElementById('imageModal'))
  modal.show()
}

async function fetchBrands() {
  const res = await axios.get('/brands/')
  brands.value = res.data
}

async function fetchBrandStats() {
  const res = await axios.get('/brands/stats/')
  brandStats.value = res.data
}

async function onAdd() {
  const formData = new FormData()
  formData.append('name', toAdd.value.name)
  formData.append('description', toAdd.value.description)
  if (toAdd.value.image) formData.append('image', toAdd.value.image)
  await axios.post('/brands/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  toAdd.value = { name: '', description: '', image: null }
  await fetchBrands()
  await fetchBrandStats()
}

async function onRemove(b) {
  if (!confirm(`Удалить "${b.name}"?`)) return
  await axios.delete(`/brands/${b.id}/`)
  await fetchBrands()
  await fetchBrandStats()
}

function onEditClick(b) {
  toEdit.value = { ...b }
}

async function onUpdate() {
  const formData = new FormData()
  formData.append('name', toEdit.value.name)
  formData.append('description', toEdit.value.description)
  if (toEdit.value.image) formData.append('image', toEdit.value.image)
  await axios.put(`/brands/${toEdit.value.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  await fetchBrands()
  await fetchBrandStats()
}

async function exportExcel() {
  const res = await axios.get('/brands/export-excel/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'Brands.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

async function exportWord() {
  const res = await axios.get('/brands/export-word/', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'Brands.docx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

onMounted(async () => {
  await Promise.all([fetchBrands(), fetchBrandStats()])
})
</script>

<style scoped>
.brands-page {
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
  flex-wrap: wrap;
  gap: 15px;
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
  box-shadow: 0 2px 6px rgba(255,105,180,0.15);
}

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
}
.btn-export.excel { background: #28a745; }
.btn-export.word { background: #007bff; }
.btn-export:hover { opacity: 0.85; }

.add-form {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 20px;
}
.add-form input[type="text"],
.add-form input[type="file"] {
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
  height: 42px;
}
.btn-add:hover { background: #ff69b4; }

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}
.filters input {
  flex: 1;
  padding: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}
.brand-card {
  background: #fff0f5;
  border: 1px solid #ffb6c1;
  border-radius: 15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 6px 15px rgba(255,105,180,0.1);
}
.brand-card h4 { color: #d63384; margin-bottom: 8px; }
.brand-card p { flex: 1; color: #4b1a30; margin-bottom: 12px; }
.brand-image {
  width: 100%;
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
}
.edit-image-preview img {
  width: 100%;
  border-radius: 10px;
  cursor: pointer;
}

.card-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
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

.modal-content input { width: 100%; padding: 10px; margin-bottom: 10px; border-radius: 15px; border: 1px solid #ffb6c1; background-color: #fff0f5; }
</style>
