<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const stores = ref([])
const storeStats = ref(null)
const toAdd = reactive({ name: '', address: '' })
const toEdit = reactive({ id: null, name: '', address: '' })
const filterName = ref('')
const user = ref(null)
const editVisible = ref(false)

const isAdmin = computed(() => user.value?.is_superuser)

const filteredStores = computed(() =>
  stores.value.filter(s =>
    s.name.toLowerCase().includes(filterName.value.toLowerCase())
  )
)

async function fetchUser() {
  try {
    user.value = (await axios.get('/userprofile/info/')).data
  } catch (err) {
    ElMessage.error('Ошибка загрузки пользователя')
  }
}

async function fetchAll() {
  try {
    stores.value = (await axios.get('/stores/')).data
  } catch (err) {
    ElMessage.error('Ошибка загрузки магазинов')
  }
}

async function fetchStats() {
  try {
    storeStats.value = (await axios.get('/stores/stats/')).data
  } catch (err) {
    ElMessage.error('Ошибка загрузки статистики')
  }
}

async function onAdd() {
  try {
    await axios.post('/stores/', { ...toAdd })
    toAdd.name = ''
    toAdd.address = ''
    await Promise.all([fetchAll(), fetchStats()])
    ElMessage.success('Магазин добавлен')
  } catch (err) {
    ElMessage.error('Ошибка добавления')
  }
}

async function onRemove(s) {
  try {
    await axios.delete(`/stores/${s.id}/`)
    await Promise.all([fetchAll(), fetchStats()])
    ElMessage.success('Магазин удален')
  } catch (err) {
    ElMessage.error('Ошибка удаления')
  }
}

function onEditClick(s) {
  toEdit.id = s.id
  toEdit.name = s.name
  toEdit.address = s.address
  editVisible.value = true
}

async function onUpdate() {
  try {
    await axios.put(`/stores/${toEdit.id}/`, { name: toEdit.name, address: toEdit.address })
    await Promise.all([fetchAll(), fetchStats()])
    editVisible.value = false
    ElMessage.success('Магазин обновлен')
  } catch (err) {
    ElMessage.error('Ошибка обновления')
  }
}

// Export functionality
async function exportData(format) {
  if (!isAdmin.value) {
    ElMessage.error('Только администратор может экспортировать данные')
    return
  }

  try {
    const response = await axios.get(`/stores/export/?type=${format}`, { responseType: 'blob' })
    const blob = response.data
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `Stores.${format === 'excel' ? 'xlsx' : 'docx'}`
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
      <h1>Магазины</h1>
    </el-header>

    <el-card v-if="storeStats">
      <el-statistic title="Всего магазинов" :value="storeStats.count || 0" />
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Экспорт</h3>
      <el-button type="primary" @click="exportData('excel')">Экспорт в Excel</el-button>
      <el-button type="primary" @click="exportData('word')" style="margin-left: 10px;">Экспорт в Word</el-button>
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Добавить магазин</h3>
      <el-form @submit.prevent="onAdd">
        <el-input v-model="toAdd.name" placeholder="Название" style="margin-bottom: 10px;" />
        <el-input v-model="toAdd.address" placeholder="Адрес" style="margin-bottom: 10px;" />
        <el-button type="primary" native-type="submit">Добавить</el-button>
      </el-form>
    </el-card>

    <el-input v-model="filterName" placeholder="Поиск по названию..." style="margin: 20px 0;" />

    <el-table :data="filteredStores" stripe>
      <el-table-column prop="name" label="Название" />
      <el-table-column prop="address" label="Адрес" />
      <el-table-column label="Действия" width="150" v-if="isAdmin">
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
        <el-form-item label="Название">
          <el-input v-model="toEdit.name" />
        </el-form-item>
        <el-form-item label="Адрес">
          <el-input v-model="toEdit.address" />
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
