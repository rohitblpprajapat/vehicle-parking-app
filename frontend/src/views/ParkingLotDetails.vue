<template>
    <AppLayout>
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div class="mt-3 text-muted">Loading parking lot details...</div>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger" role="alert">
            {{ error }}
        </div>

        <!-- Content -->
        <div v-else-if="parkingLot" class="parking-lot-details">
            <!-- Header -->
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 pb-3 border-bottom">
                <div>
                    <h1 class="h2 mb-1">{{ parkingLot.name }}</h1>
                    <p class="text-muted mb-0"><i class="bi bi-geo-alt me-1"></i>{{ parkingLot.location }}</p>
                </div>
                <div class="mt-3 mt-md-0">
                    <router-link :to="isAdmin ? '/admin/parking-lots' : '/parking-lots'" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-left me-1"></i>Back to Lots
                    </router-link>
                </div>
            </div>

            <!-- Summary Cards -->
            <div class="row g-4 mb-4">
                <div class="col-md-3 col-sm-6">
                    <BaseCard class="h-100 border-start border-4 border-info">
                        <div class="d-flex align-items-center">
                            <div class="flex-shrink-0 bg-info bg-opacity-10 p-3 rounded">
                                <span class="fs-2">🏗️</span>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <h6 class="text-muted text-uppercase small mb-1">Total Capacity</h6>
                                <div class="h3 fw-bold mb-0 text-dark">{{ parkingLot.capacity }}</div>
                                <small class="text-muted">spots</small>
                            </div>
                        </div>
                    </BaseCard>
                </div>
                <div class="col-md-3 col-sm-6">
                    <BaseCard class="h-100 border-start border-4 border-success">
                        <div class="d-flex align-items-center">
                            <div class="flex-shrink-0 bg-success bg-opacity-10 p-3 rounded">
                                <span class="fs-2">✅</span>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <h6 class="text-muted text-uppercase small mb-1">Available</h6>
                                <div class="h3 fw-bold mb-0 text-success">{{ parkingLot.available_spots }}</div>
                                <small class="text-muted">spots</small>
                            </div>
                        </div>
                    </BaseCard>
                </div>
                <div class="col-md-3 col-sm-6">
                    <BaseCard class="h-100 border-start border-4 border-danger">
                        <div class="d-flex align-items-center">
                            <div class="flex-shrink-0 bg-danger bg-opacity-10 p-3 rounded">
                                <span class="fs-2">🚗</span>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <h6 class="text-muted text-uppercase small mb-1">Occupied</h6>
                                <div class="h3 fw-bold mb-0 text-danger">{{ parkingLot.occupied_spots }}</div>
                                <small class="text-muted">spots</small>
                            </div>
                        </div>
                    </BaseCard>
                </div>
                <div class="col-md-3 col-sm-6">
                    <BaseCard class="h-100 border-start border-4 border-warning">
                        <div class="d-flex align-items-center">
                            <div class="flex-shrink-0 bg-warning bg-opacity-10 p-3 rounded">
                                <span class="fs-2">💰</span>
                            </div>
                            <div class="flex-grow-1 ms-3">
                                <h6 class="text-muted text-uppercase small mb-1">Price</h6>
                                <div class="h3 fw-bold mb-0 text-dark">{{ $currency(parkingLot.price_per_hour) }}</div>

                                <small class="text-muted">per hour</small>
                            </div>
                        </div>
                    </BaseCard>
                </div>
            </div>

            <!-- Occupancy Progress -->
            <BaseCard class="mb-4">
                <h5 class="card-title mb-3">Occupancy Overview</h5>
                <div class="progress" style="height: 25px;">
                    <div 
                        class="progress-bar progress-bar-striped progress-bar-animated" 
                        role="progressbar" 
                        :style="{ width: parkingLot.occupancy_rate + '%' }"
                        :class="getOccupancyClass(parkingLot.occupancy_rate)"
                        :aria-valuenow="parkingLot.occupancy_rate" 
                        aria-valuemin="0" 
                        aria-valuemax="100"
                    ></div>
                </div>
                <div class="mt-2 text-center text-muted fw-bold">
                    {{ parkingLot.occupancy_rate.toFixed(1) }}% occupied 
                    <span class="fw-normal">({{ parkingLot.occupied_spots }} of {{ parkingLot.capacity }} spots)</span>
                </div>
            </BaseCard>

            <!-- Spots Grid -->
            <BaseCard title="Parking Spots Layout">
                <div class="d-flex gap-4 mb-4 justify-content-center justify-content-md-start">
                    <div class="d-flex align-items-center">
                        <div class="spot-legend available me-2"></div>
                        <span>Available</span>
                    </div>
                    <div class="d-flex align-items-center">
                        <div class="spot-legend occupied me-2"></div>
                        <span>Occupied</span>
                    </div>
                </div>
                
                <div class="spots-grid-container">
                    <div v-for="spot in parkingLot.spots" :key="spot.id"
                        class="parking-spot"
                        :class="{'occupied': spot.is_occupied, 'available': !spot.is_occupied}"
                        :title="`Spot ${spot.spot_number} - ${spot.is_occupied ? 'Occupied' : 'Available'}`"
                    >
                        <span class="spot-number">{{ spot.spot_number }}</span>
                        <i class="bi" :class="spot.is_occupied ? 'bi-car-front-fill' : ''"></i>
                    </div>
                </div>
            </BaseCard>
        </div>
    </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { isAdmin as checkIsAdmin } from '../utils/auth.js'
