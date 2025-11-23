<template>
  <div class="purchases-page">
    <div class="header-stats">
      <h2>Покупки</h2>
      <div class="stats-and-buttons">
        <div class="stats-cards">
          <div class="stat-card">Количество: {{ purchaseStats?.count || 0 }}</div>
          <div class="stat-card">Среднее: {{ purchaseStats?.avg || 0 }}</div>
          <div class="stat-card">Максимум: {{ purchaseStats?.max || 0 }}</div>
          <div class="stat-card">Минимум: {{ purchaseStats?.min || 0 }}</div>
        </div>
        <div class="export-buttons">
          <button class="btn-export excel" @click="exportExcel">
            <i class="bi bi-file-earmark-spreadsheet-fill"></i> Excel
          </button>
          <button class="btn-export word" @click="exportWord">
            <i class="bi bi-file-earmark-word-fill"></i> Word
          </button>
        </div>
      </div>
    </div>

    <form @submit.prevent="onAdd" class="add-form">
      <select v-model="toAdd.buyer" required>
        <option disabled value="">Выберите покупателя</option>
        <option v-for="b in buyers" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model="toAdd.brand" required>
        <option disabled value="">Выберите бренд</option>
        <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model="toAdd.clothing_type" required>
        <option disabled value="">Выберите тип одежды</option>
        <option v-for="c in clothingTypes" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <select v-model="toAdd.store" required>
        <option disabled value="">Выберите магазин</option>
        <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
      <input v-model.number="toAdd.amount" type="number" min="1" placeholder="Кол-во" class="amount-field" required />
      <input v-model="toAdd.date" type="date" required />
      <button type="submit" class="btn-add">Добавить</button>
    </form>

    <div class="filters">
      <input v-model="filterBuyer" placeholder="Фильтр по покупателю" />
      <input v-model="filterBrand" placeholder="Фильтр по бренду" />
      <input v-model="filterClothingType" placeholder="Фильтр по типу одежды" />
      <input v-model="filterStore" placeholder="Фильтр по магазину" />
      <input v-model.number="filterAmount" type="number" placeholder="Фильтр по количеству" />
      <input v-model="filterDate" type="date" placeholder="Фильтр по дате" />
    </div>

    <div class="cards-grid">
      <div v-for="p in filteredPurchases" :key="p.id" class="purchase-card">
        <div>
          <strong>{{ buyersById[p.buyer]?.name }}</strong> — {{ brandsById[p.brand]?.name }} / {{ clothingTypesById[p.clothing_type]?.name }} / {{ storesById[p.store]?.name }}
          <br>
          <small class="text-muted">{{ p.amount }} шт, {{ p.date }}</small>
        </div>
        <div class="card-buttons">
          <button class="btn-edit" @click="onEditClick(p)" data-bs-toggle="modal" data-bs-target="#editPurchaseModal">
            <i class="bi bi-pen-fill"></i>
          </button>
          <button class="btn-delete" @click="onRemove(p)">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>

    <div class="modal fade" id="editPurchaseModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5>Редактировать покупку</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <select v-model="toEdit.buyer" class="mb-2">
              <option v-for="b in buyers" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
            <select v-model="toEdit.brand" class="mb-2">
              <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
            </select>
            <select v-model="toEdit.clothing_type" class="mb-2">
              <option v-for="c in clothingTypes" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
            <select v-model="toEdit.store" class="mb-2">
              <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
            <input v-model.number="toEdit.amount" type="number" class="mb-2" />
            <input v-model="toEdit.date" type="date" />
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
            <button class="btn btn-primary" @click="onUpdate" data-bs-dismiss="modal">Сохранить</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const purchases = ref([])
const buyers = ref([])
const brands = ref([])
const clothingTypes = ref([])
const stores = ref([])
const purchaseStats = ref({})

const toAdd = ref({ buyer:'', brand:'', clothing_type:'', store:'', amount:1, date:'' })
const toEdit = ref({ id:null, buyer:'', brand:'', clothing_type:'', store:'', amount:1, date:'' })

const buyersById = computed(() => Object.fromEntries(buyers.value.map(b=>[b.id,b])))
const brandsById = computed(() => Object.fromEntries(brands.value.map(b=>[b.id,b])))
const clothingTypesById = computed(() => Object.fromEntries(clothingTypes.value.map(c=>[c.id,c])))
const storesById = computed(() => Object.fromEntries(stores.value.map(s=>[s.id,s])))

const filterBuyer = ref('')
const filterBrand = ref('')
const filterClothingType = ref('')
const filterStore = ref('')
const filterAmount = ref(null)
const filterDate = ref('')

