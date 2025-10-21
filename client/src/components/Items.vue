<template>
  <h2>Вещи</h2>

  <!-- Форма добавления -->
  <form @submit.prevent="onAdd" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="toAdd.name" class="form-control" placeholder="Название" required />
      </div>
      <div class="col">
        <input v-model="toAdd.color" class="form-control" placeholder="Цвет" required />
      </div>
      <div class="col-auto">
        <select v-model="toAdd.brand" class="form-select" required>
          <option disabled value="">Выберите бренд</option>
          <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
      <div class="col-auto">
        <select v-model="toAdd.category" class="form-select" required>
          <option disabled value="">Выберите категорию</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="col">
        <input type="file" @change="onItemFileChange" ref="itemPictureRef" class="form-control" />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список вещей -->
  <ul class="list-group">
    <li v-for="i in items" :key="i.id" class="list-group-item d-flex justify-content-between align-items-center">
      <div class="d-flex align-items-center gap-3">
        <img
          v-if="i.picture"
          :src="i.picture"
          alt="Фото"
          width="80"
          height="80"
          class="rounded"
          style="cursor:pointer; object-fit:cover;"
          @click="openModal(i.picture)"
        />
        <div>
          <strong>{{ i.name }}</strong> — {{ i.color }}<br />
          <small class="text-muted">
            {{ brandsById[i.brand]?.name }} / {{ categoriesById[i.category]?.name }}
          </small>
        </div>
      </div>
      <div>
        <button
          class="btn btn-sm btn-success me-2"
          @click="onEditClick(i)"
          data-bs-toggle="modal"
          data-bs-target="#editItemModal"
        >
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(i)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модальное окно редактирования -->
  <div class="modal fade" id="editItemModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать вещь</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input v-model="toEdit.name" class="form-control mb-2" placeholder="Название" />
          <input v-model="toEdit.color" class="form-control mb-2" placeholder="Цвет" />
          <select v-model="toEdit.brand" class="form-select mb-2">
            <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
          <select v-model="toEdit.category" class="form-select mb-2">
            <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <input type="file" @change="onEditFileChange" ref="editPictureRef" class="form-control mt-2" />
          <img
            v-if="toEdit.picture"
            :src="toEdit.picture"
            alt="Фото"
            class="mt-3 rounded"
            width="100"
            height="100"
            style="object-fit:cover;"
          />
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
          <button class="btn btn-primary" @click="onUpdate" data-bs-dismiss="modal">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно для увеличенного фото -->
  <div class="modal fade" id="imageModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <img :src="modalImage" class="w-100 rounded" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'

const items = ref([])
const brands = ref([])
const categories = ref([])
const itemPictureRef = ref()
const editPictureRef = ref()

const toAdd = ref({ name: '', color: '', brand: '', category: '', picture: null })
const toEdit = ref({ id: null, name: '', color: '', brand: '', category: '', picture: null })
const modalImage = ref(null)

const brandsById = computed(() => Object.fromEntries(brands.value.map(b => [b.id, b])))
const categoriesById = computed(() => Object.fromEntries(categories.value.map(c => [c.id, c])))

async function fetchItems() {
  const res = await axios.get('/items/')
  items.value = res.data
}
async function fetchBrands() {
  const res = await axios.get('/brands/')
  brands.value = res.data
}
async function fetchCategories() {
  const res = await axios.get('/categories/')
  categories.value = res.data
}

function onItemFileChange(e) {
  toAdd.value.picture = e.target.files[0]
}

function onEditFileChange(e) {
  toEdit.value.newPicture = e.target.files[0]
}

async function onAdd() {
  const formData = new FormData()
  for (const key in toAdd.value) {
    if (toAdd.value[key] !== null) formData.append(key, toAdd.value[key])
  }

  await axios.post('/items/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  toAdd.value = { name: '', color: '', brand: '', category: '', picture: null }
  itemPictureRef.value.value = ''
  await fetchItems()
}

function onEditClick(i) {
  toEdit.value = { ...i }
}

async function onUpdate() {
  const formData = new FormData()
  formData.append('name', toEdit.value.name)
  formData.append('color', toEdit.value.color)
  formData.append('brand', toEdit.value.brand)
  formData.append('category', toEdit.value.category)
  if (toEdit.value.newPicture) formData.append('picture', toEdit.value.newPicture)

  await axios.put(`/items/${toEdit.value.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  await fetchItems()
}

async function onRemove(i) {
  if (!confirm(`Удалить "${i.name}"?`)) return
  await axios.delete(`/items/${i.id}/`)
  await fetchItems()
}

function openModal(url) {
  modalImage.value = url
  const modal = new Modal(document.getElementById('imageModal'))
  modal.show()
}

onMounted(async () => {
  await Promise.all([fetchItems(), fetchBrands(), fetchCategories()])
})
</script>
