<template>
    <AppLayout>
        <div class="admin-dashboard">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h2 mb-0">Admin Dashboard</h1>
                <div class="text-muted small">Overview of system status</div>
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

            <!-- Dashboard Content -->
            <div v-else-if="dashboardData">
                <!-- Summary Stats -->
                <div class="row g-4 mb-5">
                    <!-- Parking Stats -->
                    <div class="col-md-3 col-sm-6">
                        <BaseCard class="h-100 border-start border-4 border-primary">
                            <div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h6 class="text-muted text-uppercase small mb-1">Total Lots</h6>
                                    <div class="h2 fw-bold mb-0 text-primary">{{ dashboardData.summary.total_parking_lots }}</div>
                                </div>
                                <div class="fs-1 text-primary opacity-25">
                                    <i class="bi bi-p-square"></i>
                                </div>
                            </div>
                        </BaseCard>
                    </div>
                    <div class="col-md-3 col-sm-6">
                        <BaseCard class="h-100 border-start border-4 border-success">
                            <div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h6 class="text-muted text-uppercase small mb-1">Available Spots</h6>
                                    <div class="h2 fw-bold mb-0 text-success">{{ dashboardData.summary.available_spots }}</div>
                                </div>
                                <div class="fs-1 text-success opacity-25">
                                    <i class="bi bi-check-circle"></i>
                                </div>
                            </div>
                        </BaseCard>
                    </div>
                    
                    <!-- User Stats -->
                    <div class="col-md-3 col-sm-6">
                        <BaseCard class="h-100 border-start border-4 border-info">
                             <div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h6 class="text-muted text-uppercase small mb-1">Active Users</h6>
                                    <div class="h2 fw-bold mb-0 text-info">{{ dashboardData.summary.active_users }}</div>
                                </div>
                                <div class="fs-1 text-info opacity-25">
                                    <i class="bi bi-people"></i>
                                </div>
                            </div>
                        </BaseCard>
                    </div>

                    <!-- Reservation Stats -->
                     <div class="col-md-3 col-sm-6">
                        <BaseCard class="h-100 border-start border-4 border-warning">
                             <div class="d-flex align-items-center">
                                <div class="flex-grow-1">
                                    <h6 class="text-muted text-uppercase small mb-1">Active Reservations</h6>
                                    <div class="h2 fw-bold mb-0 text-warning">{{ dashboardData.summary.active_reservations }}</div>
                                </div>
                                <div class="fs-1 text-warning opacity-25">
                                    <i class="bi bi-calendar-event"></i>
                                </div>
                            </div>
                        </BaseCard>
                    </div>
                </div>

                <!-- Management Tools -->
                <div class="mb-5">
                    <h4 class="mb-3 text-muted">Management Tools</h4>
                    <div class="row g-4">
                        <div class="col-md-4">
                            <router-link to="/admin/parking-lots" class="text-decoration-none">
                                <BaseCard class="h-100 text-center hover-up">
                                    <div class="mb-3 text-primary fs-1">
                                        <i class="bi bi-buildings"></i>
                                    </div>
                                    <h5 class="text-dark">Manage Parking Lots</h5>
                                    <p class="text-muted small mb-0">Create, edit, and delete parking lots</p>
                                </BaseCard>
                            </router-link>
                        </div>
                         <div class="col-md-4">
                            <router-link to="/admin/users" class="text-decoration-none">
                                <BaseCard class="h-100 text-center hover-up">
                                    <div class="mb-3 text-info fs-1">
                                        <i class="bi bi-people-fill"></i>
                                    </div>
                                    <h5 class="text-dark">Manage Users</h5>
                                    <p class="text-muted small mb-0">View users and control account status</p>
                                </BaseCard>
                            </router-link>
                        </div>
                         <div class="col-md-4">
                            <router-link to="/admin/reservations" class="text-decoration-none">
                                <BaseCard class="h-100 text-center hover-up">
                                    <div class="mb-3 text-warning fs-1">
                                        <i class="bi bi-calendar-check-fill"></i>
                                    </div>
                                    <h5 class="text-dark">All Reservations</h5>
                                    <p class="text-muted small mb-0">Monitor all booking activities</p>
                                </BaseCard>
                            </router-link>
                        </div>
                    </div>
                </div>

                <!-- Parking Lots Overview -->
                <BaseCard title="Parking Lots Overview" class="mb-4">
                    <div class="table-responsive">
                         <table class="table table-hover align-middle">
                            <thead class="bg-light">
                                <tr>
                                    <th>Name</th>
                                    <th>Location</th>
                                    <th>Status</th>
                                    <th>Occupancy</th>
                                    <th class="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="lot in dashboardData.parking_lots" :key="lot.id">
                                    <td class="fw-bold">{{ lot.name }}</td>
                                    <td>{{ lot.location }}</td>
                                    <td>
                                        <BaseBadge :variant="lot.available_spots > 0 ? 'success' : 'danger'">
                                            {{ lot.available_spots > 0 ? 'Available' : 'Full' }}
                                        </BaseBadge>
                                    </td>
                                    <td style="width: 30%">
                                        <div class="d-flex align-items-center">
                                            <div class="progress flex-grow-1 me-2" style="height: 6px;">
                                                <div 
                                                    class="progress-bar" 
                                                    :class="getOccupancyClass(lot.occupancy_rate)"
                                                    role="progressbar" 
                                                    :style="{ width: lot.occupancy_rate + '%' }"
                                                ></div>
                                            </div>
                                            <small class="text-muted" style="width: 40px">{{ lot.occupancy_rate.toFixed(0) }}%</small>
                                        </div>
                                        <small class="text-muted d-block mt-1">
                                            {{ lot.occupied_spots }}/{{ lot.capacity }} spots
                                        </small>
                                    </td>
                                    <td class="text-end">
                                        <router-link :to="`/admin/parking-lots/${lot.id}`" class="btn btn-sm btn-outline-primary">
                                            View
                                        </router-link>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </BaseCard>

            </div>
        </div>
    </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { logout as authLogout, getUserInfo } from '../utils/auth.js'
import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
import BaseBadge from '../components/common/BaseBadge.vue'
import { API_BASE_URL } from '@/config'

const router = useRouter()
const userInfo = ref(getUserInfo() || {})
const loading = ref(true)
const error = ref('')
const dashboardData = ref(null)

const getOccupancyClass = (rate) => {
    if (rate < 50) return 'bg-success'
    if (rate < 80) return 'bg-warning'
    return 'bg-danger'
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

        const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
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
.hover-up {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hover-up:hover {
    transform: translateY(-5px);
    box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important;
}
</style>
