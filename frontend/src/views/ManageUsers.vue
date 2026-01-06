<template>
    <AppLayout>
        <div class="manage-users">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h2 mb-0">User Management</h1>
                <!-- Future: Add Add User button if API supports it -->
            </div>

            <!-- Stats Summary -->
            <div class="row g-4 mb-4">
                <div class="col-md-3 col-6">
                    <BaseCard class="h-100 text-center border-start border-4 border-primary">
                        <h6 class="text-muted text-uppercase small mb-1">Total Users</h6>
                        <div class="h2 fw-bold text-primary mb-0">{{ users.length }}</div>
                    </BaseCard>
                </div>
                <div class="col-md-3 col-6">
                    <BaseCard class="h-100 text-center border-start border-4 border-success">
                        <h6 class="text-muted text-uppercase small mb-1">Active Users</h6>
                        <div class="h2 fw-bold text-success mb-0">{{ activeUsersCount }}</div>
                    </BaseCard>
                </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="alert alert-danger" role="alert">
                {{ error }}
            </div>

            <!-- Success Message -->
            <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                {{ successMessage }}
                <button type="button" class="btn-close" @click="successMessage = ''"></button>
            </div>

            <!-- Users Table -->
            <BaseCard v-if="!loading && !error" class="border-0 shadow-sm px-0 pt-0 pb-2">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="bg-light">
                            <tr>
                                <th class="ps-4">Name</th>
                                <th>Email</th>
                                <th>Status</th>
                                <th>Roles</th>
                                <th class="text-center">Total Bookings</th>
                                <th class="text-center">Active Bookings</th>
                                <th class="text-end pe-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="user in users" :key="user.id">
                                <td class="fw-bold ps-4">{{ user.name }}</td>
                                <td class="text-muted">{{ user.email }}</td>
                                <td>
                                    <BaseBadge :variant="user.active ? 'success' : 'danger'">
                                        {{ user.active ? 'Active' : 'Inactive' }}
                                    </BaseBadge>
                                </td>
                                <td>
                                    <div class="d-flex gap-1 flex-wrap">
                                        <BaseBadge 
                                            v-for="role in user.roles" 
                                            :key="role" 
                                            :variant="role === 'admin' ? 'warning' : 'secondary'"
                                            class="text-uppercase small"
                                        >
                                            {{ role }}
                                        </BaseBadge>
                                    </div>
                                </td>
                                <td class="text-center fw-bold text-secondary">{{ user.total_reservations }}</td>
                                <td class="text-center fw-bold text-success">{{ user.active_reservations }}</td>
                                <td class="text-end pe-4">
                                    <BaseButton 
                                        size="sm" 
                                        :variant="user.active ? 'outline-warning' : 'outline-success'" 
                                        class="me-2"
                                        @click="toggleUserStatus(user)"
                                        :disabled="isCurrentUser(user) || isAdminUser(user)"
                                        :title="getToggleButtonTitle(user)"
                                    >
                                        <i class="bi" :class="user.active ? 'bi-person-x' : 'bi-person-check'"></i>
                                    </BaseButton>
                                    <BaseButton size="sm" variant="outline-info" @click="viewUserHistory(user)">
                                        <i class="bi bi-clock-history"></i>
                                    </BaseButton>
                                </td>
                            </tr>
                            <tr v-if="users.length === 0">
                                <td colspan="7" class="text-center py-4 text-muted">
                                    No users found.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </BaseCard>

            <!-- User History Modal -->
            <BaseModal 
                v-if="showHistoryModal" 
                :title="`Booking History - ${selectedUser?.name}`" 
                size="lg"
                @close="closeHistoryModal"
            >
                <div v-if="historyLoading" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
                
                <div v-else-if="reservations.length === 0" class="text-center py-4 text-muted">
                    <i class="bi bi-calendar-x fs-1 mb-2 d-block"></i>
                    No booking history found for this user.
                </div>
                
                <div v-else class="list-group list-group-flush">
                    <div v-for="reservation in reservations" :key="reservation.id" class="list-group-item px-0 py-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                             <h6 class="mb-0 fw-bold">{{ reservation.parking_lot.name }}</h6>
                             <BaseBadge :variant="getStatusVariant(reservation.status)">
                                {{ reservation.status }}
                             </BaseBadge>
                        </div>
                        <div class="row g-2 text-muted small">
                            <div class="col-sm-6">
                                <i class="bi bi-geo-alt me-1"></i>{{ reservation.parking_lot.location }}
                            </div>
                            <div class="col-sm-6">
                                <i class="bi bi-p-circle me-1"></i>Spot: {{ reservation.parking_spot.spot_number }}
                            </div>
                            <div class="col-sm-6">
                                <i class="bi bi-clock me-1"></i>Start: {{ formatDateTime(reservation.start_time) }}
                            </div>
                            <div class="col-sm-6">
                                <i class="bi bi-clock-history me-1"></i>End: {{ formatDateTime(reservation.end_time) }}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="d-flex justify-content-end mt-3">
                     <BaseButton variant="secondary" @click="closeHistoryModal">Close</BaseButton>
                </div>
            </BaseModal>
        </div>
    </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
import BaseButton from '../components/common/BaseButton.vue'
import BaseBadge from '../components/common/BaseBadge.vue'
import BaseModal from '../components/common/BaseModal.vue'
import { API_BASE_URL } from '@/config'

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

        const response = await fetch(`${API_BASE_URL}/admin/users`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
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
    if (isCurrentUser(user) || isAdminUser(user)) {
        return
    }

    const action = user.active ? 'deactivate' : 'activate'
    if (!confirm(`Are you sure you want to ${action} user "${user.name}"?`)) {
        return
    }

    try {
        const token = localStorage.getItem('authToken')

        const response = await fetch(`${API_BASE_URL}/admin/users/${user.id}/toggle-status`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
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

        const response = await fetch(`${API_BASE_URL}/admin/users/${user.id}/reservations`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
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

const isAdminUser = (user) => {
    return user.roles.includes('admin')
}

const getToggleButtonTitle = (user) => {
    if (isCurrentUser(user)) return 'Cannot modify your own account'
    if (isAdminUser(user)) return 'Cannot modify admin accounts'
    return user.active ? 'Deactivate this user' : 'Activate this user'
}

const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString()
}

const getStatusVariant = (status) => {
    switch (status) {
        case 'active': return 'success'
        case 'completed': return 'primary'
        case 'cancelled': return 'danger'
        default: return 'secondary'
    }
}

onMounted(() => {
    fetchUsers()
})
</script>

<style scoped>
/* Bootstrap handles most styling */
</style>
