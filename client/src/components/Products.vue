<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/userStore'

const userStore = useUserStore()

const products = ref([])
const categories = ref([])
const stores = ref([])
const productStats = ref(null)

const filterName = ref('')
const filterCategory = ref('')

const editVisible = ref(false)

const addName = ref('')
const addCategory = ref('')
const addStore = ref('')
const addSize = ref('M')
const addPrice = ref(0)
const addColor = ref('')
const addQuantity = ref(0)
const addImage = ref(null)

const editId = ref(null)
const editName = ref('')
const editCategory = ref('')
const editStore = ref('')
const editSize = ref('M')
const editPrice = ref(0)
const editColor = ref('')
const editQuantity = ref(0)
const editImage = ref(null)

const isAdmin = computed(() => userStore.isSuperUser)

const filteredProducts = computed(() => {
  return products.value.filter(p =>
    p.name.toLowerCase().includes(filterName.value.toLowerCase()) &&
    (!filterCategory.value || p.category === Number(filterCategory.value))
  )
})

function onAddFile(file) {
  addImage.value = file.raw
}

function onEditFile(file) {
  editImage.value = file.raw
}

async function fetchUser() {
  await userStore.fetchUserInfo()
}

async function fetchProducts() {
  products.value = (await axios.get('/products/')).data
}

async function fetchCategories() {
  categories.value = (await axios.get('/categories/')).data
}

async function fetchStores() {
  stores.value = (await axios.get('/stores/')).data
}

async function fetchStats() {
  productStats.value = (await axios.get('/products/stats/')).data
}

async function loadAll() {
  await fetchProducts()
  await fetchCategories()
  await fetchStores()
  await fetchStats()
}

async function addProduct() {
  const data = new FormData()

  data.append('name', addName.value)
  data.append('category', addCategory.value)
  data.append('store', addStore.value)
  data.append('size', addSize.value)
  data.append('price', addPrice.value)
  data.append('quantity', addQuantity.value)

  if (addColor.value) {
    data.append('color', addColor.value)
  }

  if (addImage.value) {
    data.append('image', addImage.value)
  }

  await axios.post('/products/', data)

  addName.value = ''
  addCategory.value = ''
  addStore.value = ''
  addSize.value = 'M'
  addPrice.value = 0
  addColor.value = ''
  addQuantity.value = 0
  addImage.value = null

  await loadAll()
  ElMessage.success('Товар добавлен')
}

function openEdit(p) {
  editId.value = p.id
  editName.value = p.name
  editCategory.value = p.category
  editStore.value = p.store
  editSize.value = p.size
  editPrice.value = p.price
  editColor.value = p.color
  editQuantity.value = p.quantity
  editImage.value = null
  editVisible.value = true
}

async function updateProduct() {
  const data = new FormData()

  data.append('name', editName.value)
  data.append('category', editCategory.value)
  data.append('store', editStore.value)
  data.append('size', editSize.value)
  data.append('price', editPrice.value)
  data.append('quantity', editQuantity.value)

  if (editColor.value) {
    data.append('color', editColor.value)
  }

  if (editImage.value) {
    data.append('image', editImage.value)
  }

  await axios.put(`/products/${editId.value}/`, data)

  editVisible.value = false
  await loadAll()
  ElMessage.success('Товар обновлен')
}

async function removeProduct(p) {
  await axios.delete(`/products/${p.id}/`)
  await loadAll()
  ElMessage.success('Товар удален')
}

async function exportFile() {
  if (!isAdmin.value) {
    ElMessage.error('Нет доступа')
    return
  }

  const response = await axios.get('/products/export/?type=excel', {
    responseType: 'blob'
  })

  const blob = response.data
  const link = document.createElement('a')

  link.href = URL.createObjectURL(blob)
  link.download = 'Products.xlsx'
  link.click()
}

onMounted(async () => {
  await fetchUser()
  await loadAll()
})
</script>

<template>
  <div>
    <h1>Товары</h1>

    <div v-if="productStats">
      <div>Всего: {{ productStats.count }}</div>
      <div>Средняя цена: {{ productStats.avg_price }} ₽</div>
    </div>

    <div v-if="isAdmin">
      <el-button type="primary" @click="exportFile">
        Экспорт в Excel
      </el-button>
    </div>


    <div v-if="isAdmin">
      <h3>Добавить товар</h3>

      <el-form @submit.prevent="addProduct">
        <el-input v-model="addName" placeholder="Название" />
        <el-select v-model="addCategory">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="addStore">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-input v-model="addColor" placeholder="Цвет" />
        <el-select v-model="addSize">
          <el-option label="XS" value="XS" />
          <el-option label="S" value="S" />
          <el-option label="M" value="M" />
          <el-option label="L" value="L" />
          <el-option label="XL" value="XL" />
        </el-select>
        <el-input-number v-model="addPrice" :min="0" />
        <el-input-number v-model="addQuantity" :min="0" />
        <el-upload :auto-upload="false" :limit="1" :on-change="onAddFile">
          <el-button>Фото</el-button>
        </el-upload>
        <el-button type="primary" native-type="submit">Добавить</el-button>
      </el-form>
    </div>

    <el-input v-model="filterName" placeholder="Поиск" />
    <el-select v-model="filterCategory">
      <el-option label="Все" value="" />
      <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
    </el-select>

    <el-table :data="filteredProducts">
      <el-table-column prop="name" label="Название" />
      <el-table-column prop="category_name" label="Категория" />
      <el-table-column prop="store_name" label="Магазин" />
      <el-table-column prop="price" label="Цена" />
      <el-table-column prop="quantity" label="Количество" />
      <el-table-column v-if="isAdmin" label="Действия" #default="{ row }">
        <el-button size="small" @click="openEdit(row)">Изменить</el-button>
        <el-button size="small" type="danger" @click="removeProduct(row)">Удалить</el-button>
      </el-table-column>
    </el-table>


    <el-dialog v-model="editVisible" title="Редактировать">
      <el-form>
        <el-input v-model="editName" />
        <el-select v-model="editCategory">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="editStore">
          <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
        </el-select>
        <el-input v-model="editColor" />
        <el-select v-model="editSize">
          <el-option label="XS" value="XS" />
          <el-option label="S" value="S" />
          <el-option label="M" value="M" />
          <el-option label="L" value="L" />
          <el-option label="XL" value="XL" />
        </el-select>
        <el-input-number v-model="editPrice" :min="0" />
        <el-input-number v-model="editQuantity" :min="0" />
        <el-upload :auto-upload="false" :limit="1" :on-change="onEditFile">
          <el-button>Фото</el-button>
        </el-upload>
      </el-form>

      <el-button @click="editVisible = false">Отмена</el-button>
      <el-button type="primary" @click="updateProduct">Сохранить</el-button>
    </el-dialog>
  </div>
</template>
