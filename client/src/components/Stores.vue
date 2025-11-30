<template>
  <div class="stores-page">
    <!-- Уведомления -->
    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Заголовок -->
    <div class="header-section">
      <div class="header-content">
        <div class="header-icon">🏬</div>
        <h1 class="page-title">Магазины</h1>
        <p class="header-subtitle">Список магазинов, управление и статистика</p>
      </div>
    </div>

    <!-- Статистика -->
    <div class="stats-container">
      <div class="stat-item stat-count">
        <div class="stat-icon">📦</div>
        <div class="stat-info">
          <div class="stat-label">Всего магазинов</div>
          <div class="stat-value">{{ storeStats?.count || 0 }}</div>
        </div>
      </div>
      <div v-if="storeStats?.top" class="stat-item stat-popular">
        <div class="stat-icon">⭐</div>
        <div class="stat-info">
          <div class="stat-label">Популярный</div>
          <div class="stat-value-text">{{ storeStats.top }}</div>
        </div>
      </div>
      <div class="stat-item stat-action" v-if="isAdmin">
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

    <!-- Форма добавления (только админ) -->
    <div class="add-section" v-if="isAdmin">
      <div class="add-card">
        <h3 class="add-title">✨ Добавить магазин</h3>
        <form @submit.prevent="onAdd" class="add-form">
          <input v-model="toAdd.name" type="text" class="input-elegant" placeholder="Название магазина" required />
          <input v-model="toAdd.address" type="text" class="input-elegant" placeholder="Адрес" required />
          <button type="submit" class="btn-add-elegant">
            <i class="bi bi-plus-circle"></i> Добавить
          </button>
        </form>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filter-section">
      <input v-model="filterName" class="filter-input" placeholder="Поиск по названию" />
      <input v-model="filterAddress" class="filter-input" placeholder="Поиск по адресу" />
    </div>

    <!-- Карточки магазинов -->
    <div class="cards-grid">
      <div v-if="filteredStores.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <p class="empty-text">Магазины не найдены</p>
      </div>

      <div v-for="s in filteredStores" :key="s.id" class="store-card">
        <div class="store-main">
          <div class="store-title">{{ s.name }}</div>
          <div class="store-address">{{ s.address }}</div>
        </div>
        <div class="card-buttons" v-if="isAdmin">
          <button class="btn-action edit" @click="onEditClick(s)" data-bs-toggle="modal" data-bs-target="#editStoreModal" title="Редактировать">
            <i class="bi bi-pencil-square"></i>
          </button>
          <button class="btn-action delete" @click="onRemove(s)" title="Удалить">
            <i class="bi bi-trash3"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div class="modal fade" id="editStoreModal" tabindex="-1">
      <div class="modal-dialog modal-elegant">
        <div class="modal-content modal-elegant-content">
          <div class="modal-header modal-elegant-header">
            <h5 class="modal-title"><i class="bi bi-pencil-square"></i> Редактировать магазин</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <input v-model="toEdit.name" class="input-elegant mb-2" placeholder="Название" />
            <input v-model="toEdit.address" class="input-elegant" placeholder="Адрес" />
          </div>
          <div class="modal-footer modal-elegant-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Отменить</button>
            <button class="btn btn-primary btn-elegant" @click="onUpdate" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

const stores = ref([])
const storeStats = ref({})
const toAdd = reactive({ name: '', address: '' })
const toEdit = reactive({ id: null, name: '', address: '' })
const filterName = ref('')
const filterAddress = ref('')
const user = ref(null)
const isAdmin = computed(() => user.value?.is_superuser)

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

const filteredStores = computed(() => 
  stores.value.filter(s =>
    s.name.toLowerCase().includes(filterName.value.toLowerCase()) &&
    s.address.toLowerCase().includes(filterAddress.value.toLowerCase())
  )
)

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
    stores.value = (await axios.get('/stores/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить магазины')
  }
}

