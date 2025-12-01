<template>
  <div class="products-page">
    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Красивый заголовок -->
    <div class="header-section">
      <div class="header-content">
        <div class="header-icon">👔</div>
        <h1 class="page-title">Товары</h1>
        <p class="header-subtitle">Управляй каталогом одежды</p>
      </div>
    </div>

    <!-- Статистика -->
    <div class="stats-container">
      <div class="stat-item stat-count">
        <div class="stat-icon">📦</div>
        <div class="stat-info">
          <div class="stat-label">Всего товаров</div>
          <div class="stat-value">{{ productStats?.count || 0 }}</div>
        </div>
      </div>
      <div class="stat-item stat-price">
        <div class="stat-icon">💰</div>
        <div class="stat-info">
          <div class="stat-label">Средняя цена</div>
          <div class="stat-value">{{ productStats?.avg_price || 0 }} ₽</div>
        </div>
      </div>
      <div v-if="productStats?.most_ordered" class="stat-item stat-popular">
        <div class="stat-icon">⭐</div>
        <div class="stat-info">
          <div class="stat-label">Популярный</div>
          <div class="stat-value-text">{{ productStats.most_ordered.name }}</div>
        </div>
      </div>
      <div class="stat-item stat-action">
        <div class="stat-icon">📥</div>
        <div class="stat-info">
          <div class="stat-label">Экспорт</div>
          <div class="export-quick-buttons">
            <button class="btn-quick-export excel" @click="exportExcel" title="Excel">
              <i class="bi bi-file-earmark-spreadsheet-fill"></i>
            </button>
            <button class="btn-quick-export word" @click="exportWord" title="Word">
              <i class="bi bi-file-earmark-word-fill"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Форма добавления -->
    <div class="add-section" v-if="isAdmin">
      <div class="add-card">
        <h3 class="add-title">✨ Добавить новый товар</h3>
        <form @submit.prevent="onAdd" class="add-form">
          <div class="form-row">
            <input v-model="toAdd.name" placeholder="Название товара" class="input-elegant" required />
            <select v-model="toAdd.category" class="input-elegant" required>
              <option value="" disabled>Выберите категорию</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <div class="form-row">
            <select v-model="toAdd.store" class="input-elegant" required>
              <option value="" disabled>Выберите магазин</option>
              <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
            <select v-model="toAdd.size" class="input-elegant" required>
              <option value="" disabled>Размер</option>
              <option value="XS">XS</option>
              <option value="S">S</option>
              <option value="M">M</option>
              <option value="L">L</option>
              <option value="XL">XL</option>
              <option value="XXL">XXL</option>
            </select>
          </div>

          <div class="form-row">
            <input v-model.number="toAdd.price" type="number" step="0.01" placeholder="Цена (₽)" class="input-elegant"
              required />
            <input v-model="toAdd.color" placeholder="Цвет" class="input-elegant" />
            <input v-model.number="toAdd.quantity" type="number" placeholder="Количество" class="input-elegant"
              required />
          </div>
          <div class="form-row file-row">
            <input type="file" @change="onFileChange" accept="image/*" class="file-input" />
            <button type="submit" class="btn-add-elegant">
              <i class="bi bi-plus-circle"></i> Добавить товар
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filter-section">
      <div class="filter-wrapper">
        <i class="bi bi-search"></i>
        <input v-model="filterName" placeholder="Поиск по названию..." class="filter-input" />
      </div>

      <select v-model="filterCategory" class="filter-select">
        <option value="">Все категории</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>

      <select v-model="filterSize" class="filter-select">
        <option value="">Все размеры</option>
        <option value="XS">XS</option>
        <option value="S">S</option>
        <option value="M">M</option>
        <option value="L">L</option>
        <option value="XL">XL</option>
        <option value="XXL">XXL</option>
      </select>

      <div class="result-count" v-if="filteredProducts.length > 0">
        Найдено: <strong>{{ filteredProducts.length }}</strong>
      </div>
    </div>

    <!-- Сетка карточек товаров -->
    <div class="cards-grid">
      <div v-if="filteredProducts.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p class="empty-text">Товары не найдены</p>
      </div>

      <div v-for="(p, index) in filteredProducts" :key="p.id" class="product-card"
        :style="{ '--delay': index * 0.05 + 's' }">

        <div class="product-image-wrapper">
          <img v-if="p.image" :src="p.image" class="product-image" @click="openImageModal(p.image)" />
          <div v-else class="product-image-placeholder">
            <i class="bi bi-image"></i>
          </div>
        </div>

        <div class="product-content">
          <h4 class="product-title">{{ p.name }}</h4>
          <div class="product-badges">
            <span class="badge-size">{{ p.size }}</span>
            <span v-if="p.color" class="badge-color" :style="{ '--color': getColorHex(p.color) }">
              {{ p.color }}
            </span>
          </div>
          <div class="product-meta">
            <span class="meta-category">{{ p.category_name }}</span>
            <span class="meta-store">{{ p.store_name }}</span>
            <span class="product-quantity">Количество: {{ p.quantity }}</span>
          </div>
          <div class="product-price">{{ p.price }} ₽</div>
        </div>

        <!-- КНОПКИ СПРАВА -->
        <div class="product-actions" v-if="isAdmin">
          <button class="btn-action edit" @click="onEditClick(p)" title="Редактировать">
            <i class="bi bi-pencil-square"></i>
          </button>
          <button class="btn-action delete" @click="onRemoveClick(p)" title="Удалить">
            <i class="bi bi-trash3"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Product Modal -->
    <div class="modal fade" id="editProductModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content modal-elegant-content">
          <div class="modal-header modal-elegant-header">
            <h5 class="modal-title"><i class="bi bi-pencil-square"></i> Редактировать товар</h5>
            <button type="button" class="btn-close btn-close-white" @click="hideEditModal"></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Название</label>
              <input v-model="toEdit.name" class="input-elegant" />
            </div>
            <div class="form-group">
              <label class="form-label">Категория</label>
              <select v-model="toEdit.category" class="input-elegant">
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Магазин</label>
              <select v-model="toEdit.store" class="input-elegant">
                <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Размер</label>
              <select v-model="toEdit.size" class="input-elegant">
                <option value="XS">XS</option>
                <option value="S">S</option>
                <option value="M">M</option>
                <option value="L">L</option>
                <option value="XL">XL</option>
                <option value="XXL">XXL</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Цена (₽)</label>
              <input v-model.number="toEdit.price" type="number" step="0.01" class="input-elegant" />
            </div>
            <div class="form-group">
              <label class="form-label">Цвет</label>
              <input v-model="toEdit.color" class="input-elegant" />
            </div>
            <div class="form-group">
              <label class="form-label">Количество</label>
              <input v-model.number="toEdit.quantity" type="number" class="input-elegant" />
            </div>
            <div class="form-group">
              <label class="form-label">Фото</label>
              <input type="file" @change="onFileChangeEdit" accept="image/*" class="form-control" />
            </div>
            <div v-if="toEdit.imagePreview" class="edit-image-preview">
              <img :src="toEdit.imagePreview" @click="openImageModal(toEdit.imagePreview)" />
            </div>
          </div>
          <div class="modal-footer modal-elegant-footer">
            <button class="btn btn-secondary" @click="hideEditModal">Отмена</button>
            <button class="btn btn-elegant" @click="onUpdate">
              <i class="bi bi-check-circle"></i> Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Product Modal -->
    <div class="modal fade" id="deleteProductModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content modal-elegant-content">
          <div class="modal-header modal-elegant-header delete-header">
            <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill"></i> Подтверждение удаления</h5>
            <button type="button" class="btn-close btn-close-white" @click="hideDeleteModal"></button>
          </div>
          <div class="modal-body delete-modal-body">
            <div class="delete-icon">🗑️</div>
            <p class="delete-confirm-text">Вы уверены, что хотите удалить товар?</p>
            <p class="delete-product-name">"{{ productToDelete.name }}"</p>
          </div>
          <div class="modal-footer modal-elegant-footer delete-footer">
            <button class="btn btn-secondary" @click="hideDeleteModal">Отмена</button>
            <button class="btn btn-danger" @click="confirmDelete">
              <i class="bi bi-trash3"></i> Удалить товар
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Modal -->
    <div class="modal fade" id="imageModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content modal-image-content">
          <div class="modal-body text-center">
            <img :src="currentImage" class="img-fluid modal-image" />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="hideImageModal">Закрыть</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

