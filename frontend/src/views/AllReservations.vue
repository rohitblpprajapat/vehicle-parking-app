<template>
    <div class="all-reservations">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>All Reservations</h3>
            </div>
            <div class="nav-links">
                <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/admin/parking-lots" class="nav-link">Manage Lots</router-link>
                <router-link to="/admin/users" class="nav-link">Manage Users</router-link>
                <router-link to="/admin/reservations" class="nav-link">All Reservations</router-link>
                <router-link to="/admin/summary" class="nav-link">Analytics</router-link>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="content">
            <div class="container">
                <div class="header">
                    <h1>All Reservations</h1>
                    <div class="filters">
                        <select v-model="selectedStatus" @change="fetchReservations" class="filter-select">
                            <option value="">All Statuses</option>
                            <option value="active">Active</option>
                            <option value="completed">Completed</option>
                            <option value="cancelled">Cancelled</option>
                        </select>
                        <input v-model="searchEmail" @input="debouncedSearch" placeholder="Search by user email..."
                            class="search-input">
                    </div>
                </div>

                <!-- Stats Cards -->
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">📊</div>
                        <div class="stat-content">
                            <span class="stat-value">{{ totalCount }}</span>
                            <span class="stat-label">Total Reservations</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🔄</div>
                        <div class="stat-content">
                            <span class="stat-value">{{ activeCount }}</span>
                            <span class="stat-label">Active</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">✅</div>
                        <div class="stat-content">
                            <span class="stat-value">{{ completedCount }}</span>
                            <span class="stat-label">Completed</span>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">❌</div>
                        <div class="stat-content">
                            <span class="stat-value">{{ cancelledCount }}</span>
                            <span class="stat-label">Cancelled</span>
                        </div>
                    </div>
                </div>

                <!-- Loading State -->
                <div v-if="loading" class="loading">
                    Loading reservations...
                </div>

                <!-- Error State -->
                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <!-- Reservations Table -->
                <div v-if="!loading && !error" class="table-container">
                    <table class="reservations-table">
                        <thead>
                            <tr>
                                <th style="width: 15%;">User</th>
                                <th style="width: 20%;">Parking Lot</th>
                                <th style="width: 10%;">Spot</th>
                                <th style="width: 15%;">Start Time</th>
                                <th style="width: 15%;">End Time</th>
                                <th style="width: 10%;">Status</th>
                                <th style="width: 15%;">Booked On</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="reservation in reservations" :key="reservation.id">
                                <td>
                                    <div class="user-info">
                                        <div class="user-name">{{ reservation.user.name }}</div>
                                        <div class="user-email">{{ reservation.user.email }}</div>
                                    </div>
                                </td>
                                <td>
                                    <div class="lot-info">
                                        <div class="lot-name">{{ reservation.parking_lot.name }}</div>
                                        <div class="lot-location">{{ reservation.parking_lot.location }}</div>
                                    </div>
                                </td>
                                <td class="spot-number">{{ reservation.parking_spot.spot_number }}</td>
                                <td class="datetime">{{ formatDateTime(reservation.start_time) }}</td>
                                <td class="datetime">{{ formatDateTime(reservation.end_time) }}</td>
                                <td>
                                    <span :class="['status-badge', reservation.status]">
                                        {{ reservation.status }}
                                    </span>
                                </td>
                                <td class="datetime">{{ formatDateTime(reservation.created_at) }}</td>
                            </tr>
                        </tbody>
                    </table>

                    <!-- Pagination -->
                    <div v-if="totalCount > limit" class="pagination">
                        <button @click="previousPage" :disabled="offset === 0" class="btn btn-secondary">
                            Previous
                        </button>
                        <span class="pagination-info">
                            Showing {{ offset + 1 }} - {{ Math.min(offset + limit, totalCount) }} of {{ totalCount }}
                        </span>
                        <button @click="nextPage" :disabled="offset + limit >= totalCount" class="btn btn-secondary">
                            Next
                        </button>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const reservations = ref([])