const filteredPurchases = computed(() => {
  return purchases.value.filter(p =>
    (!filterBuyer.value || buyersById.value[p.buyer]?.name.toLowerCase().includes(filterBuyer.value.toLowerCase())) &&
    (!filterBrand.value || brandsById.value[p.brand]?.name.toLowerCase().includes(filterBrand.value.toLowerCase())) &&
    (!filterClothingType.value || clothingTypesById.value[p.clothing_type]?.name.toLowerCase().includes(filterClothingType.value.toLowerCase())) &&
    (!filterStore.value || storesById.value[p.store]?.name.toLowerCase().includes(filterStore.value.toLowerCase())) &&
    (filterAmount.value===null || p.amount===filterAmount.value) &&
    (!filterDate.value || p.date===filterDate.value)
  )
})

async function fetchAll() {
  const [p,b,br,ct,s] = await Promise.all([
    axios.get('/purchases/').then(r=>r.data),
    axios.get('/buyers/').then(r=>r.data),
    axios.get('/brands/').then(r=>r.data),
    axios.get('/clothing-types/').then(r=>r.data),
    axios.get('/stores/').then(r=>r.data)
  ])
  purchases.value=p; buyers.value=b; brands.value=br; clothingTypes.value=ct; stores.value=s
}

async function fetchPurchaseStats() {
  purchaseStats.value=(await axios.get('/purchases/stats/')).data
}

async function onAdd() {
  await axios.post('/purchases/', {...toAdd.value})
  toAdd.value={ buyer:'', brand:'', clothing_type:'', store:'', amount:1, date:'' }
  await Promise.all([fetchAll(), fetchPurchaseStats()])
}

async function onRemove(p) {
  if(!confirm(`Удалить покупку от ${p.date}?`)) return
  await axios.delete(`/purchases/${p.id}/`)
  await Promise.all([fetchAll(), fetchPurchaseStats()])
}

function onEditClick(p) { toEdit.value={...p} }
async function onUpdate() { await axios.put(`/purchases/${toEdit.value.id}/`, {...toEdit.value}); await Promise.all([fetchAll(), fetchPurchaseStats()]) }

async function exportExcel() {
  const res=await axios.get('/purchases/export-excel/', { responseType:'blob' })
  const url=window.URL.createObjectURL(new Blob([res.data]))
  const link=document.createElement('a'); link.href=url; link.setAttribute('download','Purchases.xlsx'); document.body.appendChild(link); link.click(); link.remove()
}

async function exportWord() {
  const res=await axios.get('/purchases/export-word/', { responseType:'blob' })
  const url=window.URL.createObjectURL(new Blob([res.data]))
  const link=document.createElement('a'); link.href=url; link.setAttribute('download','Purchases.docx'); document.body.appendChild(link); link.click(); link.remove()
}

onMounted(async()=>{ await Promise.all([fetchAll(), fetchPurchaseStats()]) })
</script>

<style scoped>
.purchases-page {
  background: #fff;
  padding: 25px;
  border-radius: 15px;
  font-family: 'Arial', sans-serif;
}

h2 {
  color: #d63384;
  margin-bottom: 10px;
}

.header-stats {
  margin-bottom: 20px;
}

.stats-and-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.stats-cards {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.stat-card {
  background: #fff0f5;
  padding: 4px 10px;
  border-radius: 15px;
  color: #d63384;
  font-weight: bold;
  font-size: 0.85rem;
  box-shadow: 0 2px 6px rgba(255,105,180,0.15);
}

.export-buttons {
  display: flex;
  gap: 10px;
}

.btn-export {
  font-weight: bold;
  border-radius: 15px;
  padding: 6px 14px;
  color: white;
  border: none;
  cursor: pointer;
  transition: opacity 0.25s;
}

.btn-export.excel { background: #28a745; }
.btn-export.word { background: #007bff; }
.btn-export:hover { opacity: 0.85; }

.add-form {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 20px;
}

.add-form select,
.add-form input {
  flex: 1;
  padding: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
  font-size: 0.9rem;
}

.amount-field {
  max-width: 200px;
}

.btn-add {
  background: #ff1493;
  color: white;
  border: none;
  border-radius: 15px;
  padding: 8px 16px;
  cursor: pointer;
  height: 42px;
  transition: background 0.25s;
}

.btn-add:hover { background: #ff69b4; }

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.filters input {
  flex: 1;
  padding: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 20px;
}

.purchase-card {
  background: #fff0f5;
  border: 1px solid #ffb6c1;
  border-radius: 15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 6px 15px rgba(255,105,180,0.1);
}

.purchase-card small {
  color: #4b1a30;
}

.card-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.btn-edit,
.btn-delete {
  border-radius: 15px;
  padding: 6px 10px;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.25s;
}

.btn-edit { background: #ff69b4; }
.btn-edit:hover { background: #ff1493; }
.btn-delete { background: #dc3545; }
.btn-delete:hover { background: #c82333; }

.modal-content input,
.modal-content select {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 15px;
  border: 1px solid #ffb6c1;
  background-color: #fff0f5;
}
</style>
