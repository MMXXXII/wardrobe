<template>
  <div v-if="isAdmin" class="customers-page">
    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Красивый заголовок -->
    <div class="header-section">
      <div class="header-content">
        <div class="header-icon">👥</div>
        <h1 class="page-title">Покупатели</h1>
        <p class="header-subtitle">Управляй своей клиентской базой</p>
      </div>
    </div>

    <!-- Статистика -->
    <div class="stats-container">
      <div class="stat-item stat-count">
        <div class="stat-icon">🛍️</div>
        <div class="stat-info">
          <div class="stat-label">Всего покупателей</div>
          <div class="stat-value">{{ customerStats?.count || 0 }}</div>
        </div>
      </div>
      <div class="stat-item stat-admin">
        <div class="stat-icon">👑</div>
        <div class="stat-info">
          <div class="stat-label">Администраторов</div>
          <div class="stat-value">{{ customerStats?.count_admins || 0 }}</div>
        </div>
      </div>
      <div class="stat-item stat-users">
        <div class="stat-icon">👤</div>
        <div class="stat-info">
          <div class="stat-label">Обычных пользователей</div>
          <div class="stat-value">{{ customerStats?.count_users || 0 }}</div>
        </div>
      </div>
      <div class="stat-item stat-action">
        <div class="stat-icon">📥</div>
        <div class="stat-info">
          <div class="stat-label">Экспорт</div>
          <div class="export-quick-buttons">
            <button class="btn-quick-export excel" @click="exportCustomersExcel" title="Excel">
              <i class="bi bi-file-earmark-spreadsheet-fill"></i>
            </button>
            <button class="btn-quick-export word" @click="exportCustomersWord" title="Word">
              <i class="bi bi-file-earmark-word-fill"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Фильтр и сортировка -->
    <div class="filter-and-sort">
      <div class="search-wrapper">
        <i class="bi bi-search"></i>
        <input v-model="searchQuery" placeholder="Поиск покупателей..." class="search-input" @input="filterCustomers" />
      </div>
      <select v-model="sortOrder" @change="sortCustomers" class="sort-select">
        <option value="asc">От A до Я</option>
        <option value="desc">От Я до A</option>
        <option value="admin_first">Администраторы первыми</option>
        <option value="user_first">Пользователи первыми</option>
      </select>
      <button class="btn-add-elegant" @click="showAddModal">
        <i class="bi bi-plus-circle"></i> Добавить
      </button>
    </div>

    <!-- Массовое удаление -->
    <div v-if="selectedCustomers.length" class="bulk-actions">
      <div class="bulk-info">
        Выбрано: <strong>{{ selectedCustomers.length }}</strong>
      </div>
      <button class="btn-bulk-delete" @click="showDeleteSelectedModal">
        <i class="bi bi-trash3"></i> Удалить выбранные
      </button>
    </div>

    <!-- Список покупателей -->
    <div class="customers-list">
      <div v-if="filteredCustomers.length === 0" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p class="empty-text">Покупатели не найдены</p>
      </div>
      <div v-for="(c, index) in filteredCustomers" :key="c.id" class="customer-item"
        :class="{ 'selected': selectedCustomers.includes(c.id) }" :style="{ '--delay': index * 0.05 + 's' }"
        @click="toggleSelection(c.id)">
        <div class="customer-checkbox">
          <input type="checkbox" :checked="selectedCustomers.includes(c.id)" @click.stop="toggleSelection(c.id)" />
        </div>
        <div class="customer-info">
          <div class="customer-name">
            {{ c.username }}
            <span v-if="c.is_superuser" class="badge-admin">
              <i class="bi bi-shield-check"></i> Администратор
            </span>
            <span v-else class="badge-user">
              <i class="bi bi-person"></i> Пользователь
            </span>
          </div>
          <div class="customer-meta">
            <span v-if="c.email">{{ c.email }}</span>
            <span v-if="c.age" class="meta-age">{{ c.age }} лет</span>
          </div>
        </div>
        <div class="customer-actions" @click.stop>
          <button class="btn-action edit" @click="onEditClick(c)" title="Редактировать">
            <i class="bi bi-pencil-square"></i>
          </button>
          <button class="btn-action delete" @click="onRemoveClick(c)" title="Удалить">
            <i class="bi bi-trash3"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Модалки -->
    <!-- ... (ВАШИ МОДАЛКИ ОСТАЮТСЯ БЕЗ ИЗМЕНЕНИЯ) ... -->
  </div>
  <div v-else class="customers-page-empty">
    <div class="header-section">
      <div class="header-content">
        <div class="header-icon">🙅‍♂️</div>
        <h1 class="page-title">Нет доступа</h1>
        <p class="header-subtitle">Эта страница доступна только администраторам</p>
      </div>
    </div>
  </div>
  <!-- Delete Customer Modal -->
  <div class="modal fade" id="deleteCustomerModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content modal-elegant-content">
        <div class="modal-header modal-elegant-header delete-header">
          <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill"></i> Подтверждение удаления</h5>
          <button type="button" class="btn-close btn-close-white" @click="hideDeleteModal"></button>
        </div>
        <div class="modal-body delete-modal-body">
          <div class="delete-icon">🗑️</div>
          <p class="delete-confirm-text">Вы уверены, что хотите удалить покупателя?</p>
          <p class="delete-customer-name">"{{ customerToDelete.username }}"</p>
        </div>
        <div class="modal-footer modal-elegant-footer delete-footer">
          <button class="btn btn-secondary" @click="hideDeleteModal">Отмена</button>
          <button class="btn btn-danger" @click="confirmDelete">
            <i class="bi bi-trash3"></i> Удалить покупателя
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete Selected Customers Modal -->
  <div class="modal fade" id="deleteSelectedModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content modal-elegant-content">
        <div class="modal-header modal-elegant-header delete-header">
          <h5 class="modal-title"><i class="bi bi-exclamation-triangle-fill"></i> Подтверждение удаления</h5>
          <button type="button" class="btn-close btn-close-white" @click="hideDeleteSelectedModal"></button>
        </div>
        <div class="modal-body delete-modal-body">
          <div class="delete-icon">🗑️</div>
          <p class="delete-confirm-text">Вы уверены, что хотите удалить выбранных покупателей?</p>
          <p class="delete-customer-count">Будет удалено: <strong>{{ selectedCustomers.length }}</strong> {{ pluralizeCustomers(selectedCustomers.length) }}</p>
        </div>
        <div class="modal-footer modal-elegant-footer delete-footer">
          <button class="btn btn-secondary" @click="hideDeleteSelectedModal">Отмена</button>
          <button class="btn btn-danger" @click="confirmDeleteSelected">
            <i class="bi bi-trash3"></i> Удалить выбранных
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Add Customer Modal -->
  <div class="modal fade" id="addCustomerModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content modal-elegant-content">
        <div class="modal-header modal-elegant-header">
          <h5 class="modal-title">Добавить покупателя</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Закрыть"></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Имя пользователя</label>
            <input v-model="customerToAdd.username" class="input-elegant" type="text" />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="customerToAdd.email" class="input-elegant" type="email" />
          </div>
          <div class="form-group">
            <label class="form-label">Пароль</label>
            <input v-model="customerToAdd.password" class="input-elegant" type="password" />
          </div>
          <div class="form-group">
            <label class="form-label">Возраст</label>
            <input v-model="customerToAdd.age" class="input-elegant" type="number" />
          </div>
          <div class="form-check">
            <input v-model="customerToAdd.is_superuser" type="checkbox" class="form-check-input" id="isAdminCheck" />
            <label class="form-check-label" for="isAdminCheck">Администратор</label>
          </div>
        </div>
        <div class="modal-footer modal-elegant-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-elegant" @click="onAddCustomer">Добавить</button>
        </div>
      </div>
    </div>
  </div>
  <!-- Edit Customer Modal -->
  <div class="modal fade" id="editCustomerModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content modal-elegant-content">
        <div class="modal-header modal-elegant-header">
          <h5 class="modal-title">Редактировать покупателя</h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Закрыть"></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Имя пользователя</label>
            <input v-model="customerToEdit.username" class="input-elegant" type="text" />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="customerToEdit.email" class="input-elegant" type="email" />
          </div>
          <div class="form-group">
            <label class="form-label">Пароль (оставьте пустым, если не менять)</label>
            <input v-model="customerToEdit.password" class="input-elegant" type="password" />
          </div>
          <div class="form-group">
            <label class="form-label">Возраст</label>
            <input v-model="customerToEdit.age" class="input-elegant" type="number" />
          </div>
          <div class="form-check">
            <input v-model="customerToEdit.is_superuser" type="checkbox" class="form-check-input"
              id="editIsAdminCheck" />
            <label class="form-check-label" for="editIsAdminCheck">Администратор</label>
          </div>
        </div>
        <div class="modal-footer modal-elegant-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
          <button type="button" class="btn btn-elegant" @click="onUpdateCustomer">Сохранить</button>
        </div>
      </div>
    </div>
  </div>

  

  

