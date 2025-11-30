<template>
  <div class="orders-page">
    <transition name="notif-fade">
      <div v-if="notification.visible" class="notification" :class="'notification-' + notification.type" role="status"
        aria-live="polite">
        {{ notification.message }}
      </div>
    </transition>

    <!-- Заголовок -->
    <div class="header-section">
      <div class="header-content">
        <div class="header-icon">📦</div>
        <h1 class="page-title">Заказы</h1>
        <p class="header-subtitle">Следи за статусами и управляй заказами клиентов</p>
      </div>
    </div>

    <!-- Статистика -->
    <div class="stats-container">
      <div class="stat-item stat-count">
        <div class="stat-icon">📑</div>
        <div class="stat-info">
          <div class="stat-label">Всего заказов</div>
          <div class="stat-value">{{ orderStats?.count || 0 }}</div>
        </div>
      </div>
      <div class="stat-item stat-sum">
        <div class="stat-icon">💰</div>
        <div class="stat-info">
          <div class="stat-label">Общая сумма</div>
          <div class="stat-value">{{ orderStats?.total_sum || 0 }} ₽</div>
        </div>
      </div>
      <div v-if="orderStats?.topCustomer?.name" class="stat-item stat-top-customer">
        <div class="stat-icon">🏆</div>
        <div class="stat-info">
          <div class="stat-label">Лучший клиент</div>
          <div class="stat-value-text">{{ orderStats.topCustomer.name }} ({{ orderStats.topCustomer.order_count }}
            заказов)</div>
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

    <!-- Форма добавления -->
    <div class="add-section">
      <div class="add-card">
        <h3 class="add-title">✨ Добавить новый заказ</h3>
        <form @submit.prevent="onAdd" class="add-form">
          <select v-model="toAdd.store" class="input-elegant" required>
            <option value="" disabled>Выберите магазин</option>
            <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
          <select v-model="toAdd.product" class="input-elegant" required>
            <option value="" disabled>Выберите товар</option>
            <option v-for="p in filteredProducts" :key="p.id" :value="p.id">
              {{ p.name }} ({{ p.price }} ₽)
            </option>
          </select>

          <input v-model.number="toAdd.quantity" type="number" min="1" placeholder="Количество" class="input-elegant"
            required />
          <input v-model="toAdd.order_date" type="date" class="input-elegant" required />
          <button type="submit" class="btn-add-elegant"><i class="bi bi-plus-circle"></i> Добавить заказ</button>
        </form>
      </div>
    </div>

    <!-- Фильтры -->
    <div class="filter-section">
      <select v-model="filterStatus" class="filter-select">
        <option value="">Все статусы</option>
        <option value="pending">Ожидает</option>
        <option value="sold">Продано</option>
        <option value="returned">Возвращено</option>
        <option value="cancelled">Отменено</option>
      </select>
      <input v-model="filterDate" type="date" class="filter-input" placeholder="Фильтр по дате" />
    </div>

    <!-- Сетка карточек заказов -->
    <div class="cards-grid">
      <div v-if="filteredOrders.length === 0" class="empty-state">
        <div class="empty-icon">🗂️</div>
        <p class="empty-text">Заказы не найдены</p>
      </div>
      <div v-for="o in filteredOrders" :key="o.id" class="order-card">
        <div class="order-header">
          <h4>Заказ #{{ o.id }}</h4>
          <span class="badge" :class="getStatusClass(o.status)">{{ getStatusText(o.status) }}</span>
        </div>
        <div class="order-content">
          <div class="order-row"><span class="order-label">Товар:</span> {{ o.product_name }}</div>
          <div class="order-row"><span class="order-label">Покупатель:</span> {{ o.customer_name }}</div>
          <div class="order-row"><span class="order-label">Количество:</span> {{ o.quantity }} шт</div>
          <div class="order-row order-price"><span class="order-label">Сумма:</span> {{ o.total_price }} ₽</div>
          <div class="order-row text-muted small">Дата заказа: {{ o.order_date }}</div>
          <div class="order-row text-muted small" v-if="o.delivery_date">Дата доставки: {{ o.delivery_date }}</div>
        </div>
        <div class="card-buttons">
          <button v-if="o.status === 'pending'" class="btn-action complete" @click="onComplete(o)">
            <i class="bi bi-check-circle"></i> Завершить
          </button>
          <button v-if="isAdmin" class="btn-action edit" @click="onEditClick(o)" data-bs-toggle="modal"
            data-bs-target="#editOrderModal" title="Редактировать">
            <i class="bi bi-pencil-square"></i>
          </button>
          <button v-if="isAdmin" class="btn-action delete" @click="onRemove(o)" title="Удалить">
            <i class="bi bi-trash3"></i>
          </button>
        </div>
      </div>

    </div>

    <!-- Модалка редактирования -->
    <div class="modal fade" id="editOrderModal" tabindex="-1">
      <div class="modal-dialog modal-elegant">
        <div class="modal-content modal-elegant-content">
          <div class="modal-header modal-elegant-header">
            <h5 class="modal-title"><i class="bi bi-pencil-square"></i> Редактировать заказ</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <select v-model="toEdit.product" class="input-elegant mb-2">
              <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
            <select v-model="toEdit.customer" class="input-elegant mb-2">
              <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.first_name }} {{ c.last_name || '' }}
              </option>
            </select>
            <input v-model.number="toEdit.quantity" type="number" min="1" placeholder="Количество"
              class="input-elegant mb-2" />
            <input v-model="toEdit.order_date" type="date" class="input-elegant mb-2" />
            <select v-model="toEdit.status" class="input-elegant mb-2">
              <option value="pending">Ожидает</option>
              <option value="sold">Продано</option>
              <option value="returned">Возвращено</option>
              <option value="cancelled">Отменено</option>
            </select>
          </div>
          <div class="modal-footer modal-elegant-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
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