const products = ref([])
const categories = ref([])
const stores = ref([])
const productStats = ref({})
const toAdd = reactive({ name: '', category: '', store: '', size: 'M', price: 0, color: '', quantity: 0, image: null })
const toEdit = reactive({ id: null, name: '', category: '', store: '', size: 'M', price: 0, color: '', quantity: 0, image: null, imagePreview: null })
const productToDelete = reactive({ id: null, name: '' })
const filterName = ref('')
const filterCategory = ref('')
const filterSize = ref('')
const currentImage = ref(null)
const user = ref(null)
const isAdmin = computed(() => user.value?.is_superuser)

const notification = reactive({
  visible: false,
  message: '',
  type: 'success',
  _timeoutId: null
})

function showNotification(msg, type = "success", duration = 2000) {
  if (notification._timeoutId) clearTimeout(notification._timeoutId)
  notification.message = msg
  notification.type = type
  notification.visible = true
  notification._timeoutId = setTimeout(() => notification.visible = false, duration)
}

function handleApiError(err, fallbackMessage = 'Ошибка') {
  console.error(err)
  const msg = err?.response?.data?.detail || err?.message || fallbackMessage
  showNotification(msg, 'danger')
}

function getColorHex(colorName) {
  const colors = {
    'красный': '#FF0000',
    'синий': '#0000FF',
    'зелёный': '#00FF00',
    'жёлтый': '#FFFF00',
    'чёрный': '#000000',
    'белый': '#FFFFFF',
    'серый': '#808080',
    'розовый': '#FFC0CB',
    'оранжевый': '#FFA500',
    'фиолетовый': '#800080',
  }
  return colors[colorName.toLowerCase()] || '#cccccc'
}

