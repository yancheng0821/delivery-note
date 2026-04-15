<template>
  <div class="app">
    <header class="app-header">
      <div class="header-inner">
        <div class="header-left">
          <div class="logo-mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <span class="header-title">送货单生成</span>
        </div>
        <span class="header-org">宏远商贸</span>
      </div>
    </header>

    <main class="app-main">
      <!-- 步骤指示器 -->
      <div class="steps">
        <div class="step" :class="{ active: true, done: materials.length > 0 }">
          <span class="step-num">1</span>
          <span class="step-label">上传清单</span>
        </div>
        <div class="step-line" :class="{ active: materials.length > 0 }"></div>
        <div class="step" :class="{ active: materials.length > 0 }">
          <span class="step-num">2</span>
          <span class="step-label">选择物料</span>
        </div>
        <div class="step-line" :class="{ active: hasSelection }"></div>
        <div class="step" :class="{ active: hasSelection }">
          <span class="step-num">3</span>
          <span class="step-label">生成送货单</span>
        </div>
      </div>

      <div class="content-grid">
        <!-- 左列 -->
        <div class="col-left">
          <FileUpload @materials-loaded="onMaterialsLoaded" />

          <section class="card">
            <h3 class="card-title">客户信息</h3>
            <CustomerForm ref="customerFormRef" />
          </section>

          <!-- 生成按钮 -->
          <button
            class="btn-generate"
            :class="{ disabled: !canGenerate, loading: generating }"
            :disabled="!canGenerate || generating"
            @click="handleGenerate"
          >
            <svg v-if="!generating" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span class="loading-spinner" v-if="generating"></span>
            {{ generating ? '生成中...' : '生成送货单' }}
          </button>
        </div>

        <!-- 右列 -->
        <div class="col-right">
          <MaterialTable
            ref="materialTableRef"
            :materials="materials"
            @selection-change="onSelectionChange"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import FileUpload from './components/FileUpload.vue'
import CustomerForm from './components/CustomerForm.vue'
import MaterialTable from './components/MaterialTable.vue'

const materials = ref([])
const customerFormRef = ref(null)
const materialTableRef = ref(null)
const generating = ref(false)
const hasSelection = ref(false)

const canGenerate = computed(() => materials.value.length > 0 && hasSelection.value)

function onMaterialsLoaded(data) {
  materials.value = data
}

function onSelectionChange(count) {
  hasSelection.value = count > 0
}

async function handleGenerate() {
  try {
    await customerFormRef.value.validate()
  } catch {
    ElMessage.warning('请填写客户名称')
    return
  }

  const selected = materialTableRef.value.getSelectedMaterials()
  if (selected.length === 0) {
    ElMessage.warning('请至少勾选一条物料')
    return
  }

  const customer = customerFormRef.value.getData()

  generating.value = true
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer, materials: selected }),
    })

    if (!response.ok) throw new Error('生成失败')

    const result = await response.json()
    ElMessage.success(`已保存到桌面：${result.filename}`)
  } catch (err) {
    ElMessage.error(err.message || '生成失败，请重试')
  } finally {
    generating.value = false
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --color-primary: #0891B2;
  --color-primary-light: #22D3EE;
  --color-primary-bg: #ECFEFF;
  --color-success: #22C55E;
  --color-success-bg: #F0FDF4;
  --color-warning: #F59E0B;
  --color-text: #164E63;
  --color-text-secondary: #64748B;
  --color-text-muted: #94A3B8;
  --color-border: #E2E8F0;
  --color-bg: #F8FAFC;
  --color-white: #FFFFFF;
  --radius: 8px;
  --radius-lg: 12px;
  --transition: 150ms ease;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
}

/* ---- Header ---- */
.app-header {
  height: 52px;
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-mark {
  width: 32px;
  height: 32px;
  background: var(--color-primary);
  color: #fff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 0.5px;
}

.header-org {
  font-size: 13px;
  color: var(--color-text-muted);
  font-weight: 400;
}

/* ---- Steps ---- */
.steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 28px;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.35;
  transition: opacity var(--transition);
}

.step.active {
  opacity: 1;
}

.step-num {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-border);
  color: var(--color-text-muted);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition);
}

.step.active .step-num {
  background: var(--color-primary);
  color: #fff;
}

.step.done .step-num {
  background: var(--color-success);
  color: #fff;
}

.step-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.step.active .step-label {
  color: var(--color-text);
}

.step-line {
  width: 48px;
  height: 1px;
  background: var(--color-border);
  margin: 0 12px;
  transition: background var(--transition);
}

.step-line.active {
  background: var(--color-primary);
}

/* ---- Main ---- */
.app-main {
  max-width: 1360px;
  margin: 0 auto;
  padding: 24px;
}

/* ---- Grid ---- */
.content-grid {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.col-left {
  width: 360px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 76px;
}

.col-right {
  flex: 1;
  min-width: 0;
}

/* ---- Card ---- */
.card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

/* ---- Generate Button ---- */
.btn-generate {
  width: 100%;
  height: 46px;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: #fff;
  font-family: inherit;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition);
  letter-spacing: 0.5px;
}

.btn-generate:hover:not(.disabled) {
  background: #0E7490;
}

.btn-generate:active:not(.disabled) {
  transform: scale(0.98);
}

.btn-generate.disabled {
  background: var(--color-border);
  color: var(--color-text-muted);
  cursor: not-allowed;
}

.btn-generate.loading {
  opacity: 0.8;
  cursor: wait;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ---- Element Plus overrides ---- */
.el-card {
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--color-border) !important;
  box-shadow: none !important;
}

.el-card .el-card__header {
  border-bottom: 1px solid var(--color-border);
  padding: 14px 20px;
  background: transparent;
}

.el-card .el-card__body {
  padding: 20px;
}

.el-table {
  --el-table-border-color: var(--color-border);
  --el-table-header-bg-color: var(--color-bg);
  font-size: 13px;
}

.el-table th.el-table__cell {
  font-weight: 600 !important;
  color: var(--color-text-secondary) !important;
  font-size: 12px !important;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.el-input__wrapper, .el-input-number {
  border-radius: var(--radius) !important;
}

.el-form-item__label {
  font-size: 12px !important;
  font-weight: 500 !important;
  color: var(--color-text-secondary) !important;
}

.el-upload-dragger {
  border-radius: var(--radius) !important;
  border-color: var(--color-border) !important;
  transition: border-color var(--transition);
}

.el-upload-dragger:hover {
  border-color: var(--color-primary) !important;
}

.el-tag {
  border-radius: 20px !important;
}

.el-button--primary {
  background-color: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
}

/* ---- Responsive ---- */
@media (max-width: 900px) {
  .content-grid {
    flex-direction: column;
  }
  .col-left {
    width: 100%;
    position: static;
  }
  .steps {
    margin-bottom: 20px;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0s !important;
    animation-duration: 0s !important;
  }
}
</style>