const orders = ref([])
const products = ref([])
const customers = ref([])
const orderStats = ref({})
const stores = ref([])
const toAdd = reactive({ store: '', product: '', customer: '', quantity: 1, order_date: '' })
const toEdit = reactive({ id: null, product: '', customer: '', quantity: 1, order_date: '', status: 'pending' })
const filterStatus = ref('')
const filterDate = ref('')
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

const filteredOrders = computed(() =>
  orders.value.filter(o =>
    (!filterStatus.value || o.status === filterStatus.value) &&
    (!filterDate.value || o.order_date === filterDate.value)
  )
)

const filteredProducts = computed(() => {
  // Фильтруем товары по выбранному магазину, сравнивая store.id с выбранным store
  return products.value.filter(p => p.store === toAdd.store)
})




function getStatusClass(status) {
  const classes = {
    pending: 'bg-warning',
    sold: 'bg-success',
    returned: 'bg-info',
    cancelled: 'bg-danger'
  }
  return classes[status] || 'bg-secondary'
}

function getStatusText(status) {
  const texts = {
    pending: 'Ожидает',
    sold: 'Продано',
    returned: 'Возвращено',
    cancelled: 'Отменено'
  }
  return texts[status] || status
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
    const resOrders = await axios.get('/orders/')
    orders.value = resOrders.data
    const resProducts = await axios.get('/products/')
    products.value = resProducts.data
    const resStores = await axios.get('/stores/')
    stores.value = resStores.data

    // Выводим данные для отладки
    console.log('Products:', products.value);
    console.log('Stores:', stores.value);
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить данные')
  }
}



async function fetchOrderStats() {
  try {
    orderStats.value = (await axios.get('/orders/stats/')).data
  } catch (err) {
    handleApiError(err, 'Не удалось загрузить статистику')
  }
}