const filteredProducts = computed(() =>
  products.value.filter(p =>
    p.name.toLowerCase().includes(filterName.value.toLowerCase()) &&
    (!filterCategory.value || p.category === Number(filterCategory.value)) &&
    (!filterSize.value || p.size === filterSize.value)
  )
)

function onFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  toAdd.image = file
}

function onFileChangeEdit(event) {
  const file = event.target.files[0]
  if (!file) return
  toEdit.image = file
}

function openImageModal(src) {
  currentImage.value = src
  const modal = new bootstrap.Modal(document.getElementById('imageModal'))
  modal.show()
}

function hideImageModal() {
  const modalEl = document.getElementById('imageModal')
  const modalInstance = bootstrap.Modal.getInstance(modalEl)
  if (modalInstance) modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

async function fetchUser() {
  try {
    const r = await axios.get('/userprofile/info/')
    user.value = r.data
  } catch (err) {
    handleApiError(err, 'Не удалось получить информацию о пользователе')
  }
}

async function fetchAll() {
  try {
    products.value = (await axios.get('/products/')).data
    categories.value = (await axios.get('/categories/')).data
    stores.value = (await axios.get('/stores/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить данные')
  }
}

async function fetchProductStats() {
  try {
    productStats.value = (await axios.get('/products/stats/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику')
  }
}

async function onAdd() {
  try {
    const formData = new FormData()
    formData.append('name', toAdd.name)
    formData.append('category', toAdd.category)
    formData.append('store', toAdd.store)
    formData.append('size', toAdd.size)
    formData.append('price', toAdd.price)
    formData.append('quantity', toAdd.quantity)
    if (toAdd.color) formData.append('color', toAdd.color)
    if (toAdd.image) formData.append('image', toAdd.image)

    await axios.post('/products/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })

    Object.assign(toAdd, { name: '', category: '', store: '', size: 'M', price: 0, color: '', quantity: 0, image: null })
    const fileInput = document.querySelector('.file-input')
    if (fileInput) fileInput.value = ''

    await Promise.all([fetchAll(), fetchProductStats()])
    showNotification('✨ Товар добавлен!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении')
  }
}

function onEditClick(p) {
  Object.assign(toEdit, { ...p, image: null, imagePreview: p.image })
  const modal = new bootstrap.Modal(document.getElementById('editProductModal'))
  modal.show()
}

async function onUpdate() {
  try {
    const formData = new FormData()
    formData.append('name', toEdit.name)
    formData.append('category', toEdit.category)
    formData.append('store', toEdit.store)
    formData.append('size', toEdit.size)
    formData.append('price', toEdit.price)
    formData.append('quantity', toEdit.quantity)
    if (toEdit.color) formData.append('color', toEdit.color)
    if (toEdit.image) formData.append('image', toEdit.image)

    await axios.put(`/products/${toEdit.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    await Promise.all([fetchAll(), fetchProductStats()])
    hideEditModal()
    showNotification('💾 Изменения сохранены!', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении')
  }
}

function onRemoveClick(p) {
  productToDelete.id = p.id
  productToDelete.name = p.name
  const modal = new bootstrap.Modal(document.getElementById('deleteProductModal'))
  modal.show()
}

async function confirmDelete() {
  try {
    await axios.delete(`/products/${productToDelete.id}/`)
    await Promise.all([fetchAll(), fetchProductStats()])
    hideDeleteModal()
    showNotification('🗑️ Товар удален', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении')
  }
}

async function exportExcel() {
  try {
    const res = await axios.get('/products/export/?type=excel', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Products.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('📊 Excel скачан!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании')
  }
}

async function exportWord() {
  try {
    const res = await axios.get('/products/export/?type=word', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Products.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('📄 Word скачан!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании')
  }
}

function hideEditModal() {
  const modalEl = document.getElementById('editProductModal')
  const modalInstance = bootstrap.Modal.getInstance(modalEl)
  if (modalInstance) modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

function hideDeleteModal() {
  const modalEl = document.getElementById('deleteProductModal')
  const modalInstance = bootstrap.Modal.getInstance(modalEl)
  if (modalInstance) modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

onMounted(() => {
  fetchUser()
  Promise.all([fetchAll(), fetchProductStats()])
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.products-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fef5f5 0%, #f5f0ff 100%);
  padding: 40px 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  border-radius: 25px;
}

.header-section {
  text-align: center;
  margin-bottom: 50px;
  animation: slideDown 0.6s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-icon {
  font-size: 4rem;
  margin-bottom: 15px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-10px);
  }
}

.page-title {
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #ff6b9d, #c44569, #f8b500);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 10px 0;
}

.header-subtitle {
  font-size: 1.2rem;
  color: #666;
  margin: 0;
  font-weight: 300;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 50px;
  animation: slideUp 0.6s ease 0.1s both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-item {
  background: white;
  border-radius: 20px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 10px 40px rgba(255, 107, 157, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 50px rgba(255, 107, 157, 0.15);
  border-color: #ffc0cb;
}

.stat-count {
  border-left: 5px solid #ff6b9d;
}

.stat-price {
  border-left: 5px solid #f8b500;
}

.stat-popular {
  border-left: 5px solid #c44569;
}

.stat-action {
  border-left: 5px solid #28a745;
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

.stat-value {
  font-size: 2rem;
  font-weight: 800;
  color: #ff6b9d;
  margin-top: 5px;
}

.stat-value-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #c44569;
  margin-top: 5px;
}

.export-quick-buttons {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.btn-quick-export {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-quick-export.excel {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.btn-quick-export.word {
  background: linear-gradient(135deg, #007bff, #0056b3);
}

.btn-quick-export:hover {
  transform: scale(1.15) rotate(10deg);
}

.add-section {
  margin-bottom: 50px;
  animation: slideUp 0.6s ease 0.2s both;
}

.add-card {
  background: white;
  border-radius: 25px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(255, 107, 157, 0.1);
  border: 2px solid #fff0f5;
  transition: all 0.3s ease;
}

.add-card:hover {
  box-shadow: 0 15px 60px rgba(255, 107, 157, 0.15);
  border-color: #ffc0cb;
}

.add-title {
  margin: 0 0 20px 0;
  color: #ff6b9d;
  font-size: 1.5rem;
  font-weight: 700;
}

.add-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.input-elegant {
  flex: 1;
  min-width: 200px;
  padding: 14px 20px;
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  font-size: 1rem;
  background: linear-gradient(135deg, #fff5f8, #f5f0ff);
  transition: all 0.3s ease;
  font-family: inherit;
}

.input-elegant:focus {
  outline: none;
  border-color: #ff6b9d;
  background: white;
  box-shadow: 0 0 15px rgba(255, 107, 157, 0.2);
}

.file-row {
  display: flex;
  gap: 15px;
  align-items: center;
}

.file-input {
  flex: 1;
  min-width: 200px;
  padding: 14px 20px;
  border: 2px dashed #ff6b9d;
  border-radius: 15px;
  background: linear-gradient(135deg, #fff5f8, #f5f0ff);
  cursor: pointer;
}

.btn-add-elegant {
  padding: 14px 28px;
  background: linear-gradient(135deg, #ff6b9d, #c44569);
  color: white;
  border: none;
  border-radius: 15px;
  font-weight: 700;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn-add-elegant:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(255, 107, 157, 0.3);
}

.filter-section {
  display: flex;
  gap: 15px;
  margin-bottom: 40px;
  flex-wrap: wrap;
  align-items: center;
  animation: slideUp 0.6s ease 0.3s both;
}

.filter-wrapper {
  flex: 1;
  min-width: 250px;
  position: relative;
  display: flex;
  align-items: center;
}

.filter-wrapper i {
  position: absolute;
  left: 15px;
  color: #ff6b9d;
  pointer-events: none;
}

.filter-input {
  width: 100%;
  padding: 14px 20px 14px 45px;
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
}

.filter-input:focus {
  outline: none;
  border-color: #ff6b9d;
  box-shadow: 0 0 15px rgba(255, 107, 157, 0.2);
}

.filter-select {
  padding: 14px 20px;
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 180px;
}

.filter-select:focus {
  outline: none;
  border-color: #ff6b9d;
  box-shadow: 0 0 15px rgba(255, 107, 157, 0.2);
}

.result-count {
  color: #666;
  font-weight: 600;
  padding: 8px 16px;
  background: #fff0f5;
  border-radius: 20px;
}

.result-count strong {
  color: #ff6b9d;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: bounce 2s ease infinite;
}

@keyframes bounce {

  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-20px);
  }
}

.empty-text {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
  font-weight: 700;
}

.product-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 35px rgba(255, 107, 157, 0.08);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  animation: cardAppear 0.5s ease forwards;
  animation-delay: var(--delay);
}

@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(255, 107, 157, 0.15);
  border-color: #ffb6c1;
}

.product-image-wrapper {
  width: 60px;
  height: 60px;
  border-radius: 15px;
  overflow: hidden;
  background: #fff0f5;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-image {
  width: 100%;
  height: auto;
  object-fit: cover;
  border-radius: 15px;
  cursor: pointer;
}

.product-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: #f0f0f0;
  border-radius: 15px;
  color: #ccc;
  font-size: 2rem;
}

.product-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.product-title {
  font-weight: 700;
  color: #333;
  font-size: 1.15rem;
  margin-bottom: 3px;
}

.product-badges {
  display: flex;
  gap: 8px;
}

.badge-size,
.badge-color {
  background: #ffffff; /* белый фон */
  color: #333333;      /* тёмный текст для читаемости */
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid #ddd; /* лёгкая граница для контраста */
}

.product-meta {
  font-size: 0.9rem;
  color: #666;
  display: flex;
  gap: 10px;
}

.product-price {
  font-size: 1.15rem;
  font-weight: 700;
  color: #c44569;
}

.product-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
  justify-content: center;
  margin-left: 10px;
}

.btn-action {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.btn-action.edit {
  background: linear-gradient(135deg, #ff6b9d, #c44569);
}

.btn-action.edit:hover {
  transform: scale(1.15) rotate(-10deg);
}

.btn-action.delete {
  background: linear-gradient(135deg, #dc3545, #c82333);
}

.btn-action.delete:hover {
  transform: scale(1.15) rotate(10deg);
}

.modal-elegant-content {
  border: none;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-elegant-header {
  background: linear-gradient(135deg, #ff6b9d, #c44569);
  color: white;
  border: none;
  border-radius: 20px 20px 0 0;
  padding: 25px;
}

.modal-elegant-header .modal-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1.3rem;
}

.btn-close-white {
  filter: brightness(0) invert(1);
}

.modal-body {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #ff6b9d;
  font-weight: 700;
  font-size: 0.95rem;
}

.edit-image-preview {
  margin-top: 15px;
  text-align: center;
}

.edit-image-preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: 15px;
  box-shadow: 0 5px 20px rgba(255, 107, 157, 0.15);
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-image-preview img:hover {
  transform: scale(1.05);
}

.delete-confirm-text {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 10px;
  line-height: 1.6;
  text-align: center;
}

.delete-product-name {
  font-size: 1.3rem;
  color: #dc3545;
  font-weight: 700;
  margin-bottom: 15px;
  text-align: center;
  word-break: break-word;
}

.delete-confirm-warning {
  font-size: 0.9rem;
  color: #dc3545;
  font-weight: 600;
  margin: 0;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.delete-icon {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 15px;
  animation: deleteShake 0.5s ease;
}

@keyframes deleteShake {

  0%,
  100% {
    transform: translateX(0) rotate(0deg);
  }

  25% {
    transform: translateX(-5px) rotate(-2deg);
  }

  75% {
    transform: translateX(5px) rotate(2deg);
  }
}

.modal-elegant-header.delete-header {
  background: linear-gradient(135deg, #dc3545, #c82333);
}

.delete-modal-body {
  padding: 30px;
  text-align: center;
  background: linear-gradient(135deg, #fff5f5, #ffe6e6);
}

.delete-footer {
  justify-content: center;
  gap: 15px;
}

.modal-elegant-footer {
  background: #f5f5f5;
  border-top: 2px solid #f0f0f0;
  border-radius: 0 0 20px 20px;
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-elegant {
  background: linear-gradient(135deg, #ff6b9d, #c44569) !important;
  border: none !important;
  color: white !important;
  font-weight: 700 !important;
  display: flex !important;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease !important;
  padding: 10px 20px !important;
  border-radius: 10px !important;
}

.btn-elegant:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 30px rgba(255, 107, 157, 0.3) !important;
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545, #c82333) !important;
  border: none !important;
  color: white !important;
  font-weight: 700 !important;
  display: flex !important;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease !important;
  padding: 10px 20px !important;
  border-radius: 10px !important;
}

.btn-danger:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 30px rgba(220, 53, 69, 0.3) !important;
}

.modal-image-content {
  border: none;
  border-radius: 20px;
  background: #000;
}

.modal-image {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 15px;
}

.notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  padding: 16px 24px;
  border-radius: 15px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  z-index: 2000;
  font-size: 1rem;
  font-weight: 600;
  max-width: 90%;
  text-align: center;
}

.notif-fade-enter-active,
.notif-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.notif-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.notif-fade-enter-to {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.notif-fade-leave-from {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.notif-fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.notification-success {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.notification-danger {
  background: linear-gradient(135deg, #dc3545, #c82333);
}

.notification-warning {
  background: linear-gradient(135deg, #ffc107, #ff9800);
  color: #000;
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 2.5rem;
  }

  .product-card {
    flex-wrap: wrap;
  }

  .product-actions {
    width: 100%;
    flex-direction: row;
    justify-content: flex-end;
  }
}
</style>