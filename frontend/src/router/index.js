import { createRouter, createWebHistory } from 'vue-router'

import { isLoggedIn } from '../auth'
import AlertDetail from '../views/AlertDetail.vue'
import Alerts from '../views/Alerts.vue'
import IncidentDetail from '../views/IncidentDetail.vue'
import Incidents from '../views/Incidents.vue'
import Layout from '../views/Layout.vue'
import Login from '../views/Login.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login },
    {
      path: '/',
      component: Layout,
      redirect: '/alerts',
      children: [
        { path: 'alerts', name: 'alerts', component: Alerts },
        { path: 'alerts/:id', name: 'alert-detail', component: AlertDetail },
        { path: 'incidents', name: 'incidents', component: Incidents },
        {
          path: 'incidents/:id',
          name: 'incident-detail',
          component: IncidentDetail,
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.name !== 'login' && !isLoggedIn()) {
    return { name: 'login' }
  }
  if (to.name === 'login' && isLoggedIn()) {
    return { name: 'alerts' }
  }
})

export default router
