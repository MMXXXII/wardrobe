<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const products = ref([])
const categories = ref([])
const stores = ref([])
const productStats = ref(null)
const toAdd = reactive({ name: '', category: '', store: '', size: 'M', price: 0, color: '', quantity: 0, image: null })
const toEdit = reactive({ id: null, name: '', category: '', store: '', size: 'M', price: 0, color: '', quantity: 0, image: null })
const filterName = ref('')
const filterCategory = ref('')
const user = ref(null)
const editVisible = ref(false)

const isAdmin = computed(() => user.value?.is_superuser)

const filteredProducts = computed(() =>
  products.value.filter(p =>
    p.name.toLowerCase().includes(filterName.value.toLowerCase()) &&
    (!filterCategory.value || p.category === Number(filterCategory.value))
  )
)

function onFileChange(file) {
  toAdd.image = file.raw
}

function onFileChangeEdit(file) {
  toEdit.image = file.raw
}

async function fetchUser() {
  try {
    user.value = (await axios.get('/userprofile/info/')).data
  } catch {
    ElMessage.error('Ошибка загрузки пользователя')
  }
}

async function fetchAll() {
  try {
    products.value = (await axios.get('/products/')).data
    categories.value = (await axios.get('/categories/')).data
    stores.value = (await axios.get('/stores/')).data
  } catch {
    ElMessage.error('Ошибка загрузки данных')
  }
}

async function fetchStats() {
  try {
    productStats.value = (await axios.get('/products/stats/')).data
  } catch {
    ElMessage.error('Ошибка загрузки статистики')
  }
}

async function onAdd() {
  try {
    const formData = new FormData()
    formData.append('name', toAdd.name)
    formData.append('category', toAdd.category)
    formData.append('store', toAdd.store)
    formData.append('size', toAdd.size)
    formData.append('price', toAdd.price)
    formData.append('quantity', toAdd.quantity)
    if (toAdd.color) formData.append('color', toAdd.color)
    if (toAdd.image) formData.append('image', toAdd.image)

    await axios.post('/products/', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    Object.assign(toAdd, { name: '', category: '', store: '', size: 'M', price: 0, color: '', quantity: 0, image: null })
    await Promise.all([fetchAll(), fetchStats()])
    ElMessage.success('Товар добавлен')
  } catch {
    ElMessage.error('Ошибка добавления')
  }
}

async function onRemove(p) {
  try {
    await axios.delete(`/products/${p.id}/`)
    await Promise.all([fetchAll(), fetchStats()])
    ElMessage.success('Товар удален')
  } catch {
    ElMessage.error('Ошибка удаления')
  }
}

function onEditClick(p) {
  Object.assign(toEdit, { ...p, image: null })
  editVisible.value = true
}

async function onUpdate() {
  try {
    const formData = new FormData()
    formData.append('name', toEdit.name)
    formData.append('category', toEdit.category)
    formData.append('store', toEdit.store)
    formData.append('size', toEdit.size)
    formData.append('price', toEdit.price)
    formData.append('quantity', toEdit.quantity)
    if (toEdit.color) formData.append('color', toEdit.color)
    if (toEdit.image) formData.append('image', toEdit.image)

    await axios.put(`/products/${toEdit.id}/`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    await Promise.all([fetchAll(), fetchStats()])
    editVisible.value = false
    ElMessage.success('Товар обновлен')
  } catch {
    ElMessage.error('Ошибка обновления')
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
      <h1>Товары</h1>
    </el-header>

    <el-card v-if="productStats">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="Всего товаров" :value="productStats.count || 0" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="Средняя цена" :value="productStats.avg_price || 0" suffix="₽" />
        </el-col>
      </el-row>
    </el-card>

    <el-card v-if="isAdmin">
      <h3>Добавить товар</h3>
      <el-form @submit.prevent="onAdd">
        <el-input v-model="toAdd.name" placeholder="Название" style="margin-bottom: 10px;" />
        <el-select v-model="toAdd.category" placeholder="Категория" style="width: 100%; margin-bottom: 10px;">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="toAdd.store" placeholder="Магазин" style="width: 100%; margin-bottom: 10px;">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-input v-model="toAdd.color" placeholder="Цвет" style="margin-bottom: 10px;" />
        <el-select v-model="toAdd.size" placeholder="Размер" style="width: 100%; margin-bottom: 10px;">
          <el-option label="XS" value="XS" />
          <el-option label="S" value="S" />
          <el-option label="M" value="M" />
          <el-option label="L" value="L" />
          <el-option label="XL" value="XL" />
          <el-option label="XXL" value="XXL" />
        </el-select>

        <!-- Разделение полей Цена и Количество -->
        <el-row :gutter="20" style="margin-bottom: 10px;">
          <el-col :span="12">
            <el-input-number v-model="toAdd.price" :min="0" placeholder="Цена" style="width: 100%;" />
          </el-col>
          <el-col :span="12">
            <el-input-number v-model="toAdd.quantity" :min="0" placeholder="Количество" style="width: 100%;" />
          </el-col>
        </el-row>

        <el-upload :auto-upload="false" :limit="1" :on-change="onFileChange" accept="image/*"
          style="margin-bottom: 10px;">
          <el-button>Загрузить фото</el-button>
        </el-upload>
        <el-button type="primary" native-type="submit">Добавить товар</el-button>
      </el-form>
    </el-card>


    <el-input v-model="filterName" placeholder="Поиск..." style="margin: 20px 0;" />
    <el-select v-model="filterCategory" placeholder="Все категории" style="margin: 0 10px 20px 0; width: 200px;">
      <el-option label="Все категории" value="" />
      <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
    </el-select>

    <el-table :data="filteredProducts" stripe>
      <el-table-column prop="name" label="Название" />
      <el-table-column prop="category_name" label="Категория" />
      <el-table-column prop="store_name" label="Магазин" />
      <el-table-column prop="size" label="Размер" />
      <el-table-column prop="price" label="Цена" />
      <el-table-column prop="color" label="Цвет" />
      <el-table-column prop="quantity" label="Количество" />
      <el-table-column label="Фото" width="100">
        <template #default="{ row }">
          <el-image v-if="row.image" :src="row.image" style="width: 50px; height: 50px;" fit="cover" />
        </template>
      </el-table-column>
      <el-table-column label="Действия" width="120" v-if="isAdmin">
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
        <el-form-item label="Категория">
          <el-select v-model="toEdit.category" style="width: 100%;">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Магазин">
          <el-select v-model="toEdit.store" style="width: 100%;">
            <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Цвет">
          <el-input v-model="toEdit.color" />
        </el-form-item>
        <el-form-item label="Размер">
          <el-select v-model="toEdit.size" style="width: 100%;">
            <el-option label="XS" value="XS" />
            <el-option label="S" value="S" />
            <el-option label="M" value="M" />
            <el-option label="L" value="L" />
            <el-option label="XL" value="XL" />
            <el-option label="XXL" value="XXL" />
          </el-select>
        </el-form-item>
        <el-form-item label="Цена">
          <el-input-number v-model="toEdit.price" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Количество">
          <el-input-number v-model="toEdit.quantity" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Фото">
          <el-upload :auto-upload="false" :limit="1" :on-change="onFileChangeEdit" accept="image/*">
            <el-button>Загрузить фото</el-button>
          </el-upload>
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