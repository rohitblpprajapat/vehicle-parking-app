<template>
    <div class="manage-users">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Manage Users</h3>
            </div>
            <div class="nav-links">
                <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/admin/parking-lots" class="nav-link">Manage Lots</router-link>
                <router-link to="/admin/users" class="nav-link">Manage Users</router-link>
                <router-link to="/admin/reservations" class="nav-link">All Reservations</router-link>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="content">
            <div class="container">
                <div class="header">
                    <h1>User Management</h1>
                    <div class="header-stats">
                        <div class="stat-card">
                            <span class="stat-value">{{ users.length }}</span>
                            <span class="stat-label">Total Users</span>
                        </div>
                        <div class="stat-card">
                            <span class="stat-value">{{ activeUsersCount }}</span>
                            <span class="stat-label">Active Users</span>
                        </div>
                    </div>
                </div>

                <!-- Loading State -->
                <div v-if="loading" class="loading">
                    Loading users...
                </div>

                <!-- Error State -->
                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <!-- Success Message -->
                <div v-if="successMessage" class="success-message">
                    {{ successMessage }}
                </div>

                <!-- Users Table -->
                <div v-if="!loading && !error" class="table-container">
                    <table class="users-table">
                        <thead>
                            <tr>
                                <th style="width: 20%;">Name</th>
                                <th style="width: 25%;">Email</th>
                                <th style="width: 10%;">Status</th>
                                <th style="width: 15%;">Roles</th>
                                <th style="width: 10%; text-align: center;">Total Bookings</th>
                                <th style="width: 10%; text-align: center;">Active Bookings</th>
                                <th style="width: 20%; text-align: center;">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="user in users" :key="user.id">
                                <td class="user-name">{{ user.name }}</td>
                                <td class="user-email">{{ user.email }}</td>
                                <td>
                                    <span :class="['status-badge', user.active ? 'active' : 'inactive']">
                                        {{ user.active ? 'Active' : 'Inactive' }}
                                    </span>
                                </td>
                                <td>
                                    <div class="roles">
                                        <span v-for="role in user.roles" :key="role" :class="['role-badge', role]">
                                            {{ role }}
                                        </span>
                                    </div>
                                </td>
                                <td class="booking-count">{{ user.total_reservations }}</td>
                                <td class="booking-count active">{{ user.active_reservations }}</td>
                                <td class="actions">
                                    <button @click="toggleUserStatus(user)"
                                        :class="['btn', 'btn-sm', user.active ? 'btn-warning' : 'btn-success']"
                                        :disabled="isCurrentUser(user) || isAdmin(user)"
                                        :title="getToggleButtonTitle(user)">
                                        {{ user.active ? 'Deactivate' : 'Activate' }}
                                    </button>
                                    <button @click="viewUserHistory(user)" class="btn btn-sm btn-info">
                                        View History
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!-- User History Modal -->
                <div v-if="showHistoryModal" class="modal-overlay" @click="closeHistoryModal">
                    <div class="modal history-modal" @click.stop>
                        <div class="modal-header">
                            <h2>Booking History - {{ selectedUser?.name }}</h2>
                            <button @click="closeHistoryModal" class="close-btn">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div v-if="historyLoading" class="loading">
                                Loading booking history...
                            </div>
                            <div v-else-if="reservations.length === 0" class="no-data">
                                No booking history found for this user.
                            </div>
                            <div v-else class="reservations-list">
                                <div v-for="reservation in reservations" :key="reservation.id" class="reservation-card">
                                    <div class="reservation-header">
                                        <h4>{{ reservation.parking_lot.name }}</h4>
                                        <span :class="['status-badge', reservation.status]">
                                            {{ reservation.status }}
                                        </span>
                                    </div>
                                    <div class="reservation-details">
                                        <div class="detail-row">
                                            <span class="label">Location:</span>
                                            <span class="value">{{ reservation.parking_lot.location }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">Spot:</span>
                                            <span class="value">{{ reservation.parking_spot.spot_number }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">Start Time:</span>
                                            <span class="value">{{ formatDateTime(reservation.start_time) }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">End Time:</span>
                                            <span class="value">{{ formatDateTime(reservation.end_time) }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">Booked On:</span>
                                            <span class="value">{{ formatDateTime(reservation.created_at) }}</span>
                                        </div>
                                    </div>
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
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const successMessage = ref('')
const users = ref([])
const showHistoryModal = ref(false)
const selectedUser = ref(null)
const reservations = ref([])
const historyLoading = ref(false)

const activeUsersCount = computed(() => {
    return users.value.filter(user => user.active).length
})

const fetchUsers = async () => {
    try {
        loading.value = true
        error.value = ''

        const token = localStorage.getItem('authToken')
        if (!token) {
            router.push('/login')
            return
        }

        const response = await fetch('http://127.0.0.1:5000/api/v1/admin/users', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            users.value = data.users
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to fetch users'

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

const toggleUserStatus = async (user) => {
    if (isCurrentUser(user) || isAdmin(user)) {
        return
    }

    const action = user.active ? 'deactivate' : 'activate'
    if (!confirm(`Are you sure you want to ${action} user "${user.name}"?`)) {
        return
    }

    try {
        const token = localStorage.getItem('authToken')

        const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/users/${user.id}/toggle-status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = data.message

            // Update local user data
            const userIndex = users.value.findIndex(u => u.id === user.id)
            if (userIndex !== -1) {
                users.value[userIndex].active = !users.value[userIndex].active
            }

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to toggle user status'
        }
    } catch (err) {
        console.error('Toggle status error:', err)
        error.value = 'Network error. Please try again.'
    }
}

const viewUserHistory = async (user) => {
    selectedUser.value = user
    showHistoryModal.value = true
    historyLoading.value = true
    reservations.value = []

    try {
        const token = localStorage.getItem('authToken')

        const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/users/${user.id}/reservations`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            reservations.value = data.reservations
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to fetch user reservations'
        }
    } catch (err) {
        console.error('Fetch reservations error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        historyLoading.value = false
    }
}

const closeHistoryModal = () => {
    showHistoryModal.value = false
    selectedUser.value = null
    reservations.value = []
}

const isCurrentUser = (user) => {
    const currentEmail = localStorage.getItem('userEmail')
    return user.email === currentEmail
}

const isAdmin = (user) => {
    return user.roles.includes('admin')
}

const getToggleButtonTitle = (user) => {
    if (isCurrentUser(user)) return 'Cannot modify your own account'
    if (isAdmin(user)) return 'Cannot modify admin accounts'
    return user.active ? 'Deactivate this user' : 'Activate this user'
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
    fetchUsers()
})
</script>

<style scoped>
.manage-users {
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

.header-stats {
    display: flex;
    gap: 1rem;
}

.stat-card {
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
    min-width: 120px;
}

.stat-value {
    display: block;
    font-size: 1.8rem;
    font-weight: 700;
    color: #667eea;
}

.stat-label {
    display: block;
    font-size: 0.85rem;
    color: #6c757d;
    margin-top: 0.25rem;
}

.loading,
.error-message,
.success-message {
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

.success-message {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.table-container {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e9ecef;
}

.users-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.users-table th,
.users-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
    vertical-align: middle;
}

.users-table th {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    font-weight: 700;
    color: #495057;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}

.users-table tbody tr:hover {
    background-color: #f8f9fa;
}

.user-name {
    font-weight: 600;
    color: #2c3e50;
}

.user-email {
    color: #6c757d;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.active {
    background: #d4edda;
    color: #155724;
}

.status-badge.inactive {
    background: #f8d7da;
    color: #721c24;
}

.roles {
    display: flex;
    gap: 0.25rem;
    flex-wrap: wrap;
}

.role-badge {
    padding: 0.125rem 0.5rem;
    border-radius: 8px;
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: capitalize;
}

.role-badge.admin {
    background: #fff3cd;
    color: #856404;
}

.role-badge.user {
    background: #e2e3e5;
    color: #383d41;
}

.booking-count {
    text-align: center;
    font-weight: 600;
    color: #495057;
}

.booking-count.active {
    color: #28a745;
}

.actions {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.history-modal {
    background: white;
    border-radius: 8px;
    max-width: 800px;
    width: 90%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #dee2e6;
}

.modal-header h2 {
    margin: 0;
    color: #333;
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6c757d;
}

.modal-body {
    padding: 1.5rem;
    overflow-y: auto;
}

.no-data {
    text-align: center;
    color: #6c757d;
    padding: 2rem;
}

.reservations-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.reservation-card {
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 1rem;
    background: #f8f9fa;
}

.reservation-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.reservation-header h4 {
    margin: 0;
    color: #2c3e50;
}

.reservation-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.5rem;
}

.detail-row {
    display: flex;
    gap: 0.5rem;
}

.detail-row .label {
    font-weight: 600;
    color: #495057;
    min-width: 80px;
}

.detail-row .value {
    color: #6c757d;
}

.btn {
    padding: 0.375rem 0.75rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 500;
    transition: all 0.3s ease;
    font-size: 0.8rem;
}

.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
}

.btn-success {
    background: #28a745;
    color: white;
}

.btn-warning {
    background: #ffc107;
    color: #212529;
}

.btn-info {
    background: #17a2b8;
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
