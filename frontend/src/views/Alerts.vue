<template>
  <div>
    <div class="page-header">
      <div>
        <h2>告警中心</h2>
        <p class="muted">检测规则命中的安全告警</p>
      </div>
      <el-button @click="load">刷新</el-button>
    </div>

    <el-card>
      <div class="filters">
        <el-select
          v-model="filters.severity"
          placeholder="严重级别"
          clearable
          style="width: 160px"
          @change="onFilterChange"
        >
          <el-option label="高危" value="high" />
          <el-option label="中危" value="medium" />
          <el-option label="低危" value="low" />
        </el-select>

        <el-select
          v-model="filters.status"
          placeholder="状态"
          clearable
          style="width: 160px"
          @change="onFilterChange"
        >
          <el-option label="未处理" value="open" />
          <el-option label="已确认" value="acknowledged" />
          <el-option label="已关闭" value="closed" />
        </el-select>
      </div>

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
        :data="alerts"
        empty-text="暂无告警"
        class="clickable-table"
        @row-click="openAlert"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="rule_name" label="规则" min-width="180" />
        <el-table-column label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="severityType(row.severity)">
              {{ severityLabel(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entity" label="实体" min-width="150" />
        <el-table-column prop="count" label="次数" width="80" />
        <el-table-column prop="status" label="状态" width="110" />
        <el-table-column label="最后出现" min-width="170">
          <template #default="{ row }">
            {{ formatTime(row.last_seen) }}
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
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { fetchAlerts } from '../api/client'

const router = useRouter()
const alerts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const error = ref('')
const filters = reactive({ severity: '', status: '' })

function severityType(value) {
  return { high: 'danger', medium: 'warning', low: 'info' }[value] || 'info'
}

function severityLabel(value) {
  return { high: '高危', medium: '中危', low: '低危' }[value] || value
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString() : '-'
}

function openAlert(row) {
  router.push(`/alerts/${row.id}`)
}

function onFilterChange() {
  page.value = 1
  load()
}

function onSizeChange() {
  page.value = 1
  load()
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchAlerts({
      severity: filters.severity,
      status: filters.status,
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
    })
    alerts.value = data.items
    total.value = data.total
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
