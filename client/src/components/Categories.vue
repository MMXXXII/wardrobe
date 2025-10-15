<template>
  <h2>Категории</h2>

  <form @submit.prevent="onAdd" class="mb-3 d-flex gap-2">
    <input v-model="toAdd.name" class="form-control" placeholder="Название категории" required />
    <button class="btn btn-primary">Добавить</button>
  </form>

  <ul class="list-group">
    <li v-for="c in categories" :key="c.id" class="list-group-item d-flex justify-content-between">
      {{ c.name }}
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(c)" data-bs-toggle="modal" data-bs-target="#editCategoryModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(c)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <div class="modal fade" id="editCategoryModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5>Редактировать категорию</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="toEdit.name" class="form-control" />
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

const categories = ref([])
const toAdd = ref({ name: '' })
const toEdit = ref({ id: null, name: '' })

async function fetchAll() { categories.value = (await axios.get('/categories/')).data }

async function onAdd() {
  await axios.post('/categories/', { ...toAdd.value })
  toAdd.value = { name: '' }
  await fetchAll()
}

async function onRemove(c) {
  if (!confirm(`Удалить категорию "${c.name}"?`)) return
  await axios.delete(`/categories/${c.id}/`)
  await fetchAll()
}

function onEditClick(c) {
  toEdit.value = { ...c }
}

async function onUpdate() {
  await axios.put(`/categories/${toEdit.value.id}/`, { ...toEdit.value })
  await fetchAll()
}

onMounted(fetchAll)
</script>
