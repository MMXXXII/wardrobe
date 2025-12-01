<template>
  <div class="categories-page">
    <!-- Уведомления -->
    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Красивый заголовок с градиентом -->
    <div class="header-section">
      <div class="header-content">
        <div class="header-icon">👗</div>
        <h1 class="page-title">Категории одежды</h1>
        <p class="header-subtitle">Управляй своей коллекцией стилей</p>
      </div>
    </div>

    <!-- Статистика красивая -->
    <div class="stats-container">
      <div class="stat-item stat-count">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-label">Всего категорий</div>
          <div class="stat-value">{{ categoryStats?.count || 0 }}</div>
        </div>
      </div>
      <div class="stat-item stat-popular">
        <div class="stat-icon">⭐</div>
        <div class="stat-info">
          <div class="stat-label">Самая популярная</div>
          <div class="stat-value">{{ categoryStats?.top || 'N/A' }}</div>
        </div>
      </div>
      <div v-if="isAdmin" class="stat-item stat-action">
        <div class="stat-icon">📥</div>
        <div class="stat-info">
          <div class="stat-label">Быстрый экспорт</div>
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

    <!-- Форма добавления красивая -->
    <div class="add-section" v-if="isAdmin">
      <div class="add-card">
        <h3 class="add-title">✨ Добавить новую категорию</h3>
        <form @submit.prevent="onAdd" class="add-form">
          <div class="form-group">
            <input v-model="toAdd.name" placeholder="Введите название категории..." class="input-elegant" required />
            <button type="submit" class="btn-add-elegant">
              <i class="bi bi-plus-circle"></i> Добавить
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Фильтр красивый -->
    <div class="filter-section">
      <div class="filter-wrapper">
        <i class="bi bi-search"></i>
        <input v-model="filterName" placeholder="Поиск категории..." class="filter-input" />
      </div>
      <div class="result-count" v-if="filteredCategories.length > 0">
        Найдено: <strong>{{ filteredCategories.length }}</strong> {{ pluralize(filteredCategories.length) }}
      </div>
    </div>

    <!-- Сетка карточек красивая -->
    <div class="cards-grid">
      <div v-for="(c, index) in filteredCategories" :key="c.id" class="category-card"
        :style="{ '--delay': index * 0.05 + 's' }">
        <div class="card-header">
          <div class="card-icon">👚</div>
          <!-- Кнопки редактирования/удаления только для админа -->
          <div class="card-actions" v-if="isAdmin">
            <button class="btn-icon edit" @click="onEditClick(c)" data-bs-toggle="modal"
              data-bs-target="#editCategoryModal" title="Редактировать">
              <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn-icon delete" @click="onRemoveClick(c)" title="Удалить">
              <i class="bi bi-trash3"></i>
            </button>
          </div>
        </div>

        <h4 class="card-title">{{ c.name }}</h4>

        <!-- ID показываем только администратору -->
        <div class="card-footer" v-if="isAdmin">
          <div class="card-meta">
            ID: <span>{{ c.id }}</span>
          </div>
        </div>
      </div>

      <!-- Пустое состояние -->
      <div v-if="filteredCategories.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p class="empty-text">Категории не найдены</p>
        <p class="empty-subtext">Добавьте первую категорию, чтобы начать!</p>
      </div>
    </div>


    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editCategoryModal" tabindex="-1">
      <div class="modal-dialog modal-elegant">
        <div class="modal-content modal-elegant-content">
          <div class="modal-header modal-elegant-header">
            <h5 class="modal-title">
              <i class="bi bi-pencil-square"></i> Редактировать категорию
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">Название категории</label>
              <input v-model="toEdit.name" placeholder="Введите название..." class="input-elegant" />
            </div>
          </div>
          <div class="modal-footer modal-elegant-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отменить</button>
            <button class="btn btn-primary btn-elegant" @click="onUpdate" data-bs-dismiss="modal">
              <i class="bi bi-check-circle"></i> Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно удаления -->
    <div class="modal fade" id="deleteCategoryModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content modal-elegant-content">
          <div class="modal-header modal-elegant-header delete-header">
            <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill"></i> Подтверждение удаления</h5>
            <button type="button" class="btn-close btn-close-white" @click="hideDeleteModal"></button>
          </div>
          <div class="modal-body delete-modal-body">
            <div class="delete-icon">🗑️</div>
            <p class="delete-confirm-text">Вы уверены, что хотите удалить категорию?</p>
            <p class="delete-category-name">"{{ categoryToDelete.name }}"</p>
          </div>
          <div class="modal-footer modal-elegant-footer delete-footer">
            <button class="btn btn-secondary" @click="hideDeleteModal">Отмена</button>
            <button class="btn btn-danger" @click="confirmDelete">
              <i class="bi bi-trash3"></i> Удалить категорию
            </button>
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

