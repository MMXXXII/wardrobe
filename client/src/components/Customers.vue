<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()
const customers = ref([])
const filteredCustomers = ref([])
const customerStats = ref(null)
const searchQuery = ref('')
const toAdd = reactive({ username: '', email: '', password: '', age: null, is_superuser: false })
const toEdit = reactive({ id: null, username: '', email: '', password: '', age: null, is_superuser: false })
const addVisible = ref(false)
const editVisible = ref(false)

const isAdmin = computed(() => userStore.isSuperUser)

function filterCustomers() {
  const query = searchQuery.value.toLowerCase()
  filteredCustomers.value = customers.value.filter(c =>
    c.username.toLowerCase().includes(query) || c.email.toLowerCase().includes(query)
  )
}

async function loadData() {
  const [customersRes, statsRes] = await Promise.all([
    axios.get('/customers/'),
    axios.get('/customers/stats/')
  ])
  customers.value = customersRes.data
  customerStats.value = statsRes.data
  filterCustomers()
}

function openAdd() {
  toAdd.username = ''
  toAdd.email = ''
  toAdd.password = ''
  toAdd.age = null
  toAdd.is_superuser = false
  addVisible.value = true
}

async function saveAdd() {
  await axios.post('/customers/', {
    username: toAdd.username,
    email: toAdd.email,
    password: toAdd.password,
    age: toAdd.age,
    is_superuser: toAdd.is_superuser
  })
  await loadData()
  addVisible.value = false
  ElMessage.success('Покупатель добавлен')
}

function openEdit(c) {
  toEdit.id = c.id
  toEdit.username = c.username
  toEdit.email = c.email
  toEdit.password = ''
  toEdit.age = c.age
  toEdit.is_superuser = c.is_superuser
  editVisible.value = true
}

async function saveForm() {
  const payload = {
    username: toEdit.username,
    email: toEdit.email,
    age: toEdit.age,
    is_superuser: toEdit.is_superuser
  }
  if (toEdit.password) {
    payload.password = toEdit.password
  }
  await axios.put(`/customers/${toEdit.id}/`, payload)
  await loadData()
  editVisible.value = false
  ElMessage.success('Покупатель обновлен')
}

async function onRemove(c) {
  await axios.delete(`/customers/${c.id}/`)
  await loadData()
  ElMessage.success('Покупатель удален')
}

async function exportFile(format) {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  const response = await axios.get(`/customers/export/?type=${format}`, { responseType: 'blob' })
  const blob = response.data
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `Customers.${format === 'excel' ? 'xlsx' : 'docx'}`
  link.click()
}

onMounted(async () => {
  if (isAdmin.value) {
    await loadData()
  }
})
</script>

<template>
  <div class="page" v-if="isAdmin">
    <el-header>
      <h1>Покупатели</h1>
    </el-header>

    <el-card v-if="customerStats">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="Всего покупателей" :value="customerStats.count || 0" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="Администраторов" :value="customerStats.count_admins || 0" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="Пользователей" :value="customerStats.count_users || 0" />
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Экспорт</h3>
      <el-button type="primary" @click="exportFile('excel')">Экспорт в Excel</el-button>
      <el-button type="primary" @click="exportFile('word')" style="margin-left: 10px;">Экспорт в Word</el-button>
    </el-card>

    <el-input v-model="searchQuery" placeholder="Поиск покупателей..." style="margin: 20px 0;" @input="filterCustomers" />
    <el-button type="primary" @click="openAdd" style="margin-bottom: 20px;">Добавить покупателя</el-button>

    <el-table :data="filteredCustomers" stripe>
      <el-table-column prop="username" label="Имя пользователя" />
      <el-table-column prop="email" label="Email" />
      <el-table-column prop="age" label="Возраст" />
      <el-table-column label="Роль">
        <template #default="{ row }">
          <el-tag v-if="row.is_superuser" type="danger">Админ</el-tag>
          <el-tag v-else>Пользователь</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Действия" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)" class="action-btn">Изменить</el-button>
          <el-button size="small" type="danger" @click="onRemove(row)" class="action-btn">Удалить</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="addVisible" title="Добавить покупателя">
      <el-form>
        <el-form-item label="Имя пользователя">
          <el-input v-model="toAdd.username" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="toAdd.email" type="email" />
        </el-form-item>
        <el-form-item label="Пароль">
          <el-input v-model="toAdd.password" type="password" />
        </el-form-item>
        <el-form-item label="Возраст">
          <el-input-number v-model="toAdd.age" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Администратор">
          <el-checkbox v-model="toAdd.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">Отмена</el-button>
        <el-button type="primary" @click="saveAdd">Добавить</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editVisible" title="Редактировать покупателя">
      <el-form>
        <el-form-item label="Имя пользователя">
          <el-input v-model="toEdit.username" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="toEdit.email" type="email" />
        </el-form-item>
        <el-form-item label="Пароль (оставьте пустым, если не менять)">
          <el-input v-model="toEdit.password" type="password" />
        </el-form-item>
        <el-form-item label="Возраст">
          <el-input-number v-model="toEdit.age" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Администратор">
          <el-checkbox v-model="toEdit.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">Отмена</el-button>
        <el-button type="primary" @click="saveForm">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
  <div v-else class="page">
    <h1>Нет доступа</h1>
    <p>Эта страница доступна только администраторам</p>
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

.action-btn {
  width: 90px;
}
</style>