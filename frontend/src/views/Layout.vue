<template>
  <el-container class="layout">
    <el-aside width="220px" class="sidebar">
      <div class="brand">MiniSOC</div>
      <el-menu :default-active="activeMenu" router class="menu">
        <el-menu-item index="/alerts">告警中心</el-menu-item>
        <el-menu-item index="/incidents">事件工单</el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">安全运营平台</div>
        <div class="header-user">
          <span>{{ username }}</span>
          <el-button link type="primary" @click="logout">退出</el-button>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { clearAuth, getUser } from '../auth'

const route = useRoute()
const router = useRouter()
const username = getUser() || 'unknown'

const activeMenu = computed(() => {
  if (route.path.startsWith('/alerts')) return '/alerts'
  if (route.path.startsWith('/incidents')) return '/incidents'
  return route.path
})

function logout() {
  clearAuth()
  router.push('/login')
}
</script>