</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import * as bootstrap from 'bootstrap'

const customers = ref([])
const filteredCustomers = ref([])
const customerStats = ref({})
const searchQuery = ref('')
const sortOrder = ref('asc')
const selectedCustomers = ref([])
const customerToAdd = reactive({ username: '', email: '', password: '', age: null, is_superuser: false })
const customerToEdit = reactive({ id: null, username: '', email: '', password: '', age: null, is_superuser: false })
const customerToDelete = reactive({ id: null, username: '' })

const user = ref(null)
const isAdmin = computed(() => user.value?.is_superuser)

let deleteSelectedModalInstance = null

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

function filterCustomers() {
  const query = (searchQuery.value || '').toLowerCase()
  filteredCustomers.value = customers.value.filter(c => {
    const name = (c.username || '').toLowerCase()
    const email = (c.email || '').toLowerCase()
    return name.includes(query) || email.includes(query)
  })
  sortCustomers()
}

function sortCustomers() {
  filteredCustomers.value.sort((a, b) => {
    if (sortOrder.value === 'admin_first') {
      if (a.is_superuser && !b.is_superuser) return -1
      if (!a.is_superuser && b.is_superuser) return 1
      return a.username.toLowerCase().localeCompare(b.username.toLowerCase())
    } else if (sortOrder.value === 'user_first') {
      if (!a.is_superuser && b.is_superuser) return -1
      if (a.is_superuser && !b.is_superuser) return 1
      return a.username.toLowerCase().localeCompare(b.username.toLowerCase())
    } else {
      const A = a.username.toLowerCase()
      const B = b.username.toLowerCase()
      return sortOrder.value === 'asc' ? A.localeCompare(B) : B.localeCompare(A)
    }
  })
}

