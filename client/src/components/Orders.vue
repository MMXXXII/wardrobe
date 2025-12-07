<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const orders = ref([])
const products = ref([])
const stores = ref([])
const orderStats = ref(null)
const toAdd = reactive({ store: '', product: '', quantity: 1, order_date: '' })
const toEdit = reactive({ order_id: null, store: '', product: '', quantity: 1, order_date: '', status: 'pending' })
const filterStatus = ref('')
const user = ref(null)
const editVisible = ref(false)

const isAdmin = computed(() => user.value?.is_superuser)

const filteredOrders = computed(() =>
  orders.value.filter(o =>
    !filterStatus.value || o.status === filterStatus.value
  )
)

const filteredProducts = computed(() => {
  return products.value.filter(p => p.store === toAdd.store)
})

const filteredProductsForEdit = computed(() => {
  if (!toEdit.store) return []
  return products.value.filter(p => p.store === toEdit.store)
})

async function fetchUser() {
  try {
    user.value = (await axios.get('/userprofile/info/')).data
  } catch {
    ElMessage.error('Ошибка загрузки пользователя')
  }
}

async function fetchAll() {
  try {
    orders.value = (await axios.get('/orders/')).data
    products.value = (await axios.get('/products/')).data
    stores.value = (await axios.get('/stores/')).data
  } catch {
    ElMessage.error('Ошибка загрузки данных')
  }
}

async function fetchStats() {
  try {
    orderStats.value = (await axios.get('/orders/stats/')).data
  } catch {
    ElMessage.error('Ошибка загрузки статистики')
  }
}

async function onAdd() {
  try {
    const product = products.value.find(p => p.id === toAdd.product);
    if (!product) {
      ElMessage.error('Товар не найден');
      return;
    }

    if (product.quantity < toAdd.quantity) {
      ElMessage.error(`Недостаточно товара. Доступно: ${product.quantity}`);
      return;
    }

    const formattedDate = toAdd.order_date ? new Date(toAdd.order_date).toLocaleDateString('en-CA') : new Date().toLocaleDateString('en-CA');

    await axios.post('/orders/', {
      store: toAdd.store,
      product: toAdd.product,
      quantity: toAdd.quantity,
      order_date: formattedDate
    });
    await Promise.all([fetchAll(), fetchStats()]);
    ElMessage.success('Заказ добавлен');
  } catch (error) {
    console.error('Ошибка при добавлении:', error.response ? error.response.data : error.message);
    ElMessage.error('Ошибка добавления');
  }
}

async function onRemove(o) {
  try {
    await axios.delete(`/orders/${o.order_id}/`)
    await Promise.all([fetchAll(), fetchStats()])
    ElMessage.success('Заказ удален')
  } catch {
    ElMessage.error('Ошибка удаления')
  }
}

function onEditClick(o) {
  Object.assign(toEdit, { ...o })
  editVisible.value = true
}

async function onUpdate() {
  try {
    const product = products.value.find(p => p.id === toEdit.product);
    if (!product) {
      ElMessage.error('Товар не найден');
      return;
    }

    if (product.quantity < toEdit.quantity) {
      ElMessage.error(`Недостаточно товара. Доступно: ${product.quantity}`);
      return;
    }

    const formattedDate = toEdit.order_date ? 
      new Date(toEdit.order_date).toISOString().split('T')[0] : 
      new Date().toISOString().split('T')[0]
    
    await axios.put(`/orders/${toEdit.order_id}/`, {
      store: toEdit.store,
      product: toEdit.product,
      quantity: toEdit.quantity,
      order_date: formattedDate,
      status: toEdit.status
    })
    await Promise.all([fetchAll(), fetchStats()])
    editVisible.value = false
    ElMessage.success('Заказ обновлен')
  } catch {
    ElMessage.error('Ошибка обновления');
  }
}

async function exportData(format) {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  try {
    const response = await axios.get(`/orders/export/?type=${format}`, { responseType: 'blob' })
    const blob = response.data
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `Orders.${format === 'excel' ? 'xlsx' : 'docx'}`
    link.click()
  } catch {
    ElMessage.error('Ошибка экспорта')
  }
}

