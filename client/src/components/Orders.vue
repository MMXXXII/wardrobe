<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()

const orders = ref([])
const products = ref([])
const stores = ref([])
const stats = ref(null)
const filterStatus = ref('')

const addStore = ref(null)
const addProduct = ref(null)
const addQuantity = ref(1)
const addDate = ref(null)

const editVisible = ref(false)
const editId = ref(null)
const editStore = ref(null)
const editProduct = ref(null)
const editQuantity = ref(1)
const editDate = ref(null)
const editStatus = ref('pending')

const isAdmin = computed(() => userStore.isSuperUser)

const filteredOrders = computed(() =>
  orders.value.filter(o => !filterStatus.value || o.status === filterStatus.value)
)

watch(addStore, () => {
  addProduct.value = null
})

const productsForAdd = computed(() =>
  products.value.filter(p => p.store === addStore.value)
)

const productsForEdit = computed(() =>
  editStore.value
    ? products.value.filter(p => p.store === editStore.value)
    : []
)

async function loadAll() {
  orders.value = (await axios.get('/orders/')).data
  products.value = (await axios.get('/products/')).data
  stores.value = (await axios.get('/stores/')).data
  stats.value = (await axios.get('/orders/stats/')).data
}

async function addOrder() {
  if (!addStore.value || !addProduct.value) {
    ElMessage.error('Заполните магазин и товар')
    return
  }

  const product = products.value.find(p => p.id === addProduct.value)
  if (!product) {
    ElMessage.error('Товар не найден')
    return
  }

  if (product.quantity < addQuantity.value) {
    ElMessage.error(`Доступно: ${product.quantity}`)
    return
  }

  await axios.post('/orders/', {
    store: addStore.value,
    product: addProduct.value,
    quantity: addQuantity.value,
    order_date: normalizeDate(addDate.value)
  })

  addStore.value = null
  addProduct.value = null
  addQuantity.value = 1
  addDate.value = null

  await loadAll()
}


function openEdit(o) {
  editId.value = o.order_id
  editStore.value = o.store
  editProduct.value = o.product
  editQuantity.value = o.quantity
  editDate.value = o.order_date
  editStatus.value = o.status
  editVisible.value = true
}

async function updateOrder() {
  const product = products.value.find(p => p.id === editProduct.value)
  if (!product) {
    ElMessage.error('Товар не найден')
    return
  }

  if (product.quantity < editQuantity.value) {
    ElMessage.error(`Доступно: ${product.quantity}`)
    return
  }

  await axios.put(`/orders/${editId.value}/`, {
    store: editStore.value,
    product: editProduct.value,
    quantity: editQuantity.value,
    order_date: editDate.value,
    status: editStatus.value
  })

  editVisible.value = false
  await loadAll()
  ElMessage.success('Обновлено')
}

async function removeOrder(o) {
  await axios.delete(`/orders/${o.order_id}/`)
  await loadAll()
  ElMessage.success('Удалено')
}

async function exportFile() {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  const res = await axios.get('/orders/export/?type=excel', {
    responseType: 'blob'
  })

  const link = document.createElement('a')
  link.href = URL.createObjectURL(res.data)
  link.download = 'Orders.xlsx'
  link.click()
}

onMounted(async () => {
  await userStore.fetchUserInfo()
  await loadAll()
})
</script>


<template>
  <div>
    <div>
      <h2>Заказы</h2>
      <div>Всего: {{ stats?.count || 0 }}</div>
      <div>Сумма: {{ stats?.total_sum || 0 }} ₽</div>
    </div>

    <div v-if="isAdmin">
      <el-button type="primary" @click="exportFile">
        Экспорт в Excel
      </el-button>
    </div>


    <div>
      <h3>Добавить заказ</h3>
      <el-form @submit.prevent="addOrder">
        <el-select v-model="addStore" placeholder="Магазин">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>

        <el-select v-model="addProduct" placeholder="Товар" :disabled="!addStore">
          <el-option v-for="p in productsForAdd" :key="p.id" :label="`${p.name} (${p.price} ₽)`" :value="p.id" />
        </el-select>

        <el-input-number v-model="addQuantity" :min="1" />
        <el-date-picker v-model="addDate" type="date" />

        <el-button type="primary" native-type="submit">Добавить</el-button>
      </el-form>
    </div>

    <el-select v-model="filterStatus" placeholder="Статус">
      <el-option label="Все" value="" />
      <el-option label="Ожидает" value="pending" />
      <el-option label="Продано" value="sold" />
      <el-option label="Возврат" value="returned" />
      <el-option label="Отменено" value="cancelled" />
    </el-select>

    <el-table :data="filteredOrders">
      <el-table-column prop="product_name" label="Товар" />
      <el-table-column prop="store_name" label="Магазин" />
      <el-table-column prop="quantity" label="Кол-во" />
      <el-table-column prop="total_price" label="Сумма" />
      <el-table-column prop="order_date" label="Дата" />
      <el-table-column prop="status" label="Статус" />
      <el-table-column v-if="isAdmin" label="Действия" #default="{ row }">
        <el-button size="small" @click="openEdit(row)">Изменить</el-button>
        <el-button size="small" type="danger" @click="removeOrder(row)">Удалить</el-button>
      </el-table-column>
    </el-table>


    <el-dialog v-model="editVisible" title="Редактировать">
      <el-form>
        <el-select v-model="editStore">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>

        <el-select v-model="editProduct">
          <el-option v-for="p in productsForEdit" :key="p.id" :label="`${p.name} (${p.price} ₽)`" :value="p.id" />
        </el-select>

        <el-input-number v-model="editQuantity" :min="1" />
        <el-date-picker v-model="editDate" type="date" />

        <el-select v-model="editStatus">
          <el-option label="Ожидает" value="pending" />
          <el-option label="Продано" value="sold" />
          <el-option label="Возврат" value="returned" />
          <el-option label="Отменено" value="cancelled" />
        </el-select>
      </el-form>

      <el-button @click="editVisible = false">Отмена</el-button>
      <el-button type="primary" @click="updateOrder">Сохранить</el-button>
    </el-dialog>
  </div>
</template>