const categories = ref([])
const categoryStats = ref({})
const toAdd = reactive({ name: '' })
const toEdit = reactive({ id: null, name: '' })
const categoryToDelete = reactive({ id: null, name: '' })
const filterName = ref('')
const user = ref(null)
const isAdmin = computed(() => user.value?.is_superuser)

// Notification
const notification = reactive({
  visible: false,
  message: '',
  type: 'success',
  _timeoutId: null
})

function showNotification(msg, type = "success", duration = 2000) {
  if (notification._timeoutId) {
    clearTimeout(notification._timeoutId)
    notification._timeoutId = null
  }
  notification.message = msg
  notification.type = type
  notification.visible = true

  notification._timeoutId = setTimeout(() => {
    notification.visible = false
    notification._timeoutId = null
  }, duration)
}

function handleApiError(err, fallbackMessage = 'Ошибка') {
  console.error(err)
  const msg = err?.response?.data?.detail || err?.message || fallbackMessage
  showNotification(msg, 'danger')
}

function pluralize(count) {
  if (count % 10 === 1 && count % 100 !== 11) return 'категория'
  if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return 'категории'
  return 'категорий'
}

const filteredCategories = computed(() => {
  return categories.value.filter(c =>
    c.name.toLowerCase().includes(filterName.value.toLowerCase())
  )
})

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
    categories.value = (await axios.get('/categories/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить категории')
  }
}

