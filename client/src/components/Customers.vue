<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()

const customers = ref([])
const filteredCustomers = ref([])
const customerStats = ref(null)

const searchQuery = ref('')

const toAddUsername = ref('')
const toAddEmail = ref('')
const toAddPassword = ref('')
const toAddAge = ref(null)
const toAddIsSuperuser = ref(false)

const toEditId = ref(null)
const toEditUsername = ref('')
const toEditEmail = ref('')
const toEditPassword = ref('')
const toEditAge = ref(null)
const toEditIsSuperuser = ref(false)

const addVisible = ref(false)
const editVisible = ref(false)

const isAdmin = computed(() => userStore.isSuperUser)

function filterCustomers() {
  const query = searchQuery.value.toLowerCase()

  filteredCustomers.value = customers.value.filter(c =>
    c.username.toLowerCase().includes(query) ||
    c.email.toLowerCase().includes(query)
  )
}

async function loadData() {
  const customersRes = await axios.get('/customers/')
  const statsRes = await axios.get('/customers/stats/')

  customers.value = customersRes.data
  customerStats.value = statsRes.data

  filterCustomers()
}

function openAdd() {
  toAddUsername.value = ''
  toAddEmail.value = ''
  toAddPassword.value = ''
  toAddAge.value = null
  toAddIsSuperuser.value = false

  addVisible.value = true
}

async function saveAdd() {
  await axios.post('/customers/', {
    username: toAddUsername.value,
    email: toAddEmail.value,
    password: toAddPassword.value,
    age: toAddAge.value,
    is_superuser: toAddIsSuperuser.value
  })

  await loadData()
  addVisible.value = false

  ElMessage.success('Покупатель добавлен')
}

function openEdit(c) {
  toEditId.value = c.id
  toEditUsername.value = c.username
  toEditEmail.value = c.email
  toEditPassword.value = ''
  toEditAge.value = c.age
  toEditIsSuperuser.value = c.is_superuser

  editVisible.value = true
}

async function saveForm() {
  const payload = {
    username: toEditUsername.value,
    email: toEditEmail.value,
    age: toEditAge.value,
    is_superuser: toEditIsSuperuser.value
  }

  if (toEditPassword.value) {
    payload.password = toEditPassword.value
  }

  await axios.put(`/customers/${toEditId.value}/`, payload)

  await loadData()
  editVisible.value = false

  ElMessage.success('Покупатель обновлен')
}

async function onRemove(c) {
  await axios.delete(`/customers/${c.id}/`)
  await loadData()

  ElMessage.success('Покупатель удален')
}

async function exportExcel() {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  const response = await axios.get('/customers/export/?type=excel', {
    responseType: 'blob'
  })

  const blob = response.data
  const link = document.createElement('a')

  link.href = URL.createObjectURL(blob)
  link.download = 'Customers.xlsx'
  link.click()
}

onMounted(async () => {
  if (isAdmin.value) {
    await loadData()
  }
})
</script>

<template>
  <div v-if="isAdmin">
    <h1>Покупатели</h1>

    <div v-if="customerStats">
      <div>Всего: {{ customerStats.count || 0 }}</div>
      <div>Администраторов: {{ customerStats.count_admins || 0 }}</div>
      <div>Пользователей: {{ customerStats.count_users || 0 }}</div>
    </div>

    <el-button type="primary" @click="exportExcel">
      Экспорт в Excel
    </el-button>

    <el-input v-model="searchQuery" placeholder="Поиск" @input="filterCustomers" />

    <el-button type="primary" @click="openAdd">
      Добавить покупателя
    </el-button>

    <el-table :data="filteredCustomers">
      <el-table-column prop="username" label="Имя" />
      <el-table-column prop="email" label="Email" />
      <el-table-column prop="age" label="Возраст" />
      <el-table-column prop="is_superuser" label="Админ" />
      <el-table-column label="Действия" #default="{ row }">
        <el-button size="small" @click="openEdit(row)">
          Изменить
        </el-button>
        <el-button size="small" type="danger" @click="onRemove(row)">
          Удалить
        </el-button>
      </el-table-column>
    </el-table>


    <el-dialog v-model="addVisible" title="Добавить">
      <el-input v-model="toAddUsername" placeholder="Имя" />
      <el-input v-model="toAddEmail" placeholder="Email" />
      <el-input v-model="toAddPassword" type="password" placeholder="Пароль" />
      <el-input-number v-model="toAddAge" />
      <el-checkbox v-model="toAddIsSuperuser">
        Администратор
      </el-checkbox>

      <el-button @click="addVisible = false">Отмена</el-button>
      <el-button type="primary" @click="saveAdd">Добавить</el-button>
    </el-dialog>

    <el-dialog v-model="editVisible" title="Редактировать">
      <el-input v-model="toEditUsername" />
      <el-input v-model="toEditEmail" />
      <el-input v-model="toEditPassword" type="password" />
      <el-input-number v-model="toEditAge" />
      <el-checkbox v-model="toEditIsSuperuser">
        Администратор
      </el-checkbox>

      <el-button @click="editVisible = false">Отмена</el-button>
      <el-button type="primary" @click="saveForm">Сохранить</el-button>
    </el-dialog>
  </div>

  <div v-else>
    <h1>Нет доступа</h1>
  </div>
</template>
