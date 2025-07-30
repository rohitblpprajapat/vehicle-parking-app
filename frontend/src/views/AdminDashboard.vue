<template>
    <div class="admin-dashboard">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Admin Dashboard</h3>
            </div>
            <div class="nav-links">
                <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/admin/parking-lots" class="nav-link">Manage Lots</router-link>
                <router-link to="/admin/users" class="nav-link">Manage Users</router-link>
                <router-link to="/admin/reservations" class="nav-link">All Reservations</router-link>
                <router-link to="/admin/summary" class="nav-link">Analytics</router-link>
                <span class="user-info">Welcome, {{ userInfo.name }}</span>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="dashboard-content">
            <div class="container">
                <h1>Admin Dashboard</h1>

                <!-- Loading State -->
                <div v-if="loading" class="loading">
                    Loading dashboard data...
                </div>

                <!-- Error State -->
                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <!-- Dashboard Content -->
                <div v-if="!loading && !error && dashboardData">
                    <!-- Summary Cards -->
                    <div class="stats-grid">
                        <div class="stat-card parking">
                            <h3>Total Parking Lots</h3>
                            <p class="stat-number">{{ dashboardData.summary.total_parking_lots }}</p>
                        </div>
                        <div class="stat-card spots">
                            <h3>Total Spots</h3>
                            <p class="stat-number">{{ dashboardData.summary.total_spots }}</p>
                        </div>
                        <div class="stat-card occupied">
                            <h3>Occupied Spots</h3>
                            <p class="stat-number">{{ dashboardData.summary.occupied_spots }}</p>
                        </div>
                        <div class="stat-card available">
                            <h3>Available Spots</h3>
                            <p class="stat-number">{{ dashboardData.summary.available_spots }}</p>
                        </div>
                        <div class="stat-card users">
                            <h3>Total Users</h3>
                            <p class="stat-number">{{ dashboardData.summary.total_users }}</p>
                        </div>
                        <div class="stat-card active-users">
                            <h3>Active Users</h3>
                            <p class="stat-number">{{ dashboardData.summary.active_users }}</p>
                        </div>
                        <div class="stat-card reservations">
                            <h3>Total Reservations</h3>
                            <p class="stat-number">{{ dashboardData.summary.total_reservations }}</p>
                        </div>
                        <div class="stat-card active-reservations">
                            <h3>Active Reservations</h3>
                            <p class="stat-number">{{ dashboardData.summary.active_reservations }}</p>
                        </div>
                    </div>

                    <!-- Quick Management Actions -->
                    <div class="management-section">
                        <h2>Management Tools</h2>
                        <div class="management-grid">
                            <router-link to="/admin/parking-lots" class="management-card">
                                <div class="card-icon">🏗️</div>
                                <h3>Manage Parking Lots</h3>
                                <p>Create, edit, and delete parking lots</p>
                            </router-link>
                            <router-link to="/admin/users" class="management-card">
                                <div class="card-icon">👥</div>
                                <h3>Manage Users</h3>
                                <p>View users and control account status</p>
                            </router-link>
                            <router-link to="/admin/reservations" class="management-card">
                                <div class="card-icon">📅</div>
                                <h3>All Reservations</h3>
                                <p>Monitor all booking activities</p>
                            </router-link>
                        </div>
                    </div>

                    <!-- Parking Lots Overview -->
                    <div class="parking-lots-section">
                        <div class="section-header">
                            <h2>Parking Lots Overview</h2>
                            <router-link to="/admin/parking-lots" class="btn btn-primary">
                                Manage Parking Lots
                            </router-link>
                        </div>

                        <div class="lots-grid">
                            <div v-for="lot in dashboardData.parking_lots" :key="lot.id" class="lot-card">
                                <div class="lot-header">
                                    <h3>{{ lot.name }}</h3>
                                    <span class="price">${{ lot.price_per_hour }}/hour</span>
                                </div>
                                <p class="location">{{ lot.location }}</p>

                                <div class="lot-stats">
                                    <div class="stat">
                                        <span class="label">Capacity:</span>
                                        <span class="value">{{ lot.capacity }}</span>
                                    </div>
                                    <div class="stat">
                                        <span class="label">Available:</span>
                                        <span class="value">{{ lot.available_spots }}</span>
                                    </div>
                                    <div class="stat">
                                        <span class="label">Occupied:</span>
                                        <span class="value">{{ lot.occupied_spots }}</span>
                                    </div>
                                    <div class="stat">
                                        <span class="label">Occupancy:</span>
                                        <span class="value">{{ lot.occupancy_rate.toFixed(1) }}%</span>
                                    </div>
                                </div>

                                <div class="occupancy-bar">
                                    <div class="occupancy-fill" :style="{ width: lot.occupancy_rate + '%' }"></div>
                                </div>

                                <div class="lot-actions">
                                    <router-link :to="`/admin/parking-lots/${lot.id}`" class="btn btn-secondary">
                                        View Details
                                    </router-link>
                                </div>
                            </div>
                        </div>
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
const loading = ref(true)
const error = ref('')
const dashboardData = ref(null)

