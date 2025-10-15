<template>
  <h2>Бренды</h2>

  <form @submit.prevent="onAdd" class="mb-3">
    <div class="row g-2">
      <div class="col">
        <input v-model="toAdd.name" class="form-control" placeholder="Название бренда" required />
      </div>
      <div class="col">
        <input v-model="toAdd.description" class="form-control" placeholder="Описание" required />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <ul class="list-group">
    <li v-for="b in brands" :key="b.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ b.name }}</strong><br>
        <small class="text-muted">{{ b.description }}</small>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(b)" data-bs-toggle="modal" data-bs-target="#editBrandModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(b)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модал -->
  <div class="modal fade" id="editBrandModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать бренд</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="toEdit.name" class="form-control mb-2" />
          <textarea v-model="toEdit.description" class="form-control"></textarea>
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
import { ref, onMounted } from 'vue'
import axios from 'axios'

const brands = ref([])
const toAdd = ref({ name: '', description: '' })
const toEdit = ref({ id: null, name: '', description: '' })

// Загружаем бренды
async function fetchAll() {
  const res = await axios.get('/brands/')
  brands.value = res.data
}

// Добавление бренда
async function onAdd() {
  await axios.post('/brands/', { ...toAdd.value })
  toAdd.value = { name: '', description: '' }
  await fetchAll()
}

// Удаление бренда
async function onRemove(b) {
  if (!confirm(`Удалить бренд "${b.name}"?`)) return
  await axios.delete(`/brands/${b.id}/`)
  await fetchAll()
}

// Подготовка к редактированию
function onEditClick(b) {
  toEdit.value = { ...b }
}

// Обновление бренда
async function onUpdate() {
  await axios.put(`/brands/${toEdit.value.id}/`, { ...toEdit.value })
  await fetchAll()
}

// При загрузке страницы
onMounted(fetchAll)
</script>
