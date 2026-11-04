<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <div class="login-title">MiniSOC</div>
        <div class="login-subtitle">轻量级安全运营与应急响应平台</div>
      </template>

      <el-form @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input
            v-model="form.username"
            placeholder="admin"
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="请输入密码"
            autocomplete="current-password"
            @keyup.enter="onSubmit"
          />
        </el-form-item>

        <el-alert
          v-if="error"
          :title="error"
          type="error"
          :closable="false"
          show-icon
          class="mb"
        />

        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="login-button"
        >
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { login } from '../api/client'
import { setToken, setUser } from '../auth'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function onSubmit() {
  if (!form.username || !form.password) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  error.value = ''
  try {
    const data = await login(form.username, form.password)
    setToken(data.access_token)
    setUser(form.username)
    ElMessage.success('登录成功')
    router.push('/alerts')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