const totalCount = ref(0)
const selectedStatus = ref('')
const searchEmail = ref('')
const limit = ref(20)
const offset = ref(0)

// Stats computed properties
const activeCount = computed(() => reservations.value.filter(r => r.status === 'active').length)
const completedCount = computed(() => reservations.value.filter(r => r.status === 'completed').length)
const cancelledCount = computed(() => reservations.value.filter(r => r.status === 'cancelled').length)

let searchTimeout = null

const fetchReservations = async () => {
    try {
        loading.value = true
        error.value = ''

        const token = localStorage.getItem('authToken')
        if (!token) {
            router.push('/login')
            return
        }

        // Build query parameters
        const params = new URLSearchParams({
            limit: limit.value.toString(),
            offset: offset.value.toString()
        })

        if (selectedStatus.value) {
            params.append('status', selectedStatus.value)
        }

        const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/reservations?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            reservations.value = data.reservations
            totalCount.value = data.total_count

            // Filter by email on frontend if search is active
            if (searchEmail.value) {
                reservations.value = reservations.value.filter(reservation =>
                    reservation.user.email.toLowerCase().includes(searchEmail.value.toLowerCase()) ||
                    reservation.user.name.toLowerCase().includes(searchEmail.value.toLowerCase())
                )
            }
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to fetch reservations'

            if (response.status === 401 || response.status === 403) {
                router.push('/login')
            }
        }
    } catch (err) {
        console.error('Fetch error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        loading.value = false
    }
}

const debouncedSearch = () => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
        offset.value = 0 // Reset to first page when searching
        fetchReservations()
    }, 300)
}

const previousPage = () => {
    if (offset.value > 0) {
        offset.value = Math.max(0, offset.value - limit.value)
        fetchReservations()
    }
}

const nextPage = () => {
    if (offset.value + limit.value < totalCount.value) {
        offset.value += limit.value
        fetchReservations()
    }
}

const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString()
}

const logout = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('userEmail')
    router.push('/login')
}

onMounted(() => {
    fetchReservations()
})
</script>

<style scoped>
.all-reservations {
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

.content {
    padding: 2rem;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.header h1 {
    margin: 0;
    color: #333;
}

.filters {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.filter-select,
.search-input {
    padding: 0.5rem 1rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 0.9rem;
}

.search-input {
    min-width: 250px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    gap: 1rem;
}

.stat-icon {
    font-size: 2rem;
    width: 50px;
    text-align: center;
}

.stat-content {
    flex: 1;
}

.stat-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #667eea;
}

.stat-label {
    display: block;
    font-size: 0.85rem;
    color: #6c757d;
}

.loading,
.error-message {
    text-align: center;
    padding: 1rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.error-message {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.table-container {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e9ecef;
}

.reservations-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}

.reservations-table th,
.reservations-table td {
    padding: 1rem 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
}

.reservations-table th {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    font-weight: 700;
    color: #495057;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.reservations-table tbody tr:hover {
    background-color: #f8f9fa;
}

.user-info,
.lot-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.user-name,
.lot-name {
    font-weight: 600;
    color: #2c3e50;
    font-size: 0.9rem;
}

.user-email,
.lot-location {
    color: #6c757d;
    font-size: 0.8rem;
}

.spot-number {
    font-weight: 600;
    color: #495057;
    text-align: center;
    background: #f8f9fa;
    font-family: monospace;
}

.datetime {
    color: #495057;
    font-size: 0.8rem;
    white-space: nowrap;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.active {
    background: #fff3cd;
    color: #856404;
}

.status-badge.completed {
    background: #d4edda;
    color: #155724;
}

.status-badge.cancelled {
    background: #f8d7da;
    color: #721c24;
}

.pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
}

.pagination-info {
    color: #6c757d;
    font-size: 0.9rem;
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
    font-size: 0.9rem;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-logout {
    background: #dc3545;
    color: white;
}

.btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}
</style>
