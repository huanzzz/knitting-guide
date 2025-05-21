<template>
  <div class="counter-panel">
    <div v-if="!isKnitting">
      <button @click="startKnitting">开始编织</button>
    </div>
    <div v-else>
      <button @click="decrease">-</button>
      <input v-model="currentRow" type="number" :min="startRow" :max="endRow" />
      <button @click="increase">+</button>
      <div>
        起始行：<input v-model="startRow" type="number" />
        结束行：<input v-model="endRow" type="number" />
      </div>
      <KnittingTag v-if="showKnittingTag" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import KnittingTag from './KnittingTag.vue'
const props = defineProps({
  start: Number,
  end: Number,
  current: Number
})
const emit = defineEmits(['update'])
const isKnitting = ref(false)
const startRow = ref(props.start || 1)
const endRow = ref(props.end || 1)
const currentRow = ref(props.current || startRow.value)
function startKnitting() {
  isKnitting.value = true
  currentRow.value = startRow.value
}
function increase() {
  if (currentRow.value < endRow.value) currentRow.value++
}
function decrease() {
  if (currentRow.value > startRow.value) currentRow.value--
}
const showKnittingTag = computed(() => isKnitting.value && currentRow.value <= endRow.value)
watch([startRow, endRow, currentRow], () => {
  emit('update', { start: startRow.value, end: endRow.value, current: currentRow.value })
})
</script>

<style scoped>
.counter-panel { margin-top: 20px; }
</style>
