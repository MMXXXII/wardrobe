<template>
  <h2>Магазины</h2>

  <form @submit.prevent="onAdd" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="toAdd.name" class="form-control" placeholder="Название магазина" required />
      </div>
      <div class="col">
        <input v-model="toAdd.address" class="form-control" placeholder="Адрес" required />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <ul class="list-group">
    <li v-for="s in stores" :key="s.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ s.name }}</strong><br>
        <small class="text-muted">{{ s.address }}</small>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(s)" data-bs-toggle="modal" data-bs-target="#editStoreModal">
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(s)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модал редактирования -->
  <div class="modal fade" id="editStoreModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5>Редактировать магазин</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="toEdit.name" class="form-control mb-2" placeholder="Название" />
          <input v-model="toEdit.address" class="form-control" placeholder="Адрес" />
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

const stores = ref([])
const toAdd = ref({ name: '', address: '' })
const toEdit = ref({ id: null, name: '', address: '' })

async function fetchAll() {
  stores.value = (await axios.get('/stores/')).data
}

async function onAdd() {
  await axios.post('/stores/', { ...toAdd.value })
  toAdd.value = { name: '', address: '' }
  await fetchAll()
}

async function onRemove(s) {
  if (!confirm(`Удалить магазин "${s.name}"?`)) return
  await axios.delete(`/stores/${s.id}/`)
  await fetchAll()
}

function onEditClick(s) {
  toEdit.value = { ...s }
}

async function onUpdate() {
  await axios.put(`/stores/${toEdit.value.id}/`, { ...toEdit.value })
  await fetchAll()
}

onMounted(fetchAll)
</script>