async function fetchCategoryStats() {
  try {
    categoryStats.value = (await axios.get('/categories/stats/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику')
  }
}

async function onAdd() {
  try {
    await axios.post('/categories/', { ...toAdd })
    toAdd.name = ''
    await Promise.all([fetchAll(), fetchCategoryStats()])
    showNotification('✨ Категория добавлена успешно!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении категории')
  }
}

function onRemoveClick(c) {
  categoryToDelete.id = c.id
  categoryToDelete.name = c.name
  const modal = new bootstrap.Modal(document.getElementById('deleteCategoryModal'))
  modal.show()
}

async function confirmDelete() {
  try {
    await axios.delete(`/categories/${categoryToDelete.id}/`)
    await Promise.all([fetchAll(), fetchCategoryStats()])
    hideDeleteModal()
    showNotification('🗑️ Категория удалена', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении категории')
  }
}

function onEditClick(c) {
  toEdit.id = c.id
  toEdit.name = c.name
}

async function onUpdate() {
  try {
    await axios.put(`/categories/${toEdit.id}/`, { name: toEdit.name })
    await Promise.all([fetchAll(), fetchCategoryStats()])
    showNotification('💾 Изменения сохранены!', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении категории')
  }
}

async function exportExcel() {
  try {
    const res = await axios.get('/categories/export/?type=excel', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Categories.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('📊 Excel файл скачан!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании файла')
  }
}

async function exportWord() {
  try {
    const res = await axios.get('/categories/export/?type=word', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Categories.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('📄 Word файл скачан!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании файла')
  }
}

function hideDeleteModal() {
  const modalEl = document.getElementById('deleteCategoryModal')
  const modalInstance = bootstrap.Modal.getInstance(modalEl)
  if (modalInstance) modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

onMounted(async () => {
  await fetchUser()
  await Promise.all([fetchAll(), fetchCategoryStats()])
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.categories-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f0ff 0%, #fff5f8 100%);
  padding: 40px 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  border-radius: 25px;
}

/* ============ ЗАГОЛОВОК ============ */
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
  background: linear-gradient(135deg, #ff1493, #ff69b4, #ffb6c1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 10px 0;
  letter-spacing: -1px;
}

.header-subtitle {
  font-size: 1.2rem;
  color: #666;
  margin: 0;
  font-weight: 300;
}

/* ============ СТАТИСТИКА ============ */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
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
  box-shadow: 0 10px 40px rgba(255, 20, 147, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.stat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 50px rgba(255, 20, 147, 0.15);
  border-color: #ffb6c1;
}

.stat-count {
  border-left: 5px solid #ff1493;
}

.stat-popular {
  border-left: 5px solid #ffd700;
}

.stat-action {
  border-left: 5px solid #00bcd4;
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
  color: #ff1493;
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

/* ============ ФОРМА ДОБАВЛЕНИЯ ============ */
.add-section {
  margin-bottom: 50px;
  animation: slideUp 0.6s ease 0.2s both;
}

.add-card {
  background: white;
  border-radius: 25px;
  padding: 30px;
  box-shadow: 0 10px 40px rgba(255, 20, 147, 0.1);
  border: 2px solid #fff0f5;
  transition: all 0.3s ease;
}

.add-card:hover {
  box-shadow: 0 15px 60px rgba(255, 20, 147, 0.15);
  border-color: #ffb6c1;
}

.add-title {
  margin: 0 0 20px 0;
  color: #ff1493;
  font-size: 1.5rem;
  font-weight: 700;
}

.add-form {
  display: flex;
  gap: 10px;
}

.form-group {
  display: flex;
  gap: 10px;
  width: 100%;
}

.input-elegant {
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  font-size: 1rem;
  font-family: inherit;
  background: linear-gradient(135deg, #fff5f8, #f5f0ff);
  transition: all 0.3s ease;
}

.input-elegant:focus {
  outline: none;
  border-color: #ff1493;
  background: white;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.2);
}

.btn-add-elegant {
  padding: 14px 28px;
  background: linear-gradient(135deg, #ff1493, #ff69b4);
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
  box-shadow: 0 10px 30px rgba(255, 20, 147, 0.3);
}

.btn-add-elegant:active {
  transform: translateY(0);
}

/* ============ ФИЛЬТР ============ */
.filter-section {
  margin-bottom: 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
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
  color: #ff69b4;
  font-size: 1.2rem;
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
  border-color: #ff1493;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.2);
}

.result-count {
  color: #666;
  font-weight: 600;
  padding: 8px 16px;
  background: #fff0f5;
  border-radius: 20px;
}

.result-count strong {
  color: #ff1493;
}

/* ============ СЕТКА КАРТОЧЕК ============ */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  animation: slideUp 0.6s ease 0.4s both;
}

.category-card {
  background: white;
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 10px 30px rgba(255, 20, 147, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  animation: cardAppear 0.5s ease forwards;
  animation-delay: var(--delay);
}

@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.category-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 50px rgba(255, 20, 147, 0.15);
  border-color: #ffb6c1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.card-icon {
  font-size: 2.5rem;
}

.card-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.category-card:hover .card-actions {
  opacity: 1;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.btn-icon.edit {
  background: linear-gradient(135deg, #ff69b4, #ff1493);
}

.btn-icon.delete {
  background: linear-gradient(135deg, #dc3545, #c82333);
}

.btn-icon:hover {
  transform: scale(1.1) rotate(-5deg);
}

.card-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #ff1493;
  margin: 0 0 15px 0;
  word-break: break-word;
}

.card-footer {
  margin-top: auto;
  padding-top: 15px;
  border-top: 2px solid #f5f5f5;
}

.card-meta {
  font-size: 0.85rem;
  color: #999;
}

.card-meta span {
  color: #ff1493;
  font-weight: 700;
}

/* ============ ПУСТОЕ СОСТОЯНИЕ ============ */
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
  margin: 0 0 10px 0;
  font-weight: 700;
}

.empty-subtext {
  font-size: 1rem;
  color: #999;
  margin: 0;
}

/* ============ МОДАЛЬНОЕ ОКНО РЕДАКТИРОВАНИЯ ============ */
.modal-elegant-content {
  border: none;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-elegant-header {
  background: linear-gradient(135deg, #ff1493, #ff69b4);
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

.btn-close {
  filter: brightness(0) invert(1);
}

.btn-close-white {
  filter: brightness(0) invert(1);
}

.modal-body {
  padding: 30px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #ff1493;
  font-weight: 700;
  font-size: 0.95rem;
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
  background: linear-gradient(135deg, #ff1493, #ff69b4) !important;
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
  box-shadow: 0 10px 30px rgba(255, 20, 147, 0.3) !important;
}

/* ============ МОДАЛЬНОЕ ОКНО УДАЛЕНИЯ ============ */
.modal-elegant-header.delete-header {
  background: linear-gradient(135deg, #dc3545, #c82333);
}

.delete-modal-body {
  padding: 30px;
  text-align: center;
  background: linear-gradient(135deg, #fff5f5, #ffe6e6);
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

.delete-confirm-text {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 10px;
  line-height: 1.6;
  text-align: center;
}

.delete-category-name {
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

.delete-footer {
  justify-content: center;
  gap: 15px;
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

/* ============ NOTIFICATION ============ */
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

/* ============ АДАПТИВ ============ */
@media (max-width: 768px) {
  .categories-page {
    padding: 20px 15px;
  }

  .page-title {
    font-size: 2.5rem;
  }

  .header-icon {
    font-size: 3rem;
  }

  .stats-container {
    grid-template-columns: 1fr;
    margin-bottom: 30px;
  }

  .cards-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .add-form {
    flex-direction: column;
  }

  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-wrapper {
    min-width: unset;
  }

  .result-count {
    text-align: center;
  }
}
</style>