const onAdd = async () => {
  const product = filteredProducts.value.find(p => p.id === toAdd.product);

  // Проверка количества товара на фронтенде
  if (toAdd.quantity > product.quantity) {
    showNotification(`Недостаточно товара: доступно только ${product.quantity} единиц`, 'danger');
    return;
  }

  // Отладочная информация перед отправкой запроса
  console.log('Sending order data:', {
    store: toAdd.store,
    product: toAdd.product,
    customer: toAdd.customer,
    quantity: toAdd.quantity,
    order_date: toAdd.order_date
  });

  try {
    const res = await axios.post('/orders/', {
      store: toAdd.store,
      product: toAdd.product,
      customer: toAdd.customer,
      quantity: toAdd.quantity,
      order_date: toAdd.order_date
    });

    // Обновление данных после успешного добавления заказа
    await Promise.all([fetchAll(), fetchOrderStats()]);
    showNotification('Заказ добавлен', 'success');
  } catch (err) {
    console.error('Error response:', err?.response?.data);
    handleApiError(err, 'Ошибка при добавлении заказа');
  }
};




async function onRemove(o) {
  if (!confirm(`Удалить заказ #${o.id}?`)) return

  try {
    await axios.delete(`/orders/${o.id}/`)
    await Promise.all([fetchAll(), fetchOrderStats()])
    showNotification('Заказ удален', 'danger')
  } catch (err) {
    handleApiError(err, 'Ошибка при удалении заказа')
  }
}

function onEditClick(o) {
  Object.assign(toEdit, { ...o })
}

async function onUpdate() {
  try {
    await axios.put(`/orders/${toEdit.id}/`, {
      product: toEdit.product,
      customer: toEdit.customer,
      quantity: toEdit.quantity,
      order_date: toEdit.order_date,
      status: toEdit.status
    })
    await Promise.all([fetchAll(), fetchOrderStats()])
    showNotification('Изменения сохранены', 'warning')
  } catch (err) {
    handleApiError(err, 'Ошибка при обновлении заказа')
  }
}

async function exportExcel() {
  try {
    const res = await axios.get('/orders/export/?type=excel', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Orders.xlsx')
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
    const res = await axios.get('/orders/export/?type=word', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'Orders.docx')
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
  await Promise.all([fetchAll(), fetchOrderStats()])
})
</script>

<style scoped>
.orders-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fff5f8 0%, #f5f0ff 100%);
  padding: 40px 20px;
  font-family: 'Segoe UI', Arial, sans-serif;
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
}

