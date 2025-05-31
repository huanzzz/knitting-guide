<template>
  <div class="pattern-panel">
    <SectionItem
      v-for="(section, idx) in sections"
      :key="idx"
      :section="section"
      :active="activeSection === idx"
      @click="selectSection(idx)"
    />
  </div>
</template>

<script setup>
import SectionItem from './SectionItem.vue'
const props = defineProps({
  sections: Array, // 每个部分的内容
  activeSection: Number // 当前高亮的部分
})
const emit = defineEmits(['update:activeSection'])
function selectSection(idx) {
  emit('update:activeSection', idx)
}
</script>

<style scoped>
.pattern-panel { overflow-y: auto; max-height: 400px; }
</style>
