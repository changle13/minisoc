<template>
  <div>
    <div class="page-header">
      <div>
        <h2>响应记录</h2>
        <p class="muted">自动响应 Agent 的封禁与解封审计</p>
      </div>
      <el-button @click="load">刷新</el-button>
    </div>

    <el-card>
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        :closable="false"
        show-icon
        class="mb"
      />

      <el-table
        v-loading="loading"
        :data="actions"
        empty-text="暂无响应记录"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="alert_id" label="Alert ID" width="100" />
        <el-table-column prop="action" label="动作" width="100" />
        <el-table-column prop="target_ip" label="目标 IP" min-width="150" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时间" min-width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="详情" min-width="300">
          <template #default="{ row }">
            <span class="detail-text">{{ row.detail || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="load"
          @size-change="onSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

import { fetchActions } from '../api/client'

const actions = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const error = ref('')

function statusType(value) {
  if (['blocked', 'unblocked', 'already_blocked'].includes(value)) return 'success'
  if (value === 'error') return 'danger'
  return 'info'
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString() : '-'
}

function onSizeChange() {
  page.value = 1
  load()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchActions({
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
    })
    actions.value = data.items
    total.value = data.total
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
