<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const customers = ref([])
const filteredCustomers = ref([])
const customerStats = ref(null)
const searchQuery = ref('')
const customerToAdd = reactive({ username: '', email: '', password: '', age: null, is_superuser: false })
const customerToEdit = reactive({ id: null, username: '', email: '', password: '', age: null, is_superuser: false })
const user = ref(null)
const addVisible = ref(false)
const editVisible = ref(false)

const isAdmin = computed(() => user.value?.is_superuser)

function filterCustomers() {
  const query = searchQuery.value.toLowerCase()
  filteredCustomers.value = customers.value.filter(c =>
    c.username.toLowerCase().includes(query) || c.email.toLowerCase().includes(query)
  )
}

async function fetchUser() {
  try {
    user.value = (await axios.get('/userprofile/info/')).data
  } catch {
    ElMessage.error('Ошибка загрузки пользователя')
  }
}

async function fetchCustomers() {
  try {
    customers.value = (await axios.get('/customers/')).data
    filterCustomers()
  } catch {
    ElMessage.error('Ошибка загрузки покупателей')
  }
}

async function fetchStats() {
  try {
    customerStats.value = (await axios.get('/customers/stats/')).data
  } catch {
    ElMessage.error('Ошибка загрузки статистики')
  }
}

function showAddModal() {
  Object.assign(customerToAdd, { username: '', email: '', password: '', age: null, is_superuser: false })
  addVisible.value = true
}

async function onAddCustomer() {
  try {
    await axios.post('/customers/', { ...customerToAdd })
    await Promise.all([fetchCustomers(), fetchStats()])
    addVisible.value = false
    ElMessage.success('Покупатель добавлен')
  } catch {
    ElMessage.error('Ошибка добавления')
  }
}

function onEditClick(c) {
  Object.assign(customerToEdit, { ...c, password: '' })
  editVisible.value = true
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
    await Promise.all([fetchCustomers(), fetchStats()])
    editVisible.value = false
    ElMessage.success('Покупатель обновлен')
  } catch {
    ElMessage.error('Ошибка обновления')
  }
}

async function onRemove(c) {
  try {
    await axios.delete(`/customers/${c.id}/`)
    await Promise.all([fetchCustomers(), fetchStats()])
    ElMessage.success('Покупатель удален')
  } catch {
    ElMessage.error('Ошибка удаления')
  }
}

onMounted(async () => {
  await fetchUser()
  if (isAdmin.value) {
    await Promise.all([fetchCustomers(), fetchStats()])
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

    <el-input v-model="searchQuery" placeholder="Поиск покупателей..." style="margin: 20px 0;" @input="filterCustomers" />
    <el-button type="primary" @click="showAddModal" style="margin-bottom: 20px;">Добавить покупателя</el-button>

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
          <el-button size="small" @click="onEditClick(row)" class="action-btn">Изменить</el-button>
          <el-button size="small" type="danger" @click="onRemove(row)" class="action-btn">Удалить</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="addVisible" title="Добавить покупателя">
      <el-form>
        <el-form-item label="Имя пользователя">
          <el-input v-model="customerToAdd.username" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="customerToAdd.email" type="email" />
        </el-form-item>
        <el-form-item label="Пароль">
          <el-input v-model="customerToAdd.password" type="password" />
        </el-form-item>
        <el-form-item label="Возраст">
          <el-input-number v-model="customerToAdd.age" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Администратор">
          <el-checkbox v-model="customerToAdd.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addVisible = false">Отмена</el-button>
        <el-button type="primary" @click="onAddCustomer">Добавить</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editVisible" title="Редактировать покупателя">
      <el-form>
        <el-form-item label="Имя пользователя">
          <el-input v-model="customerToEdit.username" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="customerToEdit.email" type="email" />
        </el-form-item>
        <el-form-item label="Пароль (оставьте пустым, если не менять)">
          <el-input v-model="customerToEdit.password" type="password" />
        </el-form-item>
        <el-form-item label="Возраст">
          <el-input-number v-model="customerToEdit.age" :min="1" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Администратор">
          <el-checkbox v-model="customerToEdit.is_superuser" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">Отмена</el-button>
        <el-button type="primary" @click="onUpdateCustomer">Сохранить</el-button>
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