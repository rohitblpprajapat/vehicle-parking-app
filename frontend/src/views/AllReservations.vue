<template>
    <AppLayout>
        <div class="all-reservations">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h2 mb-0">All Reservations</h1>
                <!-- Filters -->
                <div class="d-flex gap-2">
                    <select class="form-select w-auto" v-model="selectedStatus" @change="fetchReservations">
                        <option value="">All Statuses</option>
                        <option value="active">Active</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                    <div class="input-group w-auto">
                        <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
                        <input 
                            type="text" 
                            class="form-control" 
                            v-model="searchEmail" 
                            @input="debouncedSearch" 
                            placeholder="Search email..."
                        >
                    </div>
                </div>
            </div>

            <!-- Stats Overview -->
            <div class="row g-4 mb-4">
                <div class="col-md-3 col-6">
                    <BaseCard class="h-100 border-start border-4 border-primary">
                        <div class="d-flex align-items-center">
                            <div class="flex-grow-1">
                                <h6 class="text-muted text-uppercase small mb-1">Total</h6>
                                <div class="h2 fw-bold text-primary mb-0">{{ totalCount }}</div>
                            </div>
                            <div class="fs-1 text-primary opacity-25">
                                <i class="bi bi-bar-chart"></i>
                            </div>
                        </div>
                    </BaseCard>
                </div>
                <div class="col-md-3 col-6">
                    <BaseCard class="h-100 border-start border-4 border-warning">
                         <div class="d-flex align-items-center">
                            <div class="flex-grow-1">
                                <h6 class="text-muted text-uppercase small mb-1">Active</h6>
                                <div class="h2 fw-bold text-warning mb-0">{{ activeCount }}</div>
                            </div>
                            <div class="fs-1 text-warning opacity-25">
                                <i class="bi bi-calendar-event"></i>
                            </div>
                        </div>
                    </BaseCard>
                </div>
                <div class="col-md-3 col-6">
                    <BaseCard class="h-100 border-start border-4 border-success">
                         <div class="d-flex align-items-center">
                            <div class="flex-grow-1">
                                <h6 class="text-muted text-uppercase small mb-1">Completed</h6>
                                <div class="h2 fw-bold text-success mb-0">{{ completedCount }}</div>
                            </div>
                            <div class="fs-1 text-success opacity-25">
                                <i class="bi bi-check-circle"></i>
                            </div>
                        </div>
                    </BaseCard>
                </div>
                <div class="col-md-3 col-6">
                    <BaseCard class="h-100 border-start border-4 border-danger">
                         <div class="d-flex align-items-center">
                            <div class="flex-grow-1">
                                <h6 class="text-muted text-uppercase small mb-1">Cancelled</h6>
                                <div class="h2 fw-bold text-danger mb-0">{{ cancelledCount }}</div>
                            </div>
                            <div class="fs-1 text-danger opacity-25">
                                <i class="bi bi-x-circle"></i>
                            </div>
                        </div>
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

            <!-- Reservations Table -->
            <BaseCard v-if="!loading && !error" class="border-0 shadow-sm px-0 pt-0 pb-2">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="bg-light">
                            <tr>
                                <th class="ps-4">User</th>
                                <th>Parking Lot</th>
                                <th class="text-center">Spot</th>
                                <th>Vehicle</th>
                                <th>Period</th>
                                <th>Status</th>
                                <th class="pe-4 text-end">Booked On</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="reservation in reservations" :key="reservation.id">
                                <td class="ps-4">
                                    <div class="fw-bold text-dark">{{ reservation.user.name }}</div>
                                    <div class="text-muted small">{{ reservation.user.email }}</div>
                                </td>
                                <td>
                                    <div class="fw-bold text-dark">{{ reservation.parking_lot.name }}</div>
                                    <div class="text-muted small"><i class="bi bi-geo-alt me-1"></i>{{ reservation.parking_lot.location }}</div>
                                </td>
                                <td class="text-center">
                                    <span class="badge bg-light text-dark border font-monospace">{{ reservation.parking_spot.spot_number }}</span>
                                </td>
                                <td>
                                    <span class="font-monospace small">{{ reservation.vehicle_number || '-' }}</span>
                                </td>
                                <td>
                                    <div class="small">
                                        <div class="text-muted">Start: <span class="text-dark">{{ formatDateTime(reservation.start_time) }}</span></div>
                                        <div class="text-muted">End: <span class="text-dark">{{ formatDateTime(reservation.end_time) }}</span></div>
                                    </div>
                                </td>
                                <td>
                                    <BaseBadge :variant="getStatusVariant(reservation.status)">
                                        {{ reservation.status }}
                                    </BaseBadge>
                                </td>
                                <td class="text-end pe-4 text-muted small">
                                    {{ formatDateTime(reservation.created_at) }}
                                </td>
                            </tr>
                             <tr v-if="reservations.length === 0">
                                <td colspan="6" class="text-center py-4 text-muted">
                                    No reservations found matching criteria.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                 <!-- Pagination -->
                <div v-if="totalCount > limit" class="d-flex justify-content-between align-items-center px-4 py-3 border-top">
                    <BaseButton 
                        size="sm" 
                        variant="outline-secondary" 
                        @click="previousPage" 
                        :disabled="offset === 0"
                    >
                        Previous
                    </BaseButton>
                    <span class="text-muted small">
                        Showing {{ offset + 1 }} - {{ Math.min(offset + limit, totalCount) }} of {{ totalCount }}
                    </span>
                    <BaseButton 
                        size="sm" 
                        variant="outline-secondary" 
                        @click="nextPage" 
                        :disabled="offset + limit >= totalCount"
                    >
                        Next
                    </BaseButton>
                </div>
            </BaseCard>
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
import BaseInput from '../components/common/BaseInput.vue'
import { API_BASE_URL } from '@/config'

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

        const params = new URLSearchParams({
            limit: limit.value.toString(),
            offset: offset.value.toString()
        })

        if (selectedStatus.value) {
            params.append('status', selectedStatus.value)
        }

        const response = await fetch(`${API_BASE_URL}/admin/reservations?${params}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        if (response.ok) {
            const data = await response.json()
            reservations.value = data.reservations
            totalCount.value = data.total_count

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
        offset.value = 0 
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
    return new Date(dateString).toLocaleString(undefined, {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    })
}

const getStatusVariant = (status) => {
    switch(status) {
        case 'active': return 'warning'
        case 'completed': return 'success'
        case 'cancelled': return 'danger'
        default: return 'secondary'
    }
}

onMounted(() => {
    fetchReservations()
})
</script>

<style scoped>
/* Bootstrap does the heavy lifting */
</style>
