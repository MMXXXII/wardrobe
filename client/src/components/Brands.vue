<template>
  <h2>Бренды</h2>

  <!-- Форма добавления -->
  <form @submit.prevent="onAdd" class="mb-3">
    <div class="row g-2 align-items-center">
      <div class="col">
        <input v-model="toAdd.name" class="form-control" placeholder="Название бренда" required />
      </div>
      <div class="col">
        <input v-model="toAdd.description" class="form-control" placeholder="Описание" required />
      </div>
      <div class="col">
        <input type="file" @change="onBrandFileChange" ref="brandPictureRef" class="form-control" />
      </div>
      <div class="col-auto">
        <button class="btn btn-primary">Добавить</button>
      </div>
    </div>
  </form>

  <!-- Список брендов -->
  <ul class="list-group">
    <li
      v-for="b in brands"
      :key="b.id"
      class="list-group-item d-flex justify-content-between align-items-center"
    >
      <div class="d-flex align-items-center gap-3">
        <img
          v-if="b.picture"
          :src="b.picture"
          alt="Фото бренда"
          width="80"
          height="80"
          class="rounded"
          style="cursor:pointer; object-fit:cover;"
          @click="openModal(b.picture)"
        />
        <div>
          <strong>{{ b.name }}</strong><br />
          <small class="text-muted">{{ b.description }}</small>
        </div>
      </div>

      <div>
        <button
          class="btn btn-sm btn-success me-2"
          @click="onEditClick(b)"
          data-bs-toggle="modal"
          data-bs-target="#editBrandModal"
        >
          <i class="bi bi-pen-fill"></i>
        </button>
        <button class="btn btn-sm btn-danger" @click="onRemove(b)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </li>
  </ul>

  <!-- Модальное окно редактирования -->
  <div class="modal fade" id="editBrandModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Редактировать бренд</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <div class="modal-body">
          <input v-model="toEdit.name" class="form-control mb-2" placeholder="Название" />
          <textarea
            v-model="toEdit.description"
            class="form-control mb-2"
            placeholder="Описание"
          ></textarea>
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
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Modal } from 'bootstrap'

const brands = ref([])
const brandPictureRef = ref()
const editPictureRef = ref()
const modalImage = ref(null)

const toAdd = ref({ name: '', description: '', picture: null })
const toEdit = ref({ id: null, name: '', description: '', picture: null })

// Загрузка списка брендов
async function fetchBrands() {
  const res = await axios.get('/brands/')
  brands.value = res.data
}

// Добавление бренда
function onBrandFileChange(e) {
  toAdd.value.picture = e.target.files[0]
}

async function onAdd() {
  const formData = new FormData()
  for (const key in toAdd.value) {
    if (toAdd.value[key] !== null) formData.append(key, toAdd.value[key])
  }

  await axios.post('/brands/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  toAdd.value = { name: '', description: '', picture: null }
  brandPictureRef.value.value = ''
  await fetchBrands()
}

// Удаление бренда
async function onRemove(b) {
  if (!confirm(`Удалить бренд "${b.name}"?`)) return
  await axios.delete(`/brands/${b.id}/`)
  await fetchBrands()
}

// Редактирование бренда
function onEditClick(b) {
  toEdit.value = { ...b }
}

function onEditFileChange(e) {
  toEdit.value.newPicture = e.target.files[0]
}

async function onUpdate() {
  const formData = new FormData()
  formData.append('name', toEdit.value.name)
  formData.append('description', toEdit.value.description)
  if (toEdit.value.newPicture) formData.append('picture', toEdit.value.newPicture)

  await axios.put(`/brands/${toEdit.value.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  await fetchBrands()
}

// Модалка для увеличенного изображения
function openModal(url) {
  modalImage.value = url
  const modal = new Modal(document.getElementById('imageModal'))
  modal.show()
}

onMounted(fetchBrands)
</script>
