<template>
  <div>
    <div class="bg-gradient-blur"></div>
    <div class="page-title">
      <img src="/favicon.ico" alt="icon" class="page-icon" /> 大机灵背心
    </div>
    <div class="app-container">
      <div class="preview-panel">
        <div v-if="previewFiles.length > 0" class="preview-content">
          <img :src="previewFiles[currentPage]" :alt="'预览图片 ' + (currentPage + 1)" />
          <div class="preview-controls">
            <FancyCircleButton @click="prevPage" :disabled="currentPage === 0">←</FancyCircleButton>
            <span>{{ currentPage + 1 }} / {{ previewFiles.length }}</span>
            <FancyCircleButton @click="nextPage" :disabled="currentPage === previewFiles.length - 1">→</FancyCircleButton>
          </div>
        </div>
        <div v-else class="no-preview">
          暂无预览图片
        </div>
      </div>
      
      <div class="pattern-panel">
        <div class="pattern-container">
          <div v-if="sections.length > 0" class="sections-container">
            <el-card
              v-for="section in sections"
              :key="section.id"
              class="section-item"
              shadow="hover"
              style="margin-bottom: 28px; cursor: pointer;"
              :class="{ selected: selectedSection && selectedSection.id === section.id }"
              @click="selectSection(section)"
            >
              <template #header>
                <el-text tag="h3" size="large" style="font-weight:600;letter-spacing:1px;">{{ section.title }}</el-text>
              </template>
              <el-text tag="div">
                <div v-html="formatContent(section.content)"></div>
              </el-text>
            </el-card>
          </div>
          <div v-else class="no-sections">
            暂无编织图解内容
          </div>
        </div>
        <div class="counter-container">
          <div v-if="selectedSection" class="counter-wrapper">
            <CounterPanel
              :start="selectedSection.startRow"
              :end="selectedSection.endRow"
              :current="selectedSection.currentRow"
              :section-id="selectedSection.id"
              :is-knitting="selectedSection.isKnitting"
              @update="updateCounter"
              @save="saveRowCounts"
            />
          </div>
          <div v-else class="no-counter">
            请选择一个部分开始编织
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import CounterPanel from './components/CounterPanel.vue'
import KnittingTag from './components/KnittingTag.vue'
import { ElCard, ElText } from 'element-plus'
import FancyCircleButton from './components/FancyCircleButton.vue'

const previewFiles = ref([])
const currentPage = ref(Number(localStorage.getItem('currentPage')) || 0)
const sections = ref([])
const selectedSectionId = localStorage.getItem('selectedSectionId')
const selectedSection = ref(null)
const loading = ref(false)
const error = ref(null)

// 获取图片列表
async function fetchImageList() {
  try {
    loading.value = true
    const response = await fetch('/api/images')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    console.log('图片列表数据:', data)
    if (!data.files || !Array.isArray(data.files)) {
      throw new Error('图片数据格式不正确')
    }
    previewFiles.value = data.files.map(file => `http://localhost:8080${file}`)
  } catch (err) {
    error.value = `获取图片列表失败: ${err.message}`
    console.error('获取图片列表错误:', err)
  } finally {
    loading.value = false
  }
}

// 获取编织图解内容
async function fetchSections() {
  try {
    loading.value = true
    // 并行获取编织图解内容和行数信息
    const [sectionsResponse, rowCountsResponse] = await Promise.all([
      fetch('/api/extracted-sizes'),
      fetch('/api/row-counts')
    ])
    
    if (!sectionsResponse.ok || !rowCountsResponse.ok) {
      throw new Error(`HTTP error! status: ${sectionsResponse.status || rowCountsResponse.status}`)
    }
    
    const [sectionsData, rowCountsData] = await Promise.all([
      sectionsResponse.json(),
      rowCountsResponse.json()
    ])
    
    console.log('编织图解数据:', sectionsData)
    console.log('行数数据:', rowCountsData)
    
    if (!sectionsData.sections || !Array.isArray(sectionsData.sections)) {
      throw new Error('编织图解数据格式不正确')
    }
    
    if (!rowCountsData.sections || !Array.isArray(rowCountsData.sections)) {
      throw new Error('行数数据格式不正确')
    }
    
    // 从本地存储加载保存的行数设置
    const savedCounts = JSON.parse(localStorage.getItem('rowCounts') || '{}')
    
    // 合并编织图解内容和行数信息
    sections.value = sectionsData.sections.map((section, index) => {
      const sectionId = `section-${index}`;
      const rowCountInfo = rowCountsData.sections[index] || {};
      let savedData = savedCounts[sectionId];

      // 判断本地存储的 start/end 是否和 rowCountInfo 一致
      const shouldUseRowCountInfo =
        !savedData ||
        savedData.start !== rowCountInfo.start_row ||
        savedData.end !== rowCountInfo.end_row;

      if (shouldUseRowCountInfo) {
        // 用 rowCountInfo 覆盖本地
        savedData = {
          start: rowCountInfo.start_row,
          end: rowCountInfo.end_row,
          current: rowCountInfo.start_row,
          isKnitting: false,
        };
        savedCounts[sectionId] = savedData;
      }

      const startRow = savedData.start || rowCountInfo.start_row || 1;
      const endRow = savedData.end || rowCountInfo.end_row || 1;
      const currentRow = savedData.current || startRow;

      return {
        id: sectionId,
        title: section.title || `部分 ${index + 1}`,
        content: section.content || '',
        isKnitting: savedData.isKnitting || false,
        currentRow,
        startRow,
        endRow,
      };
    });
    localStorage.setItem('rowCounts', JSON.stringify(savedCounts));
  } catch (err) {
    error.value = `获取编织图解内容失败: ${err.message}`
    console.error('获取编织图解内容错误:', err)
  } finally {
    loading.value = false
  }
}

