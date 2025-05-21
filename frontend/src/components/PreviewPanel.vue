<template>
  <div class="preview-panel">
    <button @click="prevPage">←</button>
    <div class="preview-content">
      <img v-if="isImage" :src="currentSrc" alt="预览图片" />
      <!-- PDF 预览可后续集成 pdf.js -->
    </div>
    <button @click="nextPage">→</button>
    <div class="page-info">{{ currentPage + 1 }} / {{ totalPages }}</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const props = defineProps({
  files: Array, // 图片或PDF文件列表
  type: { type: String, default: 'image' }
})
const currentPage = ref(0)
const totalPages = computed(() => props.files?.length || 0)
const currentSrc = computed(() => props.files?.[currentPage.value] || '')
const isImage = computed(() => props.type === 'image')
function prevPage() {
  if (currentPage.value > 0) currentPage.value--
}
function nextPage() {
  if (currentPage.value < totalPages.value - 1) currentPage.value++
}
</script>

<style scoped>
.preview-panel { display: flex; flex-direction: column; align-items: center; }
.preview-content { min-width: 200px; min-height: 300px; margin: 10px 0; }
.page-info { margin-top: 8px; }
</style>
