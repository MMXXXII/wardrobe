<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const categories = ref([])
const categoryStats = ref(null)
const toAdd = reactive({ name: '' })
const toEdit = reactive({ id: null, name: '' })
const filterName = ref('')
const user = ref(null)
const editVisible = ref(false)

const isAdmin = computed(() => user.value?.is_superuser)

const filteredCategories = computed(() => {
  return categories.value.filter(c =>
    c.name.toLowerCase().includes(filterName.value.toLowerCase())
  )
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
    categories.value = (await axios.get('/categories/')).data
  } catch {
    ElMessage.error('Ошибка загрузки категорий')
  }
}

async function fetchStats() {
  try {
    categoryStats.value = (await axios.get('/categories/stats/')).data
  } catch {
    ElMessage.error('Ошибка загрузки статистики')
  }
}

async function onAdd() {
  try {
    await axios.post('/categories/', { ...toAdd })
    toAdd.name = ''
    await Promise.all([fetchAll(), fetchStats()])
    ElMessage.success('Категория добавлена')
  } catch {
    ElMessage.error('Ошибка добавления')
  }
}

async function onRemove(c) {
  try {
    await axios.delete(`/categories/${c.id}/`)
    await Promise.all([fetchAll(), fetchStats()])
    ElMessage.success('Категория удалена')
  } catch {
    ElMessage.error('Ошибка удаления')
  }
}

function onEditClick(c) {
  toEdit.id = c.id
  toEdit.name = c.name
  editVisible.value = true
}

async function onUpdate() {
  try {
    await axios.put(`/categories/${toEdit.id}/`, { name: toEdit.name })
    await Promise.all([fetchAll(), fetchStats()])
    editVisible.value = false
    ElMessage.success('Категория обновлена')
  } catch {
    ElMessage.error('Ошибка обновления')
  }
}

async function exportData(format) {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  try {
    const response = await axios.get(`/categories/export/?type=${format}`, { responseType: 'blob' })
    const blob = response.data
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `Categories.${format === 'excel' ? 'xlsx' : 'docx'}`
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
      <h1>Категории</h1>
    </el-header>

    <el-card v-if="categoryStats">
      <el-statistic title="Всего категорий" :value="categoryStats.count || 0" />
    </el-card>

    <!-- Export buttons (only visible for admin) -->
    <el-card v-if="isAdmin">
      <h3>Экспорт</h3>
      <el-button type="primary" @click="exportData('excel')">Экспорт в Excel</el-button>
      <el-button type="primary" @click="exportData('word')" style="margin-left: 10px;">Экспорт в Word</el-button>
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Добавить категорию</h3>
      <el-form @submit.prevent="onAdd">
        <el-input v-model="toAdd.name" placeholder="Название категории" />
        <el-button type="primary" native-type="submit" style="margin-top: 10px;">Добавить</el-button>
      </el-form>
    </el-card>

    <el-input v-model="filterName" placeholder="Поиск..." style="margin: 20px 0;" />

    <el-table :data="filteredCategories" stripe>
      <el-table-column prop="id" label="ID" width="80" v-if="isAdmin" />
      <el-table-column prop="name" label="Название" />
      <el-table-column label="Действия" width="220" v-if="isAdmin">
        <template #default="{ row }">
          <el-button size="small" @click="onEditClick(row)" class="action-btn">Изменить</el-button>
          <el-button size="small" type="danger" @click="onRemove(row)" class="action-btn">Удалить</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="Редактировать">
      <el-form>
        <el-form-item label="Название">
          <el-input v-model="toEdit.name" />
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

.action-btn {
  width: 90px;
}
</style>
