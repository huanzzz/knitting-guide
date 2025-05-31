<template>
  <div
    class="section-item"
    :class="{ active }"
    @click="$emit('click')"
  >
    <div class="section-title">
      {{ section.title }}
      <KnittingTag v-if="section.isKnitting" />
    </div>
    <div class="section-content">{{ section.content }}</div>
  </div>
</template>

<script setup>
import KnittingTag from './KnittingTag.vue'
const props = defineProps({
  section: Object,
  active: Boolean
})
</script>

<style scoped>
.section-item { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
.section-item.active { background: #f0f8ff; }
.section-title { font-weight: bold; }
</style>
