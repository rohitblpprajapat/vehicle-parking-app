import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import ParkingLots from '../views/ParkingLots.vue'
import Reservations from '../views/Reservations.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import ManageParkingLots from '../views/ManageParkingLots.vue'
import ParkingLotDetails from '../views/ParkingLotDetails.vue'
import ManageUsers from '../views/ManageUsers.vue'
import AllReservations from '../views/AllReservations.vue'
import UserProfile from '../views/UserProfile.vue'
import AdminSummary from '../views/AdminSummary.vue'
import { isAuthenticated, isAdmin } from '../utils/auth.js'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, userOnly: true }
  },
  {
    path: '/parking-lots',
    name: 'ParkingLots',
    component: ParkingLots,
    meta: { requiresAuth: true }
  },
  {
    path: '/reservations',
    name: 'Reservations',
    component: Reservations,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: { requiresAuth: true, userOnly: true }
  },
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/parking-lots',
    name: 'ManageParkingLots',
    component: ManageParkingLots,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/parking-lots/:id',
    name: 'ParkingLotDetails',
    component: ParkingLotDetails,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'ManageUsers',
    component: ManageUsers,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/reservations',
    name: 'AllReservations',
    component: AllReservations,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/summary',
    name: 'AdminSummary',
    component: AdminSummary,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for authentication and authorization
router.beforeEach((to, from, next) => {
  const authenticated = isAuthenticated()
  const adminUser = isAdmin()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authenticated) {
    next('/login')
    return
  }
  
  // Check if route requires admin access
  if (to.meta.requiresAdmin && !adminUser) {
    console.warn('Access denied: Admin privileges required')
    next('/dashboard') // Redirect regular users to their dashboard
    return
  }
  
  // Check if route is for regular users only (non-admin)
  if (to.meta.userOnly && adminUser) {
    next('/admin/dashboard') // Redirect admins to admin dashboard
    return
  }
  
  // Check if route is for guests only (login page)
  if (to.meta.guestOnly && authenticated) {
    // Redirect authenticated users based on their role
    if (adminUser) {
      next('/admin/dashboard')
    } else {
      next('/dashboard')
    }
    return
  }
  
  next()
})

export default router
