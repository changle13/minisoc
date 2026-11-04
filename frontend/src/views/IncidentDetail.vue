<template>
  <div>
    <div class="page-header">
      <div>
        <el-button link type="primary" @click="router.back()">← 返回</el-button>
        <h2>事件工单 #{{ incident?.id || '' }}</h2>
      </div>
    </div>

    <el-alert
      v-if="error"
      :title="error"
      type="error"
      :closable="false"
      show-icon
      class="mb"
    />

    <el-card v-loading="loading">
      <template v-if="incident">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="标题" :span="3">
            {{ incident.title }}
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="severityType(incident.severity)">
              {{ incident.severity }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            {{ incident.status }}
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ incident.assignee || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(incident.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatTime(incident.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <h3 class="section-title">关联告警</h3>
        <el-table
          :data="incident.alerts"
          empty-text="没有关联告警"
          class="clickable-table"
          @row-click="openAlert"
        >
          <el-table-column prop="id" label="Alert ID" width="100" />
          <el-table-column prop="rule_name" label="规则" min-width="180" />
          <el-table-column label="级别" width="100">
            <template #default="{ row }">
              <el-tag :type="severityType(row.severity)">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="entity" label="实体" min-width="150" />
          <el-table-column prop="count" label="次数" width="80" />
          <el-table-column label="最后出现" min-width="170">
            <template #default="{ row }">
              {{ formatTime(row.last_seen) }}
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchIncident } from '../api/client'

const route = useRoute()
const router = useRouter()
const incident = ref(null)
const loading = ref(false)
const error = ref('')

function severityType(value) {
  return { high: 'danger', medium: 'warning', low: 'info' }[value] || 'info'
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString() : '-'
}

function openAlert(row) {
  router.push(`/alerts/${row.id}`)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    incident.value = await fetchIncident(route.params.id)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
