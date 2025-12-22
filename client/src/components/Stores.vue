<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()

const stores = ref([])
const storeStats = ref(null)

const addName = ref('')
const addAddress = ref('')

const editId = ref(null)
const editName = ref('')
const editAddress = ref('')

const filterName = ref('')
const editVisible = ref(false)

const isAdmin = computed(() => {
  return userStore.isSuperUser
})

const filteredStores = computed(() => {
  return stores.value.filter(s =>
    s.name.toLowerCase().includes(filterName.value.toLowerCase())
  )
})

async function fetchAll() {
  const res = await axios.get('/stores/')
  stores.value = res.data
}

async function fetchStats() {
  const res = await axios.get('/stores/stats/')
  storeStats.value = res.data
}

async function onAdd() {
  await axios.post('/stores/', {
    name: addName.value,
    address: addAddress.value
  })

  addName.value = ''
  addAddress.value = ''

  await fetchAll()
  await fetchStats()

  ElMessage.success('Магазин добавлен')
}

async function onRemove(s) {
  await axios.delete(`/stores/${s.id}/`)

  await fetchAll()
  await fetchStats()

  ElMessage.success('Магазин удален')
}

function onEditClick(s) {
  editId.value = s.id
  editName.value = s.name
  editAddress.value = s.address

  editVisible.value = true
}

async function onUpdate() {
  await axios.put(`/stores/${editId.value}/`, {
    name: editName.value,
    address: editAddress.value
  })

  editVisible.value = false

  await fetchAll()
  await fetchStats()

  ElMessage.success('Магазин обновлен')
}

async function exportExcel() {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  const response = await axios.get('/stores/export/?type=excel', {
    responseType: 'blob'
  })

  const blob = response.data
  const link = document.createElement('a')

  link.href = URL.createObjectURL(blob)
  link.download = 'Stores.xlsx'
  link.click()
}

onMounted(async () => {
  await userStore.fetchUserInfo()
  await fetchAll()
  await fetchStats()
})
</script>

<template>
  <div v-if="isAdmin">
    <h1>Магазины</h1>

    <div v-if="storeStats">
      Всего магазинов: {{ storeStats.count || 0 }}
    </div>

    <el-button type="primary" @click="exportExcel">
      Экспорт в Excel
    </el-button>

    <h3>Добавить магазин</h3>

    <el-input v-model="addName" placeholder="Название" />
    <el-input v-model="addAddress" placeholder="Адрес" />
    <el-button type="primary" @click="onAdd">
      Добавить
    </el-button>

    <el-input v-model="filterName" placeholder="Поиск по названию" />

    <el-table :data="filteredStores">
      <el-table-column prop="name" label="Название" />
      <el-table-column prop="address" label="Адрес" />
      <el-table-column label="Действия" v-if="isAdmin" #default="{ row }">
        <el-button size="small" @click="onEditClick(row)">
          Изменить
        </el-button>
        <el-button size="small" type="danger" @click="onRemove(row)">
          Удалить
        </el-button>
      </el-table-column>
    </el-table>


    <el-dialog v-model="editVisible" title="Редактировать">
      <el-input v-model="editName" />
      <el-input v-model="editAddress" />

      <el-button @click="editVisible = false">
        Отмена
      </el-button>
      <el-button type="primary" @click="onUpdate">
        Сохранить
      </el-button>
    </el-dialog>
  </div>

  <div v-else>
    <h1>Нет доступа</h1>
  </div>
</template>
