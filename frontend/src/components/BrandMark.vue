<script setup lang="ts">
import xlmIcon from '../assets/xlm.svg'

withDefaults(defineProps<{ size?: number }>(), { size: 28 })
</script>

<template>
  <img :src="xlmIcon" :width="size" :height="size" alt="Logo" class="brand-icon" />
</template>

<style scoped>
.brand-icon {
  object-fit: contain;
}
</style>

