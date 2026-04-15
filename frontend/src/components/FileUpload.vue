<template>
  <section class="card">
    <h3 class="card-title">上传清单</h3>
    <el-upload
      drag
      action="/api/upload"
      accept=".xlsx,.xls"
      :show-file-list="false"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
    >
      <div class="upload-body" v-if="!fileName">
        <svg class="upload-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="17 8 12 3 7 8"/>
          <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <p class="upload-text">拖拽文件到此处，或<span>点击上传</span></p>
        <p class="upload-hint">支持 .xlsx 格式</p>
      </div>
      <div class="upload-done" v-else>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <div class="upload-done-info">
          <p class="upload-done-name">{{ fileName }}</p>
          <p class="upload-done-count">{{ itemCount }} 条物料已解析</p>
        </div>
        <span class="upload-replace">重新上传</span>
      </div>
    </el-upload>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['materials-loaded'])
const fileName = ref('')
const itemCount = ref(0)

function beforeUpload(file) {
  const isXlsx = file.name.endsWith('.xlsx') || file.name.endsWith('.xls')
  if (!isXlsx) {
    ElMessage.error('请上传 .xlsx 格式文件')
    return false
  }
  return true
}

function handleSuccess(response, file) {
  fileName.value = file.name
  itemCount.value = response.materials.length
  emit('materials-loaded', response.materials)
}

function handleError() {
  ElMessage.error('上传失败，请重试')
}
</script>

<style scoped>
.upload-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 0;
}

.upload-icon {
  color: var(--color-text-muted);
}

.upload-text {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.upload-text span {
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 500;
}

.upload-hint {
  font-size: 12px;
  color: var(--color-text-muted);
}

.upload-done {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 4px;
  color: var(--color-success);
}

.upload-done-info {
  flex: 1;
}

.upload-done-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

.upload-done-count {
  font-size: 12px;
  color: var(--color-success);
  margin-top: 2px;
}

.upload-replace {
  font-size: 12px;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: color 150ms ease;
}

.upload-replace:hover {
  color: var(--color-primary);
}
</style>