import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
import BaseBadge from '../components/common/BaseBadge.vue'
import { API_BASE_URL } from '@/config'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref('')
const parkingLot = ref(null)

const isAdmin = computed(() => checkIsAdmin())

const getOccupancyClass = (rate) => {
    if (rate < 50) return 'bg-success'
    if (rate < 80) return 'bg-warning'
    return 'bg-danger'
}

const fetchParkingLotDetails = async () => {
    try {
        loading.value = true
        error.value = ''

        const token = localStorage.getItem('authToken')
        if (!token) {
            router.push('/login')
            return
        }

        const lotId = route.params.id
        const apiEndpoint = isAdmin.value
            ? `/admin/parking-lots/${lotId}/spots`
            : `/parking-lots/${lotId}`

        const response = await fetch(`${API_BASE_URL}${apiEndpoint}`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        if (response.ok) {
            const data = await response.json()
            parkingLot.value = {
                ...data.parking_lot,
                spots: data.spots,
                occupied_spots: data.spots.filter(spot => spot.is_occupied).length,
                available_spots: data.spots.filter(spot => !spot.is_occupied).length,
                occupancy_rate: data.parking_lot.capacity > 0 ? (data.spots.filter(spot => spot.is_occupied).length / data.parking_lot.capacity * 100) : 0
            }
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to fetch parking lot details'

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

onMounted(() => {
    fetchParkingLotDetails()
})
</script>

<style scoped>
.spot-legend {
    width: 24px;
    height: 24px;
    border-radius: 4px;
}
.spot-legend.available {
    background-color: #28a745; /* Success */
    border: 1px solid #1e7e34;
}
.spot-legend.occupied {
    background-color: #dc3545; /* Danger */
    border: 1px solid #bd2130;
}

.spots-grid-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 1rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 8px;
    max-height: 500px;
    overflow-y: auto;
}

.parking-spot {
    aspect-ratio: 4/3;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    font-weight: bold;
    cursor: default;
    transition: transform 0.2s;
    border-width: 2px;
    border-style: solid;
}

.parking-spot:hover {
    transform: scale(1.05);
}

.parking-spot.available {
    background-color: #d1e7dd;
    color: #0f5132;
    border-color: #badbcc;
}

.parking-spot.occupied {
    background-color: #f8d7da;
    color: #842029;
    border-color: #f5c2c7;
}

.spot-number {
    font-size: 1.1rem;
}
</style>
