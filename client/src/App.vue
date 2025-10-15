<template>
  <div class="container py-4">
    <nav class="mb-4 d-flex justify-content-between">
      <div>
        <router-link class="me-3" to="/brands">Бренды</router-link>
        <router-link class="me-3" to="/categories">Категории</router-link>
        <router-link class="me-3" to="/items">Вещи</router-link>
        <router-link class="me-3" to="/purchases">Покупки</router-link>
        <router-link to="/stores">Магазины</router-link>
      </div>

      <!-- Кнопка для админки справа -->
      <a class="btn btn-danger" href="/admin" target="_blank">Админка</a>
    </nav>
    <router-view />
  </div>
</template>

<style scoped>
/* Дополнительное стилизование кнопки */
.btn-danger {
  position: relative;
  right: 0;
  top: 0;
}
</style>



<script setup>

</script>