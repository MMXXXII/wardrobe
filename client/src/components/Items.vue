<template>
  <h2>Вещи</h2>

  <form @submit.prevent="onAdd" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col"><input v-model="toAdd.name" class="form-control" placeholder="Название" required /></div>
      <div class="col"><input v-model="toAdd.color" class="form-control" placeholder="Цвет" required /></div>
      <div class="col-auto">
        <select v-model="toAdd.brand" class="form-select" required>
          <option v-for="b in brands" :value="b.id" :key="b.id">{{ b.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <select v-model="toAdd.category" class="form-select" required>
          <option v-for="c in categories" :value="c.id" :key="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <ul class="list-group">
    <li v-for="i in items" :key="i.id" class="list-group-item d-flex justify-content-between">
      <div>
        <strong>{{ i.name }}</strong> — {{ i.color }}<br>
        <small class="text-muted">{{ brandsById[i.brand]?.name }} / {{ categoriesById[i.category]?.name }}</small>
      </div>
      <div>
        <button class="btn btn-sm btn-success me-2" @click="onEditClick(i)" data-bs-toggle="modal" data-bs-target="#editItemModal"><i class="bi bi-pen-fill"></i></button>
        <button class="btn btn-sm btn-danger" @click="onRemove(i)"><i class="bi bi-x"></i></button>
      </div>
    </li>
  </ul>

  <!-- Модал -->
  <div class="modal fade" id="editItemModal" tabindex="-1">
    <div class="modal-dialog"><div class="modal-content">
      <div class="modal-header">
        <h5>Редактировать вещь</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <input v-model="toEdit.name" class="form-control mb-2" />
        <input v-model="toEdit.color" class="form-control mb-2" />
        <select v-model="toEdit.brand" class="form-select mb-2">
          <option v-for="b in brands" :value="b.id">{{ b.name }}</option>
        </select>
        <select v-model="toEdit.category" class="form-select">
          <option v-for="c in categories" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
        <button class="btn btn-primary" @click="onUpdate" data-bs-dismiss="modal">Сохранить</button>
      </div>
    </div></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const items = ref([])
const brands = ref([])
const categories = ref([])

const toAdd = ref({ name: '', color: '', brand: null, category: null })
const toEdit = ref({ id: null, name: '', color: '', brand: null, category: null })

const brandsById = computed(() => Object.fromEntries(brands.value.map(b => [b.id, b])))
const categoriesById = computed(() => Object.fromEntries(categories.value.map(c => [c.id, c])))

async function fetchItems() { items.value = (await axios.get('/items/')).data }
async function fetchBrands() { brands.value = (await axios.get('/brands/')).data }
async function fetchCategories() { categories.value = (await axios.get('/categories/')).data }


async function onAdd() {
  await axios.post('/items/', { ...toAdd.value })
  toAdd.value = { name: '', color: '', brand: null, category: null }
  await fetchItems()
}

async function onRemove(i) {
  if (!confirm(`Удалить "${i.name}"?`)) return
  await axios.delete(`/items/${i.id}/`)
  await fetchItems()
}

function onEditClick(i) { toEdit.value = { ...i } }

async function onUpdate() {
  await axios.put(`/items/${toEdit.value.id}/`, { ...toEdit.value })
  await fetchItems()
}

onMounted(async () => {
  await Promise.all([fetchItems(), fetchBrands(), fetchCategories()])
})
</script>
