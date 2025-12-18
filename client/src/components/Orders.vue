<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import QRCode from 'qrcode'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()

const orders = ref([])
const products = ref([])
const stores = ref([])
const stats = ref(null)

const filterStatus = ref('')

const addForm = reactive({
  store: null,
  product: null,
  quantity: 1,
  date: ''
})

const editForm = reactive({
  id: null,
  store: null,
  product: null,
  quantity: 1,
  date: '',
  status: 'pending'
})

const editVisible = ref(false)

const showOtpDialog = ref(false)
const qrDataUrl = ref('')
const totpCode = ref('')
const totpError = ref(false)
const pendingOrder = ref(null)

const isAdmin = computed(() => userStore.isSuperUser)

const filteredOrders = computed(() =>
  orders.value.filter(o => !filterStatus.value || o.status === filterStatus.value)
)

const productsForAdd = computed(() =>
  products.value.filter(p => Number(p.store) === Number(addForm.store))
)

const productsForEdit = computed(() =>
  editForm.store
    ? products.value.filter(p => Number(p.store) === Number(editForm.store))
    : []
)

watch(() => addForm.store, () => {
  addForm.product = null
})

async function loadAll() {
  orders.value = (await axios.get('/orders/')).data
  products.value = (await axios.get('/products/')).data
  stores.value = (await axios.get('/stores/')).data
  stats.value = (await axios.get('/orders/stats/')).data
}

async function buildQr(url) {
  qrDataUrl.value = url
    ? await QRCode.toDataURL(url, { width: 220, margin: 1 })
    : ''
}

async function addOrder() {
  const product = products.value.find(p => Number(p.id) === Number(addForm.product))
  if (!product) return ElMessage.error('Товар не найден')
  if (product.quantity < addForm.quantity) {
    return ElMessage.error(`Доступно: ${product.quantity}`)
  }

  pendingOrder.value = {
    store: addForm.store,
    product: addForm.product,
    quantity: addForm.quantity,
    order_date: addForm.date
      ? new Date(addForm.date).toISOString().split('T')[0]
      : new Date().toISOString().split('T')[0]
  }

  totpCode.value = ''
  totpError.value = false
  showOtpDialog.value = true

  const url = await userStore.getTotp()
  await buildQr(url)
}

async function confirmOtp() {
  const ok = await userStore.verifyOtp(totpCode.value)
  if (!ok) {
    totpError.value = true
    totpCode.value = ''
    return
  }

  userStore.isOtpVerified = true
  await axios.post('/orders/', pendingOrder.value)

  showOtpDialog.value = false
  pendingOrder.value = null

  addForm.store = null
  addForm.product = null
  addForm.quantity = 1
  addForm.date = ''

  await loadAll()
  ElMessage.success('Заказ добавлен')
}

function openEdit(o) {
  editForm.id = o.order_id
  editForm.store = o.store
  editForm.product = o.product
  editForm.quantity = o.quantity
  editForm.date = o.order_date
  editForm.status = o.status
  editVisible.value = true
}

async function updateOrder() {
  const product = products.value.find(p => Number(p.id) === Number(editForm.product))
  if (!product) return ElMessage.error('Товар не найден')
  if (product.quantity < editForm.quantity) {
    return ElMessage.error(`Доступно: ${product.quantity}`)
  }

  await axios.put(`/orders/${editForm.id}/`, {
    store: editForm.store,
    product: editForm.product,
    quantity: editForm.quantity,
    order_date: editForm.date,
    status: editForm.status
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

onMounted(async () => {
  await userStore.fetchUserInfo()
  await loadAll()
})
</script>

<template>
  <div class="page">
    <el-card>
      <h2>Заказы</h2>
      <div class="stats">
        <div>Всего: {{ stats?.count || 0 }}</div>
        <div>Сумма: {{ stats?.total_sum || 0 }} ₽</div>
      </div>
    </el-card>

    <el-card>
      <h3>Добавить заказ</h3>
      <el-form @submit.prevent="addOrder">
        <el-select v-model="addForm.store" placeholder="Магазин" style="width:100%">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>

        <el-select
          v-model="addForm.product"
          placeholder="Товар"
          style="width:100%;margin-top:10px"
          :disabled="!addForm.store"
        >
          <el-option
            v-for="p in productsForAdd"
            :key="p.id"
            :label="`${p.name} (${p.price} ₽)`"
            :value="p.id"
          />
        </el-select>

        <el-input-number v-model="addForm.quantity" :min="1" style="margin-top:10px" />
        <el-date-picker v-model="addForm.date" type="date" style="width:100%;margin-top:10px" />

        <el-button type="primary" native-type="submit" style="margin-top:15px">
          Добавить
        </el-button>
      </el-form>
    </el-card>

    <el-select v-model="filterStatus" placeholder="Статус" style="width:200px;margin:20px 0">
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
      <el-table-column v-if="isAdmin" label="Действия">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">Изменить</el-button>
          <el-button size="small" type="danger" @click="removeOrder(row)">Удалить</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="Редактировать">
      <el-form>
        <el-select v-model="editForm.store" style="width:100%">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>

        <el-select v-model="editForm.product" style="width:100%;margin-top:10px">
          <el-option
            v-for="p in productsForEdit"
            :key="p.id"
            :label="`${p.name} (${p.price} ₽)`"
            :value="p.id"
          />
        </el-select>

        <el-input-number v-model="editForm.quantity" :min="1" style="margin-top:10px" />
        <el-date-picker v-model="editForm.date" type="date" style="width:100%;margin-top:10px" />

        <el-select v-model="editForm.status" style="width:100%;margin-top:10px">
          <el-option label="Ожидает" value="pending" />
          <el-option label="Продано" value="sold" />
          <el-option label="Возврат" value="returned" />
          <el-option label="Отменено" value="cancelled" />
        </el-select>
      </el-form>

      <template #footer>
        <el-button @click="editVisible = false">Отмена</el-button>
        <el-button type="primary" @click="updateOrder">Сохранить</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showOtpDialog" title="2FA подтверждение" width="500px">
      <div style="text-align:center">
        <img v-if="qrDataUrl" :src="qrDataUrl" style="width:220px;height:220px" />
      </div>

      <el-input v-model="totpCode" maxlength="6" placeholder="Код из приложения" />

      <div v-if="totpError" style="color:red;font-size:13px;margin-top:6px">
        Неверный код
      </div>

      <template #footer>
        <el-button @click="showOtpDialog = false">Отмена</el-button>
        <el-button type="primary" @click="confirmOtp">Подтвердить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
.stats {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}
</style>