async function fetchCustomers() {
  try {
    customers.value = (await axios.get('/customers/')).data
    filterCustomers()
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить покупателей')
  }
}

async function fetchCustomerStats() {
  try {
    customerStats.value = (await axios.get('/customers/stats/')).data
  } catch (error) {
    handleApiError(error, 'Не удалось загрузить статистику')
  }
}

function showAddModal() {
  Object.assign(customerToAdd, { username: '', email: '', password: '', age: null, is_superuser: false })
  new bootstrap.Modal(document.getElementById('addCustomerModal')).show()
}

async function onAddCustomer() {
  try {
    const payload = {
      username: customerToAdd.username,
      email: customerToAdd.email,
      password: customerToAdd.password,
      age: customerToAdd.age,
      is_superuser: customerToAdd.is_superuser
    }
    await axios.post('/customers/', payload)
    await fetchCustomers()
    await fetchCustomerStats()
    hideAddModal()
    showNotification('✨ Покупатель добавлен!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при добавлении')
  }
}

function onEditClick(c) {
  customerToEdit.id = c.id
  customerToEdit.username = c.username
  customerToEdit.email = c.email
  customerToEdit.age = c.age || null
  customerToEdit.is_superuser = c.is_superuser
  customerToEdit.password = ''
  const modalEl = document.getElementById('editCustomerModal')
  const modalInstance = new bootstrap.Modal(modalEl)
  modalInstance.show()
}

