<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()
const categories = ref([])
const categoryStats = ref(null)
const toAddName = ref('')
const toEditId = ref(null)
const toEditName = ref('')
const filterName = ref('')
const editVisible = ref(false)

const isAdmin = computed(() => userStore.isSuperUser)

const filteredCategories = computed(() => {
  return categories.value.filter(c =>
    c.name.toLowerCase().includes(filterName.value.toLowerCase())
  )
})

async function loadData() {
  const [categoriesRes, statsRes] = await Promise.all([
    axios.get('/categories/'),
    axios.get('/categories/stats/')
  ])
  categories.value = categoriesRes.data
  categoryStats.value = statsRes.data
}

async function onAdd() {
  await axios.post('/categories/', { name: toAddName.value })
  toAddName.value = ''
  await loadData()
  ElMessage.success('Категория добавлена')
}

async function onRemove(c) {
  await axios.delete(`/categories/${c.id}/`)
  await loadData()
  ElMessage.success('Категория удалена')
}

function openEdit(c) {
  toEditId.value = c.id
  toEditName.value = c.name
  editVisible.value = true
}

async function saveForm() {
  await axios.put(`/categories/${toEditId.value}/`, { name: toEditName.value })
  await loadData()
  editVisible.value = false
  ElMessage.success('Категория обновлена')
}

async function exportFile(format) {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  const response = await axios.get(`/categories/export/?type=${format}`, { responseType: 'blob' })
  const blob = response.data
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `Categories.${format === 'excel' ? 'xlsx' : 'docx'}`
  link.click()
}

onMounted(async () => {
  await loadData()
})
</script>

<template>
  <div class="page">
    <el-header>
      <h1>Категории</h1>
    </el-header>

    <el-card v-if="categoryStats">
      <el-statistic title="Всего категорий" :value="categoryStats.count || 0" />
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Экспорт</h3>
      <el-button type="primary" @click="exportFile('excel')">Экспорт в Excel</el-button>
      <el-button type="primary" @click="exportFile('word')" style="margin-left: 10px;">Экспорт в Word</el-button>
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Добавить категорию</h3>
      <el-form @submit.prevent="onAdd">
        <el-input v-model="toAddName" placeholder="Название категории" />
        <el-button type="primary" native-type="submit" style="margin-top: 10px;">Добавить</el-button>
      </el-form>
    </el-card>

    <el-input v-model="filterName" placeholder="Поиск..." style="margin: 20px 0;" />

    <el-table :data="filteredCategories" stripe>
      <el-table-column prop="id" label="ID" width="80" v-if="isAdmin" />
      <el-table-column prop="name" label="Название" />
      <el-table-column label="Действия" width="220" v-if="isAdmin">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)" class="action-btn">Изменить</el-button>
          <el-button size="small" type="danger" @click="onRemove(row)" class="action-btn">Удалить</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="Редактировать">
      <el-form>
        <el-form-item label="Название">
          <el-input v-model="toEditName" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">Отмена</el-button>
        <el-button type="primary" @click="saveForm">Сохранить</el-button>
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

.action-btn {
  width: 90px;
}
</style>
