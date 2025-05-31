# Knitting Counter PRD (Product Requirements Document)

## 1. Project Background
The knitting counter page is designed to help users view knitting patterns while counting current knitting rows during the knitting process, enhancing knitting efficiency and experience.

## 2. Main Functional Requirements

### 1. Preview Original Files
- Support previewing original knitting pattern PDFs or images with left/right page navigation.
- Display one page at a time, users can navigate through pages using buttons.

### 2. Extract Size-Specific Knitting Pattern Content (extracted sizes)
- Display knitting pattern content by sections.
- Show section titles and detailed content.
- Content area is scrollable up and down.
- When clicking on a section, highlight that section text and sync with the counter below.
- For the currently knitting section, display a "knitting" tag next to the title.

### 3. Knitting Counter
- Before starting knitting, display a "Start Knitting" button.
- After clicking "Start Knitting", display the counter.
- Counter can be incremented/decremented, showing current row, start row, and end row.
- Start row and end row are editable; after user editing, save as custom row_counts.
- Counter minimum value is the start row, maximum is unlimited.
- Each knitting section has independent counter data.

### 4. Knitting Tag Logic
- After user clicks "Start Knitting", the current section displays a knitting tag.
- When current row is less than or equal to end row, display knitting tag.

## 3. Technical Implementation
- Frontend: Vue 3 + Vite, component-based development.
- Backend: Flask, providing row_counts, extracted_sizes, images and other APIs.
- Frontend-backend separation, APIs accessed via axios/fetch.
- User custom data can be persisted using localStorage.

## 4. Interaction Guidelines
- Three-column layout: preview area, content area, and counter area.
- Content area click to switch highlighting and counter.
- Counter supports increment/decrement, editing, and saving.

## 5. Future Extensions
- Support PDF preview
- Multi-user/multi-project switching
- Progress export/sharing

---

# 编织计数器 PRD（产品需求文档）

## 1. 项目背景
编织计数器页面用于帮助用户在编织过程中，一边查看编织图解内容，一边计数当前编织行，提升编织效率和体验。

## 2. 主要功能需求

### 1. 预览原文件
- 支持预览原编织图解PDF或图片，支持左右翻页查看。
- 每次显示一页，用户可通过按钮翻页。

### 2. 抽取尺码后的编织图解内容（extracted sizes）
- 按部分显示编织图解内容。
- 显示每部分标题和详细内容。
- 内容区可上下滚动。
- 点击某部分时，高亮该部分文字，并同步下方计数器。
- 当前正在编织的部分，标题旁显示"knitting"标签。

### 3. 编织计数器
- 未开始编织时，显示"开始编织"按钮。
- 点击"开始编织"后，显示计数器。
- 计数器可加减，显示当前行、起始行、结束行。
- 起始行、结束行可编辑，用户编辑后保存为自定义 row_counts。
- 计数器最小值为起始行，最大不限。
- 每一个编织部分有独立的计数器数据

### 4. knitting 标签逻辑
- 用户点击"开始编织"后，当前部分显示 knitting 标签。
- 当前行小于等于结束行时，显示 knitting 标签。

## 3. 技术实现
- 前端：Vue 3 + Vite，组件化开发。
- 后端：Flask，提供 row_counts、extracted_sizes、图片等 API。
- 前后端分离，API 通过 axios/fetch 获取。
- 用户自定义数据可用 localStorage 持久化。

## 4. 交互说明
- 预览区、内容区、计数器区三栏布局。
- 内容区点击切换高亮和计数器。
- 计数器支持加减、编辑、保存。

## 5. 未来可扩展
- 支持 PDF 预览
- 多用户/多项目切换
- 进度导出/分享 