async function onUpdateCustomer() {
  try {
    const payload = {
      username: customerToEdit.username,
      email: customerToEdit.email,
      age: customerToEdit.age,
      is_superuser: customerToEdit.is_superuser
    }
    if (customerToEdit.password) {
      payload.password = customerToEdit.password
    }
    await axios.put(`/customers/${customerToEdit.id}/`, payload)
    await fetchCustomers()
    await fetchCustomerStats()
    hideEditModal()
    showNotification('💾 Изменения сохранены!', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении')
  }
}

function onRemoveClick(c) {
  customerToDelete.id = c.id
  customerToDelete.username = c.username
  const modal = new bootstrap.Modal(document.getElementById('deleteCustomerModal'))
  modal.show()
}

async function confirmDelete() {
  try {
    const deletedId = customerToDelete.id
    await axios.delete(`/customers/${deletedId}/`)
    selectedCustomers.value = selectedCustomers.value.filter(id => id !== deletedId)
    await fetchCustomers()
    await fetchCustomerStats()
    hideDeleteModal()
    showNotification('🗑️ Покупатель удален', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении')
  }
}

function toggleSelection(id) {
  if (selectedCustomers.value.includes(id)) {
    selectedCustomers.value = selectedCustomers.value.filter((x) => x !== id)
  } else {
    selectedCustomers.value.push(id)
  }
}

function showDeleteSelectedModal() {
  const modalEl = document.getElementById('deleteSelectedModal')
  deleteSelectedModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl)
  deleteSelectedModalInstance.show()
}

function hideDeleteSelectedModal() {
  if (deleteSelectedModalInstance) deleteSelectedModalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

async function confirmDeleteSelected() {
  try {
    await Promise.all(selectedCustomers.value.map(id => axios.delete(`/customers/${id}/`)))
    selectedCustomers.value = []
    hideDeleteSelectedModal()
    await fetchCustomers()
    await fetchCustomerStats()
    showNotification('🗑️ Покупатели удалены', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении')
  }
}

async function exportCustomersExcel() {
  try {
    const response = await axios.get('/customers/export/?type=excel', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'customers.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('📊 Excel скачан!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании')
  }
}

async function exportCustomersWord() {
  try {
    const response = await axios.get('/customers/export/?type=word', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'customers.docx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    showNotification('📄 Word скачан!', 'success')
  } catch (err) {
    handleApiError(err, 'Ошибка при скачивании')
  }
}

function hideAddModal() {
  const modalEl = document.getElementById('addCustomerModal')
  const modalInstance = bootstrap.Modal.getInstance(modalEl)
  if (modalInstance) modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

function hideEditModal() {
  const modalEl = document.getElementById('editCustomerModal')
  const modalInstance = bootstrap.Modal.getInstance(modalEl)
  if (modalInstance) modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

function hideDeleteModal() {
  const modalEl = document.getElementById('deleteCustomerModal')
  const modalInstance = bootstrap.Modal.getInstance(modalEl)
  if (modalInstance) modalInstance.hide()
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove())
}

function pluralizeCustomers(count) {
  if (count % 10 === 1 && count % 100 !== 11) return 'покупатель'
  if (count % 10 >= 2 && count % 10 <= 4 && (count % 100 < 10 || count % 100 >= 20)) return 'покупателя'
  return 'покупателей'
}

onMounted(() => {
  axios.get('/userprofile/info/')
    .then(r => user.value = r.data)
    .then(() => {
      if (isAdmin.value) {
        fetchCustomers()
        fetchCustomerStats()
      }
    })
})

</script>


<style scoped>
* {
  box-sizing: border-box;
}

.customers-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f0ff 0%, #fff5f8 100%);
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
  background: linear-gradient(135deg, #ff1493, #ff69b4, #ffb6c1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 10px 0;
  border-radius: 25px;
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

.stat-admin {
  border-left: 5px solid #ffd700;
}

.stat-users {
  border-left: 5px solid #00bcd4;
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

.filter-and-sort {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  animation: slideUp 0.6s ease 0.2s both;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
  position: relative;
  display: flex;
  align-items: center;
}

.search-wrapper i {
  position: absolute;
  left: 15px;
  color: #ff69b4;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 14px 20px 14px 45px;
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  font-size: 1rem;
  background: white;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #ff1493;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.2);
}

.sort-select {
  padding: 14px 20px;
  border: 2px solid #f0f0f0;
  border-radius: 15px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 220px;
}

.sort-select:focus {
  outline: none;
  border-color: #ff1493;
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

.bulk-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  background: linear-gradient(135deg, #fff5f8, #f5f0ff);
  padding: 20px;
  border-radius: 15px;
  margin-bottom: 30px;
  border-left: 5px solid #ff1493;
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
  0%, 100% { transform: translateX(0) rotate(0deg); }
  25% { transform: translateX(-5px) rotate(-2deg); }
  75% { transform: translateX(5px) rotate(2deg); }
}

.delete-confirm-text {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 10px;
  line-height: 1.6;
  text-align: center;
}

.delete-customer-name {
  font-size: 1.3rem;
  color: #dc3545;
  font-weight: 700;
  margin-bottom: 15px;
  text-align: center;
  word-break: break-word;
}

.delete-customer-count {
  font-size: 1.1rem;
  color: #dc3545;
  font-weight: 700;
  margin-bottom: 15px;
  text-align: center;
}

.delete-customer-count strong {
  color: #c82333;
  font-size: 1.3rem;
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

.bulk-info {
  font-weight: 600;
  color: #333;
}

.bulk-info strong {
  color: #ff1493;
}

.btn-bulk-delete {
  padding: 12px 24px;
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: none;
  border-radius: 15px;
  cursor: pointer;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.btn-bulk-delete:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(220, 53, 69, 0.3);
}

.customers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  animation: slideUp 0.6s ease 0.3s both;
}

.empty-state {
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

.customer-item {
  background: white;
  border-radius: 15px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 8px 25px rgba(255, 20, 147, 0.05);
  transition: all 0.3s ease;
  border: 2px solid transparent;
  animation: itemAppear 0.5s ease forwards;
  animation-delay: var(--delay);
}

@keyframes itemAppear {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.customer-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(255, 20, 147, 0.12);
  border-color: #ffb6c1;
}

.customer-item.selected {
  background: linear-gradient(135deg, #fff5f8, #f5f0ff);
  border-color: #ff1493;
  box-shadow: 0 12px 40px rgba(255, 20, 147, 0.2);
}

.customer-checkbox {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.customer-checkbox input {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #ff1493;
}

.customer-info {
  flex: 1;
  cursor: pointer;
}

.customer-name {
  font-weight: 700;
  color: #333;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.badge-admin {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #000;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.badge-user {
  background: linear-gradient(135deg, #00bcd4, #00e5ff);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.customer-meta {
  font-size: 0.9rem;
  color: #666;
  margin-top: 4px;
  display: flex;
  gap: 15px;
}

.meta-age {
  color: #ff69b4;
  font-weight: 600;
}

.customer-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  width: 40px;
  height: 40px;
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
  background: linear-gradient(135deg, #ff69b4, #ff1493);
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

.modal-body {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 10px;
  color: #ff1493;
  font-weight: 700;
  font-size: 0.95rem;
}

.input-elegant {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #f0f0f0;
  border-radius: 12px;
  font-size: 1rem;
  background: linear-gradient(135deg, #fff5f8, #f5f0ff);
  transition: all 0.3s ease;
  font-family: inherit;
}

.input-elegant:focus {
  outline: none;
  border-color: #ff1493;
  box-shadow: 0 0 15px rgba(255, 20, 147, 0.2);
  background: white;
}

.form-check {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
}

.form-check-input {
  width: 20px;
  height: 20px;
  cursor: pointer;
  accent-color: #ff1493;
}

.form-check-label {
  cursor: pointer;
  color: #333;
  font-weight: 600;
  margin: 0;
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
}

.btn-elegant:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 30px rgba(255, 20, 147, 0.3) !important;
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
  .customers-page {
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

  .filter-and-sort {
    flex-direction: column;
  }

  .search-wrapper,
  .sort-select,
  .btn-add-elegant {
    width: 100%;
  }

  .customer-item {
    flex-wrap: wrap;
  }

  .customer-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>