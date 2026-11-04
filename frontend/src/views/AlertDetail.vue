<template>
  <div>
    <div class="page-header">
      <div>
        <el-button link type="primary" @click="router.back()">← 返回</el-button>
        <h2>告警详情 #{{ alert?.id || '' }}</h2>
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
      <template v-if="alert">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="规则">
            {{ alert.rule_name }}
          </el-descriptions-item>
          <el-descriptions-item label="规则 ID">
            {{ alert.rule_id }}
          </el-descriptions-item>
          <el-descriptions-item label="级别">
            <el-tag :type="severityType(alert.severity)">
              {{ alert.severity }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实体">
            {{ alert.entity }}
          </el-descriptions-item>
          <el-descriptions-item label="次数">
            {{ alert.count }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            {{ alert.status }}
          </el-descriptions-item>
          <el-descriptions-item label="首次出现">
            {{ formatTime(alert.first_seen) }}
          </el-descriptions-item>
          <el-descriptions-item label="最后出现">
            {{ formatTime(alert.last_seen) }}
          </el-descriptions-item>
        </el-descriptions>

        <h3 class="section-title">原始证据</h3>
        <el-table :data="alert.events" empty-text="没有关联证据">
          <el-table-column prop="id" label="Event ID" width="100" />
          <el-table-column label="时间" min-width="170">
            <template #default="{ row }">
              {{ formatTime(row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="username" label="用户" width="100" />
          <el-table-column prop="src_ip" label="来源 IP" width="140" />
          <el-table-column prop="process" label="进程" width="100" />
          <el-table-column label="类型" width="120">
            <template #default="{ row }">
              {{ row.raw?.event_type || '-' }}
            </template>
          </el-table-column>
          <el-table-column
            prop="command_line"
            label="原始日志"
            min-width="300"
          />
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchAlert } from '../api/client'

const route = useRoute()
const router = useRouter()
const alert = ref(null)
const loading = ref(false)
const error = ref('')

function severityType(value) {
  return { high: 'danger', medium: 'warning', low: 'info' }[value] || 'info'
}

function formatTime(value) {
  return value ? new Date(value).toLocaleString() : '-'
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    alert.value = await fetchAlert(route.params.id)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
