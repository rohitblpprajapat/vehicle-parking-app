<template>
  <div class="min-vh-100 bg-light">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-success shadow-sm">
      <div class="container">
        <router-link to="/dashboard" class="navbar-brand fw-bold">
          Vehicle Parking
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <!-- Admin Links -->
            <template v-if="isAdmin">
              <li class="nav-item">
                <router-link to="/admin/dashboard" class="nav-link" active-class="active">Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/admin/parking-lots" class="nav-link" active-class="active">Manage Lots</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/admin/reservations" class="nav-link" active-class="active">Reservations</router-link>
              </li>
            </template>
            <!-- User Links -->
            <template v-else>
              <li class="nav-item">
                <router-link to="/dashboard" class="nav-link" active-class="active">Dashboard</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/parking-lots" class="nav-link" active-class="active">Find Parking</router-link>
              </li>
              <li class="nav-item">
                <router-link to="/reservations" class="nav-link" active-class="active">My Reservations</router-link>
              </li>
            </template>
          </ul>
          
          <ul class="navbar-nav ms-auto align-items-center">
            <template v-if="userInfo.name">
                <li class="nav-item me-3 text-white-50">
                Welcome, {{ userInfo.name }}
                </li>
                <li class="nav-item">
                <router-link to="/profile" class="nav-link" active-class="active">Profile</router-link>
                </li>
                <li class="nav-item ms-2">
                <button @click="logout" class="btn btn-outline-light btn-sm">Logout</button>
                </li>
            </template>
            <template v-else>
                <li class="nav-item">
                    <router-link to="/login" class="nav-link">Login</router-link>
                </li>
                <li class="nav-item ms-2">
                    <router-link to="/register" class="btn btn-outline-light btn-sm">Sign Up</router-link>
                </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="container py-4">
      <slot></slot>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { logout as authLogout, getUserInfo, isAdmin as checkIsAdmin } from '../../utils/auth.js'

const router = useRouter()
const userInfo = ref(getUserInfo() || {})
const isAdmin = computed(() => checkIsAdmin())

const logout = () => {
  authLogout()
  router.push('/login')
}
</script>

<style scoped>
.navbar-brand {
  font-size: 1.25rem;
}
</style>
