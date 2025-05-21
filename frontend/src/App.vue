<template>
  <div class="app-layout">
    <div class="left-panel">
      <PreviewPanel :files="previewFiles" />
    </div>
    <div class="right-panel">
      <PatternPanel
        :sections="sections"
        :activeSection="activeSection"
        @update:activeSection="setActiveSection"
      />
      <CounterPanel
        v-if="activeSectionObj"
        :start="activeSectionObj.start"
        :end="activeSectionObj.end"
        :current="activeSectionObj.current"
        @update="updateCounter"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import PreviewPanel from './components/PreviewPanel.vue'
import PatternPanel from './components/PatternPanel.vue'
import CounterPanel from './components/CounterPanel.vue'

// 静态模拟数据
const previewFiles = [
  '/imgs/page_01.png',
  '/imgs/page_02.png',
  '/imgs/page_03.png'
]
const sections = ref([
  { title: '折叠边', content: '第1-8行：上针，下针...', start: 1, end: 8, current: 1, isKnitting: true },
  { title: '蕾丝花样', content: '第9-60行：花样编织...', start: 9, end: 60, current: 9, isKnitting: false },
  { title: '左前片', content: '第61-74行：...', start: 61, end: 74, current: 61, isKnitting: false }
])
const activeSection = ref(0)
const activeSectionObj = computed(() => sections.value[activeSection.value])
function setActiveSection(idx) {
  activeSection.value = idx
}
function updateCounter(val) {
  // 更新当前部分的计数器数据
  sections.value[activeSection.value] = {
    ...sections.value[activeSection.value],
    ...val
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: row;
  height: 100vh;
}
.left-panel {
  flex: 1;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #eee;
}
.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  padding: 24px;
  overflow: auto;
}
</style> 