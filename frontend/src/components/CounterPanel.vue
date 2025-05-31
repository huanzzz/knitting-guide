<template>
  <div class="counter-panel">
    <el-button class="edit-btn" circle size="small" @click="showEdit = true">
      <el-icon><Edit /></el-icon>
    </el-button>
    <div class="counter-content">
      <FancyCircleButton @click="decrease" :disabled="currentRow <= startRow">-</FancyCircleButton>
      <div class="progress-container">
        <svg width="160" height="100" viewBox="0 0 160 100">
          <path
            d="M 20 90 A 60 60 0 0 1 140 90"
            fill="none"
            stroke="#e0e0e0"
            stroke-width="10"
          />
          <path
            d="M 20 90 A 60 60 0 0 1 140 90"
            fill="none"
            :stroke="progressColor"
            stroke-width="10"
            :stroke-dasharray="progressLength + ', 999'"
            stroke-linecap="round"
          />
        </svg>
        <div class="current-row">{{ currentRow }}</div>
        <div class="range-label left">{{ startRow }}</div>
        <div class="range-label right">{{ endRow }}</div>
      </div>
      <FancyCircleButton @click="increase">+</FancyCircleButton>
    </div>
    <el-dialog v-model="showEdit" title="编辑行数" width="300px" :close-on-click-modal="false">
      <el-form label-width="60px">
        <el-form-item label="起始行">
          <el-input-number v-model="editStart" :min="1" :max="editEnd" />
        </el-form-item>
        <el-form-item label="结束行">
          <el-input-number v-model="editEnd" :min="editStart" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { ElDialog, ElButton, ElForm, ElFormItem, ElInputNumber, ElIcon } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import FancyCircleButton from './FancyCircleButton.vue'
import 'element-plus/es/components/dialog/style/css'
import 'element-plus/es/components/button/style/css'
import 'element-plus/es/components/form/style/css'
import 'element-plus/es/components/form-item/style/css'
import 'element-plus/es/components/input-number/style/css'
import 'element-plus/es/components/icon/style/css'

const props = defineProps({
  start: Number,
  end: Number,
  current: Number,
  sectionId: String,
  isKnitting: Boolean
})
const emit = defineEmits(['update', 'save'])

const startRow = ref(props.start)
const endRow = ref(props.end)
const currentRow = ref(props.current)

watch(() => props.start, val => startRow.value = val)
watch(() => props.end, val => endRow.value = val)
watch(() => props.current, val => currentRow.value = val)

function increase() {
  currentRow.value++
  emitUpdate()
}
function decrease() {
  if (currentRow.value > startRow.value) {
    currentRow.value--
    emitUpdate()
  }
}
function emitUpdate() {
  emit('update', {
    start: startRow.value,
    end: endRow.value,
    current: currentRow.value,
    sectionId: props.sectionId,
    isKnitting: props.isKnitting
  })
}

// 编辑弹窗逻辑
const showEdit = ref(false)
const editStart = ref(startRow.value)
const editEnd = ref(endRow.value)
watch(showEdit, (val) => {
  if (val) {
    editStart.value = startRow.value
    editEnd.value = endRow.value
  }
})
function saveEdit() {
  startRow.value = editStart.value
  endRow.value = editEnd.value
  if (currentRow.value < startRow.value) currentRow.value = startRow.value
  if (currentRow.value > endRow.value) currentRow.value = endRow.value
  emitUpdate()
  emit('save', { sectionId: props.sectionId, start: startRow.value, end: endRow.value })
  showEdit.value = false
}

// 半圆进度条计算
const progress = computed(() => {
  const total = endRow.value - startRow.value + 1
  if (total <= 0) return 0
  let p = (currentRow.value - startRow.value + 1) / total
  if (p > 1) p = 1
  if (p < 0) p = 0
  return p
})
const progressLength = computed(() => 188.4 * progress.value) // 188.4为半圆弧长
const progressColor = computed(() => progress.value >= 1 ? '#3B82F6' : '#7E82FF')
</script>

<style scoped>
.counter-panel {
  width: 100%;
  min-height: 180px;
  border-radius: 10px;
  overflow: visible;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.08);
  padding: 32px 32px 24px 32px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  background: #ffffff;
}
.counter-content {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 56px;
  width: 100%;
}
.counter-btn {
  width: 56px;
  height: 56px;
  font-size: 32px;
  border: 1.5px solid #bbb;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
  transition: box-shadow .2s, border-color .2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.counter-btn:active {
  box-shadow: 0 2px 8px #ccc;
  border-color: #888;
}
.progress-container {
  position: relative;
  width: 160px;
  height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
svg {
  display: block;
}
.current-row {
  position: absolute;
  left: 0; right: 0;
  top: 60px;
  text-align: center;
  font-size: 40px;
  font-weight: 700;
  z-index: 1;
  color: #222;
  letter-spacing: 2px;
  line-height: 1;
}
.range-label {
  position: absolute;
  top: 100px;
  font-size: 18px;
  color: #bbb;
  font-weight: 400;
  z-index: 1;
}
.range-label.left { left: 12px; }
.range-label.right { right: 12px; }
.edit-btn {
  position: absolute;
  top: 30px;
  right: 24px;
  z-index: 10;
  background: white;
  box-shadow: 0 2px 8px #eee;

}
</style>
