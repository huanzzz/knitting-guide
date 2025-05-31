<template>
  <div class="preview-panel">
    <div class="preview-content">
      <img
        v-if="isImage && currentSrc"
        :src="currentSrc"
        alt="预览图片"
        class="preview-img"
        @error="console.log('图片加载失败', currentSrc)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
const props = defineProps({
  files: Array, // 图片或PDF文件列表
  type: { type: String, default: 'image' }
})
const currentPage = ref(0)
const totalPages = computed(() => props.files?.length || 0)
const currentSrc = computed(() => props.files?.[currentPage.value] || '')
const isImage = computed(() => props.type === 'image')

// 调试：监听 currentSrc 变化
watch(currentSrc, (val) => { 
  console.log('当前图片src', val) 
})

// 防止 currentPage 越界
watch(() => props.files, (newFiles) => {
  if (currentPage.value >= (newFiles?.length || 0)) {
    currentPage.value = 0
  }
})
</script>

<style scoped>
.preview-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
  justify-content: center;
}
.preview-content {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.preview-img {
  max-width: 100%;
  max-height: 80vh;
  display: block;
  margin: 0 auto;
  box-shadow: 0 2px 8px #ccc;
  background: #fff;
  border-radius: 12px;
}
</style>
