<template>
    <div class="dashboard">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Parking Dashboard</h3>
            </div>
            <div class="nav-links">
                <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/parking-lots" class="nav-link">Parking Lots</router-link>
                <router-link to="/reservations" class="nav-link">My Reservations</router-link>
                <span class="user-info">Welcome, {{ userInfo.name }}</span>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="dashboard-content">
            <div class="container">
                <h1>Welcome to Your Dashboard</h1>

                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Available Spots</h3>
                        <p class="stat-number">{{ availableSpots }}</p>
                    </div>
                    <div class="stat-card">
                        <h3>My Reservations</h3>
                        <p class="stat-number">{{ myReservations }}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Total Parking Lots</h3>
                        <p class="stat-number">{{ totalLots }}</p>
                    </div>
                </div>

                <div class="quick-actions">
                    <h2>Quick Actions</h2>
                    <div class="action-buttons">
                        <router-link to="/parking-lots" class="btn btn-primary">Find Parking</router-link>
                        <router-link to="/reservations" class="btn btn-secondary">View Reservations</router-link>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { logout as authLogout, getUserInfo } from '../utils/auth.js'

const router = useRouter()
const userInfo = ref({})

// Reactive data
const availableSpots = ref(42)
const myReservations = ref(3)
const totalLots = ref(8)

// Get user info
userInfo.value = getUserInfo()

// Logout function
const logout = () => {
    authLogout()
    router.push('/login')
}

onMounted(() => {
    // Fetch dashboard data here
    console.log('Dashboard mounted')
})
</script>

<style scoped>
.dashboard {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.navbar {
    background: white;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand h3 {
    color: #667eea;
    margin: 0;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.user-info {
    color: #333;
    font-weight: 500;
    background-color: #f8f9fa;
    padding: 0.5rem 1rem;
    border-radius: 4px;
}

.nav-link {
    text-decoration: none;
    color: #333;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
    background-color: #667eea;
    color: white;
}

.btn-logout {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}

.btn-logout:hover {
    background-color: #c82333;
}

.dashboard-content {
    padding: 2rem;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.dashboard-content h1 {
    margin-bottom: 2rem;
    color: #333;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.stat-card h3 {
    color: #666;
    margin-bottom: 1rem;
    font-size: 1rem;
}

.stat-number {
    font-size: 2.5rem;
    font-weight: bold;
    color: #667eea;
    margin: 0;
}

.quick-actions h2 {
    margin-bottom: 1rem;
    color: #333;
}

.action-buttons {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.btn {
    padding: 12px 24px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.btn-primary {
    background-color: #667eea;
    color: white;
}

.btn-primary:hover {
    background-color: #5a67d8;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #5a6268;
}
</style>