async function fetchStoreStats() {
  try {
    storeStats.value = (await axios.get('/stores/stats/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику')
  }
}

async function onAdd() {
  if (!isAdmin.value) {
    showNotification('Только администраторы могут добавлять магазины', 'danger')
    return
  }

  try {
    await axios.post('/stores/', { ...toAdd })
    toAdd.name = ''
    toAdd.address = ''
    await Promise.all([fetchAll(), fetchStoreStats()])
    showNotification('Магазин добавлен', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении магазина')
  }
}

async function onRemove(s) {
  if (!isAdmin.value) return
  if (!confirm(`Удалить магазин "${s.name}"?`)) return
  
  try {
    await axios.delete(`/stores/${s.id}/`)
    await Promise.all([fetchAll(), fetchStoreStats()])
    showNotification('Магазин удален', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении магазина')
  }
}

function onEditClick(s) {
  if (!isAdmin.value) return
  toEdit.id = s.id
  toEdit.name = s.name
  toEdit.address = s.address
}

async function onUpdate() {
  if (!isAdmin.value) return
  try {
    await axios.put(`/stores/${toEdit.id}/`, { name: toEdit.name, address: toEdit.address })
    await Promise.all([fetchAll(), fetchStoreStats()])
    showNotification('Изменения сохранены', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении магазина')
  }
}

async function exportExcel() {
  try {
    const res = await axios.get('/stores/export/?type=excel', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Stores.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('Файл сформирован, скачивание началось', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании файла')
  }
}

async function exportWord() {
  try {
    const res = await axios.get('/stores/export/?type=word', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Stores.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('Файл сформирован, скачивание началось', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании файла')
  }
}

onMounted(async () => {
  await fetchUser()
  await Promise.all([fetchAll(), fetchStoreStats()])
})
</script>

<style scoped>
.stores-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fef5f5 0%, #f5f0ff 100%);
  padding: 40px 20px;
  font-family: 'Segoe UI', Arial, sans-serif;
  border-radius: 25px;
}

/* Заголовок */
.header-section {
  text-align: center;
  margin-bottom: 50px;
  animation: slideDown 0.6s ease;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-30px); }
  to   { opacity: 1; transform: translateY(0); }
}

.header-icon {
  font-size: 4rem;
  margin-bottom: 15px;
}

.page-title {
  font-size: 3.1rem;
  font-weight: 800;
  background: linear-gradient(135deg, #ff6b9d, #d63384, #f8b500);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 10px 0;
}

.header-subtitle {
  font-size: 1.15rem;
  color: #666;
  margin: 0;
  font-weight: 300;
}

/* Статистика */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 22px;
  margin-bottom: 48px;
  animation: slideUp 0.6s ease 0.1s both;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}

.stat-item {
  background: white;
  border-radius: 20px;
  padding: 24px 18px;
  display: flex;
  align-items: center;
  gap: 18px;
  box-shadow: 0 10px 40px rgba(255, 107, 157, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}
.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 50px rgba(255, 107, 157, 0.15);
  border-color: #ffc0cb;
}

.stat-count       { border-left: 5px solid #ff6b9d; }
.stat-popular     { border-left: 5px solid #c44569; }
.stat-action      { border-left: 5px solid #28a745; }

.stat-icon { font-size: 2.2rem; }
.stat-info { flex: 1; }
.stat-label { font-size: 0.92rem; color: #999; text-transform: uppercase; font-weight: 600; }
.stat-value { font-size: 1.8rem; font-weight: 800; color: #ff6b9d; margin-top: 4px; }
.stat-value-text { font-size: 1.07rem; color: #c44569; font-weight: 700; margin-top: 6px; }

.export-quick-buttons {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}
.btn-quick-export {
  width: 33px;
  height: 33px;
  border-radius: 50%;
  border: none;
  color: white;
  background: #ff6b9d;
  transition: all 0.3s;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem;
}
.btn-quick-export.excel { background: linear-gradient(135deg, #28a745, #20c997); }
.btn-quick-export.word { background: linear-gradient(135deg, #007bff, #0056b3); }
.btn-quick-export:hover { transform: scale(1.13) rotate(8deg); }

/* Форма добавления */
.add-section { margin-bottom: 40px; animation: slideUp 0.6s ease 0.2s both; }
.add-card {
  background: white;
  border-radius: 18px;
  padding: 26px;
  box-shadow: 0 10px 40px rgba(255, 107, 157, 0.09);
  border: 2px solid #fff0f5;
  transition: all 0.3s ease;
}
.add-title { color: #ff6b9d; font-size: 1.3rem; font-weight: 700; margin-bottom: 14px; }
.add-form {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}
.input-elegant {
  flex: 1 1 180px;
  padding: 13px 18px;
  border: 2px solid #f0f0f0;
  border-radius: 14px;
  font-size: 1rem;
  background: linear-gradient(135deg, #fff5f8, #f5f0ff);
  transition: all 0.25s;
}
.input-elegant:focus {
  outline: none;
  border-color: #ff6b9d;
  background: #fff;
  box-shadow: 0 0 10px rgba(255, 107, 157, 0.18);
}
.btn-add-elegant {
  background: linear-gradient(135deg, #ff6b9d, #d63384);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  font-size: 1rem;
  padding: 13px 22px;
  cursor: pointer;
  transition: all 0.25s;
  display: flex; align-items: center; gap: 8px; white-space: nowrap;
}
.btn-add-elegant:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(255, 107, 157, 0.15);
}

/* Фильтр */
.filter-section {
  display: flex;
  gap: 14px;
  margin-bottom: 38px;
  flex-wrap: wrap;
  align-items: center;
  animation: slideUp 0.6s ease 0.3s both;
}
.filter-input {
  padding: 13px 18px;
  border: 2px solid #f0f0f0;
  border-radius: 14px;
  font-size: 1rem;
  background: #fff;
  min-width: 160px;
  transition: all 0.25s;
}
.filter-input:focus {
  outline: none;
  border-color: #ff6b9d;
  box-shadow: 0 0 10px rgba(255, 107, 157, 0.18);
}

/* Карточки магазинов */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
  animation: slideUp 0.6s ease 0.4s both;
}
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 54px 20px;
}
.empty-icon {
  font-size: 3.8rem;
  margin-bottom: 19px;
  animation: bounce 2s ease infinite;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-18px); }
}
.empty-text {
  font-size: 1.25rem;
  color: #444;
  margin: 0;
  font-weight: 700;
}
.store-card {
  background: white;
  border-radius: 17px;
  box-shadow: 0 9px 33px rgba(255, 107, 157, 0.08);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 23px;
  animation: cardAppear 0.5s ease forwards;
}
@keyframes cardAppear {
  from { opacity: 0; transform: translateY(15px); }
  to   { opacity: 1; transform: translateY(0); }
}
.store-card:hover {
  border-color: #ffc0cb;
  box-shadow: 0 14px 48px rgba(255, 107, 157, 0.16);
}
.store-main { flex: 1; }
.store-title { font-size: 1.1rem; font-weight: 700; color: #333; }
.store-address { font-size: 0.95rem; color: #888; margin-top: 7px; }

.card-buttons {
  display: flex;
  gap: 8px;
  margin-left: 15px;
}
.btn-action {
  border-radius: 14px;
  padding: 8px 14px;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.23s;
  font-size: 1.08rem;
  display: flex; align-items: center; gap: 5px;
}
.btn-action.edit { background: linear-gradient(135deg, #ff6b9d, #d63384); }
.btn-action.edit:hover { background: #c44569; }
.btn-action.delete { background: linear-gradient(135deg, #dc3545, #c82333); }
.btn-action.delete:hover { background: #b70023; }

.modal-elegant-content {
  border: none;
  border-radius: 18px;
  box-shadow: 0 17px 49px rgba(0,0,0,0.13);
}
.modal-elegant-header {
  background: linear-gradient(135deg, #ff6b9d, #d63384);
  color: white;
  border: none;
  border-radius: 18px 18px 0 0;
  padding: 24px;
}
.modal-elegant-header .modal-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1.18rem;
}
.modal-body { padding: 27px; }
.input-elegant.mb-2 { margin-bottom: 10px; }
.modal-elegant-footer {
  background: #f5f5f5;
  border-top: 2px solid #f0f0f0;
  border-radius: 0 0 18px 18px;
  padding: 18px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.btn-elegant {
  background: linear-gradient(135deg, #ff6b9d, #d63384) !important;
  border: none !important;
  color: white !important;
  font-weight: 700 !important;
  display: flex !important;
  align-items: center;
  gap: 8px;
  transition: all 0.25s ease !important;
}
.btn-elegant:hover { transform: translateY(-2px) !important; }

.notification {
  position: fixed;
  top: 17px;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  padding: 14px 22px;
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  z-index: 2000;
  font-size: 1rem;
  font-weight: 600;
  max-width: 92%;
  text-align: center;
}
.notif-fade-enter-active,
.notif-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.notif-fade-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-15px);
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
  transform: translateX(-50%) translateY(-15px);
}
.notification-success { background: #198754; }
.notification-danger  { background: #dc3545; }
.notification-warning { background: #ffc107; color: #000; }

/* mobile */
@media (max-width: 768px) {
  .stores-page { padding: 20px 8px; }
  .page-title { font-size: 2.2rem; }
  .header-icon { font-size: 2.5rem; }
  .stats-container { grid-template-columns: 1fr; }
  .add-card, .modal-elegant-content { padding: 14px; }
  .cards-grid { grid-template-columns: 1fr; gap: 18px; }
  .store-card { padding: 13px; flex-direction: column; }
  .add-form { flex-direction: column; }
  .filter-section { flex-direction: column; }
}
</style>