.page-title {
  font-size: 3.1rem;
  font-weight: 800;
  background: linear-gradient(135deg, #ff6b9d, #d63384, #c44569, #ffb6c1);
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

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 22px;
  margin-bottom: 48px;
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
  padding: 24px 18px;
  display: flex;
  align-items: center;
  gap: 18px;
  box-shadow: 0 10px 40px rgba(255, 20, 147, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 50px rgba(255, 20, 147, 0.15);
  border-color: #ffd6e6;
}

.stat-count {
  border-left: 5px solid #d63384;
}

.stat-sum {
  border-left: 5px solid #ff6b9d;
}

.stat-top-customer {
  border-left: 5px solid #c44569;
}

.stat-action {
  border-left: 5px solid #28a745;
}

.stat-icon {
  font-size: 2.2rem;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.92rem;
  color: #999;
  text-transform: uppercase;
  font-weight: 600;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 800;
  color: #d63384;
  margin-top: 4px;
}

.stat-value-text {
  font-size: 1.07rem;
  color: #c44569;
  font-weight: 700;
  margin-top: 6px;
}

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
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
}

.btn-quick-export.excel {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.btn-quick-export.word {
  background: linear-gradient(135deg, #007bff, #0056b3);
}

.btn-quick-export:hover {
  transform: scale(1.13) rotate(8deg);
}

.add-section {
  margin-bottom: 40px;
  animation: slideUp 0.6s ease 0.2s both;
}

.add-card {
  background: white;
  border-radius: 18px;
  padding: 26px 30px;
  box-shadow: 0 10px 40px rgba(255, 20, 147, 0.09);
  border: 2px solid #fff0f5;
  transition: all 0.3s ease;
}

.add-title {
  margin: 0 0 17px 0;
  color: #d63384;
  font-size: 1.3rem;
  font-weight: 700;
}

.add-form {
  display: flex;
  gap: 14px;
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
  border-color: #d63384;
  background: #fff;
  box-shadow: 0 0 10px rgba(255, 20, 147, 0.18);
}

.btn-add-elegant {
  background: linear-gradient(135deg, #ff6b9d, #d63384);
  color: white;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  font-size: 1rem;
  padding: 14px 23px;
  cursor: pointer;
  transition: all 0.25s;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.btn-add-elegant:hover {
  transform: translateY(-1.5px);
  box-shadow: 0 8px 24px rgba(255, 20, 147, 0.19);
}

.filter-section {
  display: flex;
  gap: 14px;
  margin-bottom: 38px;
  flex-wrap: wrap;
  align-items: center;
  animation: slideUp 0.6s ease 0.3s both;
}

.filter-select,
.filter-input {
  padding: 13px 18px;
  border: 2px solid #f0f0f0;
  border-radius: 14px;
  font-size: 1rem;
  background: #fff;
  min-width: 160px;
  transition: all 0.25s;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #d63384;
  box-shadow: 0 0 10px rgba(255, 20, 147, 0.18);
}

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

  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-18px);
  }
}

.empty-text {
  font-size: 1.25rem;
  color: #444;
  margin: 0;
  font-weight: 700;
}

.order-card {
  background: white;
  border-radius: 17px;
  box-shadow: 0 9px 33px rgba(255, 20, 147, 0.08);
  border: 2px solid transparent;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  padding: 23px;
  animation: cardAppear 0.5s ease forwards;
}

@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(15px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.order-card:hover {
  border-color: #ffd6e6;
  box-shadow: 0 14px 48px rgba(255, 20, 147, 0.16);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.order-header h4 {
  color: #d63384;
  margin: 0;
  font-size: 1.14rem;
  font-weight: bold;
}

.order-content {
  margin-bottom: 13px;
}

.order-row {
  margin-bottom: 7px;
  font-size: 0.97rem;
}

.order-label {
  color: #c44569;
  font-weight: 600;
  margin-right: 4px;
}

.order-price {
  font-size: 1.08em;
  color: #ff1493;
  font-weight: bold;
}

.card-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: auto;
}

.btn-action {
  border-radius: 14px;
  padding: 8px 14px;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.23s;
  font-size: 0.96rem;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-action.complete {
  background: linear-gradient(135deg, #28a745, #20c997);
}

.btn-action.complete:hover {
  background: #218838;
}

.btn-action.edit {
  background: linear-gradient(135deg, #ff6b9d, #d63384);
}

.btn-action.edit:hover {
  background: #c44569;
}

.btn-action.delete {
  background: linear-gradient(135deg, #dc3545, #c82333);
}

.btn-action.delete:hover {
  background: #b70023;
}

.modal-elegant-content {
  border: none;
  border-radius: 18px;
  box-shadow: 0 17px 49px rgba(0, 0, 0, 0.13);
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

.modal-body {
  padding: 27px;
}

.input-elegant.mb-2 {
  margin-bottom: 10px;
}

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

.btn-elegant:hover {
  transform: translateY(-2px) !important;
}

.notification {
  position: fixed;
  top: 17px;
  left: 50%;
  transform: translateX(-50%);
  color: #fff;
  padding: 14px 22px;
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
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

.notification-success {
  background: #198754;
}

.notification-danger {
  background: #dc3545;
}

.notification-warning {
  background: #ffc107;
  color: #000;
}

/* mobile */
@media (max-width: 768px) {
  .orders-page {
    padding: 20px 8px;
  }

  .page-title {
    font-size: 2.2rem;
  }

  .header-icon {
    font-size: 2.5rem;
  }

  .stats-container {
    grid-template-columns: 1fr;
  }

  .add-card,
  .modal-elegant-content {
    padding: 14px;
  }

  .cards-grid {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .order-card {
    padding: 13px;
  }

  .add-form {
    flex-direction: column;
  }

  .filter-section {
    flex-direction: column;
  }
}
</style>
