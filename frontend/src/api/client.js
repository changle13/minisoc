import { clearAuth, getToken } from '../auth'

function buildQuery(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, value)
    }
  })
  const query = search.toString()
  return query ? `?${query}` : ''
}

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  const token = getToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`/api/v1${path}`, { ...options, headers })
  const data = await response.json().catch(() => ({}))

  if (response.status === 401) {
    clearAuth()
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
    throw new Error('登录已过期，请重新登录')
  }

  if (!response.ok) {
    throw new Error(data.detail || `HTTP ${response.status}`)
  }

  return data
}

export function login(username, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
}

export function fetchAlerts(params) {
  return request(`/alerts${buildQuery(params)}`)
}

export function fetchAlert(id) {
  return request(`/alerts/${id}`)
}

export function fetchIncidents(params) {
  return request(`/incidents${buildQuery(params)}`)
}

export function fetchIncident(id) {
  return request(`/incidents/${id}`)
}