// Get user info
userInfo.value = getUserInfo()

// Logout function
const logout = () => {
    authLogout()
    router.push('/login')
}

const fetchDashboardData = async () => {
    try {
        loading.value = true
        error.value = ''

        const token = localStorage.getItem('authToken')
        if (!token) {
            router.push('/login')
            return
        }

        const response = await fetch('http://127.0.0.1:5000/api/v1/admin/dashboard', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            dashboardData.value = await response.json()
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to fetch dashboard data'

            if (response.status === 401 || response.status === 403) {
                router.push('/login')
            }
        }
    } catch (err) {
        console.error('Dashboard fetch error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchDashboardData()
})
</script>

<style scoped>
.admin-dashboard {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-brand h3 {
    margin: 0;
    font-size: 1.5rem;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.user-info {
    color: white;
    font-weight: 500;
    background-color: rgba(255, 255, 255, 0.1);
    padding: 0.5rem 1rem;
    border-radius: 4px;
}

.nav-link {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
    background-color: rgba(255, 255, 255, 0.2);
}

.dashboard-content {
    padding: 2rem;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.loading,
.error-message {
    text-align: center;
    padding: 2rem;
    font-size: 1.1rem;
}

.error-message {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    padding: 1.25rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
    border-left: 4px solid #667eea;
    transition: transform 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-card.parking {
    border-left-color: #667eea;
}

.stat-card.spots {
    border-left-color: #28a745;
}

.stat-card.occupied {
    border-left-color: #dc3545;
}

.stat-card.available {
    border-left-color: #28a745;
}

.stat-card.users {
    border-left-color: #17a2b8;
}

.stat-card.active-users {
    border-left-color: #20c997;
}

.stat-card.reservations {
    border-left-color: #ffc107;
}

.stat-card.active-reservations {
    border-left-color: #fd7e14;
}

.stat-card h3 {
    color: #6c757d;
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: uppercase;
}

.stat-number {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
    margin: 0;
}

.parking-lots-section {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-header h2 {
    margin: 0;
    color: #333;
}

.lots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.lot-card {
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1.5rem;
    background: #f8f9fa;
}

.lot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.lot-header h3 {
    margin: 0;
    color: #333;
    font-size: 1.2rem;
}

.price {
    background: #28a745;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.9rem;
    font-weight: bold;
}

.location {
    color: #6c757d;
    margin: 0 0 1rem 0;
}

.lot-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.stat {
    display: flex;
    justify-content: space-between;
}

.stat .label {
    color: #6c757d;
    font-size: 0.9rem;
}

.stat .value {
    font-weight: bold;
    color: #333;
}

.occupancy-bar {
    background: #e9ecef;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.occupancy-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745 0%, #ffc107 70%, #dc3545 100%);
    transition: width 0.3s ease;
}

.lot-actions {
    text-align: center;
}

.btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 500;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-logout {
    background: #dc3545;
    color: white;
}

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Management Section Styles */
.management-section {
    margin-bottom: 3rem;
}

.management-section h2 {
    margin: 0 0 1.5rem 0;
    color: #333;
}

.management-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

.management-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-decoration: none;
    color: inherit;
    transition: all 0.3s ease;
    border: 1px solid #e9ecef;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.management-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    border-color: #667eea;
}

.management-card .card-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 50%;
}

.management-card h3 {
    margin: 0 0 0.75rem 0;
    color: #2c3e50;
    font-size: 1.25rem;
}

.management-card p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
    line-height: 1.4;
}
</style>