function prevPage() {
  console.log('prevPage clicked');
  console.log('prevPage clicked', new Error().stack);
  if (currentPage.value > 0) {
    currentPage.value--;
    localStorage.setItem('currentPage', currentPage.value);
  }
}

function nextPage() {
  console.log('nextPage clicked');
  if (currentPage.value < previewFiles.value.length - 1) {
    currentPage.value++;
    localStorage.setItem('currentPage', currentPage.value);
  }
}

// sections 加载后自动恢复选中
watch(sections, (newSections) => {
  if (selectedSectionId) {
    const found = newSections.find(s => s.id === selectedSectionId)
    if (found) selectedSection.value = found
  }
})

function selectSection(section) {
  selectedSection.value = section
  localStorage.setItem('selectedSectionId', section.id)
}

function updateCounter({ start, end, current, sectionId, isKnitting }) {
  const section = sections.value.find(s => s.id === sectionId)
  if (section) {
    section.startRow = start
    section.endRow = end
    section.currentRow = current
    section.isKnitting = isKnitting
    
    // 保存到本地存储
    const savedCounts = JSON.parse(localStorage.getItem('rowCounts') || '{}')
    savedCounts[sectionId] = { start, end, current, isKnitting }
    localStorage.setItem('rowCounts', JSON.stringify(savedCounts))
  }
}

async function saveRowCounts({ sectionId, start, end }) {
  try {
    const response = await fetch('/api/sections/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        sectionId,
        start,
        end
      })
    })
    
    if (!response.ok) {
      throw new Error('保存失败')
    }
    
    // 保存到本地存储
    const savedCounts = JSON.parse(localStorage.getItem('rowCounts') || '{}')
    savedCounts[sectionId] = { start, end }
    localStorage.setItem('rowCounts', JSON.stringify(savedCounts))
  } catch (err) {
    error.value = '保存行数设置失败'
    console.error(err)
  }
}

// 保证换行显示
function formatContent(content) {
  if (!content) return ''
  return content.replace(/\n/g, '<br>')
}

onMounted(async () => {
  await Promise.all([fetchImageList(), fetchSections()])
})
</script>

<style scoped>
body, .app-container {
  min-height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  position: relative;
  overflow-x: hidden;
}
.bg-gradient-blur {
  position: fixed;
  z-index: -1;
  top: 0; left: 0; width: 100vw; height: 100vh;
  pointer-events: none;
  background: radial-gradient(circle at 20% 30%, #CCCEFF 0%, transparent 60%),
              radial-gradient(circle at 80% 20%, #AE8C6C 0%, transparent 70%),
              radial-gradient(circle at 60% 80%, #91BC87 0%, transparent 70%),
              radial-gradient(circle at 60% 80%, #ffffff 0%, transparent 0%),
              linear-gradient(120deg, #F4F5FF 50% 20%, #CCCEFF 100%);
  filter: blur(60px) brightness(1.08);
}
.app-container {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 20px;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  height: calc(100vh - 40px);
}

.preview-panel {
  flex: 1;
  min-width: 300px;
  max-width: 50%;
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-height: 100vh;
}

.pattern-panel {
  flex: 1;
  min-width: 300px;
  max-width: 50%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pattern-container {
  height: 60%;
  border: none;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #fafbfc;
}

.counter-container {
  height: 40%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 32px !important;
}

.counter-wrapper {
  width: 100%;
  max-width: 400px;
}

.no-counter {
  text-align: center;
  color: #666;
  font-size: 16px;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.preview-content img {
  width: 100%;
  height: auto;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 4px 16px rgba(0,0,0,0.10);
  background: #fff;
  display: block;
  margin: 0 auto;
}

.preview-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
}

.sections-container {
  font-family: 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  font-size: 9px;
  line-height: 1.8;
  padding: 32px 12px 32px 12px;
  background: #ffffffb9;
  border: 1px solid #ececec;
  flex: 1;
  overflow-y: auto;
}

.section-item {
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: none;
  cursor: pointer;
}

:deep(.el-card__header) {
  padding: 10px 14px !important;
}

:deep(.el-card__body) {
  padding: 10px 14px !important;
  white-space: pre-line;
}

.section-item p, .section-item div > div, .section-item div > p {
  margin-bottom: 12px;
}

.no-preview,
.no-sections {
  text-align: center;
  padding: 20px;
  color: #666;
  background: #f5f5f5;
  border-radius: 8px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

button {
  padding: 5px 15px;
  border: none;
  border-radius: 4px;
  background: #858dff;
  color: white;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.section-item.selected {
  border: 2px solid #8fa4ff !important;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.12);
}

.page-title {
  position: absolute;
  top: 18px;
  left: 32px;
  font-size: 2.1rem;
  font-weight: 700;
  color: #3a3a3a;
  letter-spacing: 2px;
  z-index: 10;
  font-family: 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  user-select: none;
  display: flex;
  align-items: center;
}

.page-icon {
  margin-right: 8px;
  height: 2.1rem;
  width: auto;
}
</style> 