onMounted(async () => {
  await fetchUser()
  await Promise.all([fetchAll(), fetchStats()])
})
</script>

<template>
  <div class="page">
    <el-header>
      <h1>Заказы</h1>
    </el-header>

    <el-card v-if="orderStats">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="Всего заказов" :value="orderStats.count || 0" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="Общая сумма" :value="orderStats.total_sum || 0" suffix="₽" />
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Экспорт</h3>
      <el-button type="primary" @click="exportData('excel')">Экспорт в Excel</el-button>
      <el-button type="primary" @click="exportData('word')" style="margin-left: 10px;">Экспорт в Word</el-button>
    </el-card>

    <el-card>
      <h3>Добавить заказ</h3>
      <el-form @submit.prevent="onAdd">
        <el-select v-model="toAdd.store" placeholder="Магазин" style="width: 100%; margin-bottom: 10px;">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-select v-model="toAdd.product" placeholder="Товар" style="width: 100%; margin-bottom: 10px;">
          <el-option v-for="p in filteredProducts" :key="p.id" :label="`${p.name} (${p.price} ₽)`" :value="p.id" />
        </el-select>
        <el-input-number v-model="toAdd.quantity" :min="1" placeholder="Количество" style="margin-bottom: 10px;" />
        <el-date-picker v-model="toAdd.order_date" type="date" placeholder="Дата" style="width: 100%; margin-bottom: 10px;" />
        <el-button type="primary" native-type="submit">Добавить заказ</el-button>
      </el-form>
    </el-card>

    <el-select v-model="filterStatus" placeholder="Все статусы" style="margin: 20px 0; width: 200px;">
      <el-option label="Все статусы" value="" />
      <el-option label="Ожидает" value="pending" />
      <el-option label="Продано" value="sold" />
      <el-option label="Возвращено" value="returned" />
      <el-option label="Отменено" value="cancelled" />
    </el-select>

    <el-table :data="filteredOrders" stripe>
      <el-table-column prop="product_name" label="Товар" />
      <el-table-column prop="store_name" label="Магазин" />
      <el-table-column prop="customer_name" label="Покупатель" />
      <el-table-column prop="quantity" label="Количество" />
      <el-table-column prop="total_price" label="Сумма" />
      <el-table-column prop="order_date" label="Дата" />
      <el-table-column prop="status" label="Статус">
        <template #default="{ row }">
          <el-tag v-if="row.status === 'pending'">Ожидает</el-tag>
          <el-tag v-if="row.status === 'sold'" type="success">Продано</el-tag>
          <el-tag v-if="row.status === 'returned'" type="info">Возвращено</el-tag>
          <el-tag v-if="row.status === 'cancelled'" type="danger">Отменено</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Действия" width="120" v-if="isAdmin">
        <template #default="{ row }">
          <div class="actions-column">
            <el-button size="small" @click="onEditClick(row)" class="action-btn">Изменить</el-button>
          </div>
          <div class="actions-column">
            <el-button size="small" type="danger" @click="onRemove(row)" class="action-btn">Удалить</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="Редактировать">
      <el-form>
        <el-form-item label="Магазин">
          <el-select v-model="toEdit.store" style="width: 100%;">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Товар">
          <el-select v-model="toEdit.product" style="width: 100%;">
            <el-option v-for="p in filteredProductsForEdit" :key="p.id" :label="`${p.name} (${p.price} ₽)`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Количество">
          <el-input-number v-model="toEdit.quantity" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Дата">
          <el-date-picker v-model="toEdit.order_date" type="date" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Статус">
          <el-select v-model="toEdit.status" style="width: 100%;">
            <el-option label="Ожидает" value="pending" />
            <el-option label="Продано" value="sold" />
            <el-option label="Возвращено" value="returned" />
            <el-option label="Отменено" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">Отмена</el-button>
        <el-button type="primary" @click="onUpdate">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
}

.el-card {
  margin-bottom: 20px;
}

.actions-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
  margin-bottom: 5px;
}

.action-btn {
  width: auto;
  width: 100px;
}
</style>
