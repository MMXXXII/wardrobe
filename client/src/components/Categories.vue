<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()

const categories = ref([])
const categoryStats = ref(null)

const addName = ref('')
const editId = ref(null)
const editName = ref('')

const filterName = ref('')
const editVisible = ref(false)

const isAdmin = computed(() => {
  return userStore.isSuperUser
})

const filteredCategories = computed(() => {
  return categories.value.filter(c =>
    c.name.toLowerCase().includes(filterName.value.toLowerCase())
  )
})

async function loadData() {
  const res = await axios.get('/categories/')
  categories.value = res.data

  const stats = await axios.get('/categories/stats/')
  categoryStats.value = stats.data
}

async function onAdd() {
  await axios.post('/categories/', {
    name: addName.value
  })

  addName.value = ''

  await loadData()

  ElMessage.success('Категория добавлена')
}

async function onRemove(c) {
  await axios.delete(`/categories/${c.id}/`)

  await loadData()

  ElMessage.success('Категория удалена')
}

function openEdit(c) {
  editId.value = c.id
  editName.value = c.name
  editVisible.value = true
}

async function saveForm() {
  await axios.put(`/categories/${editId.value}/`, {
    name: editName.value
  })

  editVisible.value = false

  await loadData()

  ElMessage.success('Категория обновлена')
}

async function exportExcel() {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  const response = await axios.get('/categories/export/?type=excel', {
    responseType: 'blob'
  })

  const blob = response.data
  const link = document.createElement('a')

  link.href = URL.createObjectURL(blob)
  link.download = 'Categories.xlsx'
  link.click()
}

onMounted(async () => {
  await loadData()
})
</script>

<template>
  <div>
    <h1>Категории</h1>

    <div v-if="categoryStats">
      Всего категорий: {{ categoryStats.count || 0 }}
    </div>

    <div v-if="isAdmin">
      <el-button type="primary" @click="exportExcel">
        Экспорт в Excel
      </el-button>
    </div>

    <div v-if="isAdmin">
      <h3>Добавить категорию</h3>

      <el-input v-model="addName" placeholder="Название категории" />

      <el-button type="primary" @click="onAdd">
        Добавить
      </el-button>
    </div>

    <el-input v-model="filterName" placeholder="Поиск" />

    <el-table :data="filteredCategories">
      <el-table-column prop="id" label="ID" v-if="isAdmin" />
      <el-table-column prop="name" label="Название" />

      <el-table-column v-if="isAdmin" label="Действия" #default="{ row }">
        <el-button size="small" @click="openEdit(row)">
          Изменить
        </el-button>
        <el-button size="small" type="danger" @click="onRemove(row)">
          Удалить
        </el-button>
      </el-table-column>
    </el-table>


    <el-dialog v-model="editVisible" title="Редактировать">
      <el-input v-model="editName" />

      <el-button @click="editVisible = false">
        Отмена
      </el-button>

      <el-button type="primary" @click="saveForm">
        Сохранить
      </el-button>
    </el-dialog>
  </div>
</template>
