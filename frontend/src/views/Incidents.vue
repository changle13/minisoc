<template>
  <div>
    <div class="page-header">
      <div>
        <h2>事件工单</h2>
        <p class="muted">多条相关告警合并成的安全事件</p>
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
        :data="incidents"
        empty-text="暂无事件工单"
        class="clickable-table"
        @row-click="openIncident"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" min-width="260" />
        <el-table-column label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110" />
        <el-table-column label="负责人" width="120">
          <template #default="{ row }">
            {{ row.assignee || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
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
import { useRouter } from 'vue-router'

import { fetchIncidents } from '../api/client'

const router = useRouter()
const incidents = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const error = ref('')

function severityType(value) {
  return { high: 'danger', medium: 'warning', low: 'info' }[value] || 'info'
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString() : '-'
}

function openIncident(row) {
  router.push(`/incidents/${row.id}`)
}

function onSizeChange() {
  page.value = 1
  load()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchIncidents({
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
    })
    incidents.value = data.items
    total.value = data.total
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
