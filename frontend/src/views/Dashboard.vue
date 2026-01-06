<template>
    <AppLayout>
        <div class="dashboard">
            <!-- Header -->
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h3 mb-0">Dashboard</h1>
                <span class="text-muted">{{ currentDate }}</span>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Content -->
            <div v-else>
                <!-- Error/Success Messages -->
                <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
                <div v-if="successMessage" class="alert alert-success" role="alert">{{ successMessage }}</div>

                <!-- Stats Grid -->
                <div class="row g-4 mb-4">
                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 border-start-4 border-start-success shadow-sm">
                            <div class="card-body">
                                <div class="d-flex align-items-center justify-content-between mb-2">
                                    <h6 class="card-subtitle text-muted text-uppercase mb-0">Available Spots</h6>
                                    <div class="fs-4">🅿️</div>
                                </div>
                                <h2 class="card-title mb-0 text-success fw-bold">{{ availableSpots }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 border-start-4 border-start-primary shadow-sm">
                            <div class="card-body">
                                <div class="d-flex align-items-center justify-content-between mb-2">
                                    <h6 class="card-subtitle text-muted text-uppercase mb-0">My Reservations</h6>
                                    <div class="fs-4">📅</div>
                                </div>
                                <h2 class="card-title mb-0 text-primary fw-bold">{{ userReservations.length }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 border-start-4 border-start-warning shadow-sm">
                            <div class="card-body">
                                <div class="d-flex align-items-center justify-content-between mb-2">
                                    <h6 class="card-subtitle text-muted text-uppercase mb-0">Active Bookings</h6>
                                    <div class="fs-4">🚗</div>
                                </div>
                                <h2 class="card-title mb-0 text-warning fw-bold">{{ activeReservations }}</h2>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-3">
                        <div class="card h-100 border-start-4 border-start-info shadow-sm">
                            <div class="card-body">
                                <div class="d-flex align-items-center justify-content-between mb-2">
                                    <h6 class="card-subtitle text-muted text-uppercase mb-0">Parking Lots</h6>
                                    <div class="fs-4">🏢</div>
                                </div>
                                <h2 class="card-title mb-0 text-info fw-bold">{{ parkingLots.length }}</h2>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Active Reservations Section -->
                <section v-if="activeReservationsList.length > 0" class="mb-5">
                    <h4 class="mb-3">Active Reservations</h4>
                    <div class="row g-4">
                        <div v-for="reservation in activeReservationsList" :key="reservation.id" class="col-md-6 col-xl-4">
                            <BaseCard class="border-warning">
                                <div class="d-flex justify-content-between align-items-start mb-3">
                                    <div>
                                        <h5 class="fw-bold mb-1">{{ reservation.parking_lot }}</h5>
                                        <BaseBadge variant="warning">Active</BaseBadge>
                                    </div>
                                    <div class="text-end">
                                        <div class="fs-5 fw-bold">Spot {{ reservation.spot_number }}</div>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <div class="d-flex justify-content-between small mb-1">
                                        <span class="text-muted">Started:</span>
                                        <span class="fw-medium">{{ formatDateTime(reservation.start_time) }}</span>
                                    </div>
                                    <div class="d-flex justify-content-between small">
                                        <span class="text-muted">Ends:</span>
                                        <span class="fw-medium">{{ formatDateTime(reservation.end_time) }}</span>
                                    </div>
                                </div>

                                <div class="d-grid gap-2">
                                    <BaseButton variant="success" size="sm" @click="occupySpot(reservation)">
                                        Mark as Occupied
                                    </BaseButton>
                                    <div class="d-flex gap-2">
                                        <BaseButton variant="warning" size="sm" class="flex-grow-1" @click="extendReservation(reservation)">
                                            Extend (+1hr)
                                        </BaseButton>
                                        <BaseButton variant="danger" size="sm" class="flex-grow-1" @click="releaseSpot(reservation)">
                                            Release
                                        </BaseButton>
                                    </div>
                                </div>
                            </BaseCard>
                        </div>
                    </div>
                </section>

                <!-- Quick Booking Section -->
                <section class="mb-5">
                    <h4 class="mb-3">Quick Booking</h4>
                    <div class="row g-4">
                        <div v-for="lot in parkingLots" :key="lot.id" class="col-md-6 col-xl-4">
                            <BaseCard>
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h5 class="mb-0">{{ lot.name }}</h5>
                                    <BaseBadge variant="success" pill>{{ $currency(lot.price_per_hour) }}/hr</BaseBadge>

                                </div>
                                <p class="text-muted small mb-3">📍 {{ lot.location }}</p>

                                <div class="mb-3">
                                    <div class="progress" style="height: 8px;">
                                        <div 
                                            class="progress-bar" 
                                            role="progressbar" 
                                            :style="{ width: (lot.available_spots / lot.capacity * 100) + '%' }"
                                            :class="getProgressBarClass(lot)"
                                        ></div>
                                    </div>
                                    <div class="d-flex justify-content-between mt-1">
                                        <small class="text-muted">{{ lot.available_spots }} spots left</small>
                                        <small class="text-muted">{{ lot.capacity }} total</small>
                                    </div>
                                </div>

                                <div class="d-flex gap-2">
                                    <router-link :to="`/parking-lots`" class="btn btn-outline-secondary btn-sm flex-grow-1">
                                        Details
                                    </router-link>
                                    <BaseButton 
                                        variant="primary" 
                                        size="sm" 
                                        class="flex-grow-1"
                                        @click="quickReserve(lot)"
                                        :disabled="lot.available_spots === 0 || hasActiveReservationInLot(lot.id)"
                                    >
                                        {{ lot.available_spots === 0 ? 'Full' : hasActiveReservationInLot(lot.id) ? 'Reserved' : 'Reserve' }}
                                    </BaseButton>
                                </div>
                            </BaseCard>
                        </div>
                    </div>
                </section>

                <!-- Recent History -->
                <section>
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="mb-0">Recent History</h4>
                        <router-link to="/reservations" class="btn btn-link btn-sm text-decoration-none">View All</router-link>
                    </div>
                    
                    <BaseCard v-if="recentReservations.length === 0" class="text-center py-4 bg-light">
                        <p class="text-muted mb-0">No parking history yet. Book your first spot above!</p>
                    </BaseCard>

                    <div v-else class="list-group">
                        <div v-for="reservation in recentReservations" :key="reservation.id" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center p-3">
                            <div>
                                <h6 class="mb-1 fw-bold">{{ reservation.parking_lot }}</h6>
                                <div class="small text-muted">
                                    Spot {{ reservation.spot_number }} • {{ formatDate(reservation.created_at) }}
                                </div>
                            </div>
                            <BaseBadge :variant="getStatusVariant(reservation.status)">
                                {{ reservation.status }}
                            </BaseBadge>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    </AppLayout>

    <!-- Reservation Modal -->
    <BaseModal v-if="showReservationModal" :title="`Quick Reserve - ${selectedLot?.name}`" @close="closeReservationModal">
        <div class="mb-4">
            <p class="text-muted mb-3">Rate: {{ $currency(selectedLot?.price_per_hour) }}/hr</p>
            <BaseInput
                id="vehicle-number"
                v-model="vehicleNumber"
                label="Vehicle Number"
                placeholder="Enter vehicle registration number"
                required
            />
             <p class="small text-muted mt-2">Default booking duration: 2 hours</p>
        </div>
        <template #footer>
            <BaseButton variant="secondary" @click="closeReservationModal">Cancel</BaseButton>
            <BaseButton variant="primary" @click="confirmQuickReservation" :loading="!!reserving" :disabled="!!reserving || !vehicleNumber">
                Confirm
            </BaseButton>
        </template>
    </BaseModal>

    <!-- Payment Modal -->
    <PaymentModal
        v-if="showPaymentModal"
        :amount="estimatedCost"
        @close="showPaymentModal = false"
        @payment-success="handlePaymentSuccess"
    />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getUserInfo } from '../utils/auth.js'
import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
import BaseButton from '../components/common/BaseButton.vue'
import BaseBadge from '../components/common/BaseBadge.vue'
import BaseModal from '../components/common/BaseModal.vue'
import PaymentModal from '../components/common/PaymentModal.vue'
import BaseInput from '../components/common/BaseInput.vue'
import { API_BASE_URL } from '@/config'

const userInfo = ref(getUserInfo() || {})
const loading = ref(true)
const error = ref('')
const successMessage = ref('')
const parkingLots = ref([])
const userReservations = ref([])
const showReservationModal = ref(false)
const selectedLot = ref(null)
const vehicleNumber = ref('')
const showPaymentModal = ref(false)
const estimatedCost = ref(0)
const reserving = ref(null)
const currentDate = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

// Computed properties
const availableSpots = computed(() => {
    return parkingLots.value.reduce((total, lot) => total + lot.available_spots, 0)
})

const activeReservations = computed(() => {
    return userReservations.value.filter(res => res.status === 'active').length
})

const activeReservationsList = computed(() => {
    return userReservations.value.filter(res => res.status === 'active')
})

const recentReservations = computed(() => {
    return userReservations.value
        .filter(res => res.status !== 'active')
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5) // Show last 5 completed reservations
})

// Data fetching functions
const fetchParkingLots = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/parking-lots`, {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        if (response.ok) {
            const data = await response.json()
            parkingLots.value = data.parking_lots
        } else {
            console.error('Failed to fetch parking lots')
        }
    } catch (err) {
        console.error('Error fetching parking lots:', err)
    }
}

const fetchUserReservations = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/reservations`, {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        if (response.ok) {
            const data = await response.json()
            userReservations.value = data.reservations
        } else {
            console.error('Failed to fetch reservations')
        }
    } catch (err) {
        console.error('Error fetching reservations:', err)
    }
}

// User actions
const quickReserve = (lot) => {
    if (hasActiveReservationInLot(lot.id)) {
        error.value = 'You already have an active reservation in this parking lot'
        window.scrollTo(0, 0)
        return
    }
    
    selectedLot.value = lot
    showReservationModal.value = true
}

const confirmQuickReservation = () => {
    if (!selectedLot.value || !vehicleNumber.value) return

    // Calculate estimated cost (2 hours default)
    estimatedCost.value = selectedLot.value.price_per_hour * 2

    showReservationModal.value = false
    showPaymentModal.value = true
}

const handlePaymentSuccess = async () => {
    showPaymentModal.value = false
    await finalizeQuickReservation()
}

const finalizeQuickReservation = async () => {
    if (!selectedLot.value || !vehicleNumber.value) return 

    try {
        reserving.value = selectedLot.value.id
        const response = await fetch(`${API_BASE_URL}/reservations`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lot_id: selectedLot.value.id,
                duration_hours: 2, // Default 2 hours
                vehicle_number: vehicleNumber.value
            })
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Successfully reserved spot ${data.reservation.spot_number} in ${selectedLot.value.name}`
            error.value = ''
            closeReservationModal()
            window.scrollTo(0, 0)

            // Refresh data
            await Promise.all([fetchParkingLots(), fetchUserReservations()])

            setTimeout(() => {
                successMessage.value = ''
            }, 5000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to reserve spot'
            closeReservationModal()
            window.scrollTo(0, 0)
        }
    } catch (err) {
        console.error('Reservation error:', err)
        error.value = 'Network error. Please try again.'
        closeReservationModal()
        window.scrollTo(0, 0)
    } finally {
        reserving.value = null
    }
}

const occupySpot = async (reservation) => {
    try {
        const response = await fetch(`${API_BASE_URL}/reservations/${reservation.id}/occupy`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        if (response.ok) {
            successMessage.value = 'Spot marked as occupied'
            error.value = ''
            window.scrollTo(0, 0)
            await fetchUserReservations()

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to occupy spot'
            window.scrollTo(0, 0)
        }
    } catch (err) {
        console.error('Occupy error:', err)
        error.value = 'Network error. Please try again.'
        window.scrollTo(0, 0)
    }
}

const releaseSpot = async (reservation) => {
    if (!confirm('Are you sure you want to release this spot? This action cannot be undone.')) {
        return
    }

    try {
        const response = await fetch(`${API_BASE_URL}/reservations/${reservation.id}/release`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Spot released successfully. Duration: ${data.reservation.duration_hours}h, Cost: $${data.reservation.total_cost}`
            error.value = ''
            window.scrollTo(0, 0)

            // Refresh data
            await Promise.all([fetchParkingLots(), fetchUserReservations()])

            setTimeout(() => {
                successMessage.value = ''
            }, 5000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to release spot'
            window.scrollTo(0, 0)
        }
    } catch (err) {
        console.error('Release error:', err)
        error.value = 'Network error. Please try again.'
        window.scrollTo(0, 0)
    }
}

const extendReservation = async (reservation) => {
    try {
        const response = await fetch(`${API_BASE_URL}/reservations/${reservation.id}/extend`, {
            method: 'PUT',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                additional_hours: 1
            })
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Reservation extended by 1 hour. Additional cost: $${data.reservation.additional_cost}`
            error.value = ''
            window.scrollTo(0, 0)
            await fetchUserReservations()

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to extend reservation'
            window.scrollTo(0, 0)
        }
    } catch (err) {
        console.error('Extend error:', err)
        error.value = 'Network error. Please try again.'
        window.scrollTo(0, 0)
    }
}

// Helper functions
const hasActiveReservationInLot = (lotId) => {
    return activeReservationsList.value.some(res => {
        return parkingLots.value.find(lot => lot.name === res.parking_lot)?.id === lotId
    })
}

const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString()
}

const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString()
}

const getProgressBarClass = (lot) => {
    const percentage = (lot.available_spots / lot.capacity) * 100
    if (percentage === 0) return 'bg-secondary'
    if (percentage <= 20) return 'bg-danger'
    if (percentage <= 50) return 'bg-warning'
    return 'bg-success'
}

const getStatusVariant = (status) => {
    switch (status) {
        case 'active': return 'warning'
        case 'completed': return 'success'
        case 'cancelled': return 'danger'
        default: return 'secondary'
    }
}

const closeReservationModal = () => {
    showReservationModal.value = false
    selectedLot.value = null
    vehicleNumber.value = ''
    error.value = ''
}

// Border-start utility classes need to be defined or we use bootstrap border utilities
// Using custom border-start-X classes for card borders or just inline styles or custom css in dashboard
// Let's add simple scoped css for the colored borders if bootstrap doesn't have colored borders like that out of box (it has border-primary etc but that's full border)

onMounted(async () => {
    loading.value = true
    try {
        await Promise.all([fetchParkingLots(), fetchUserReservations()])
    } catch (err) {
        error.value = 'Failed to load dashboard data'
    } finally {
        loading.value = false
    }
})
</script>

<style scoped>
.border-start-4 {
    border-left-width: 4px !important;
}
.border-start-success { border-left-color: var(--bs-success) !important; }
.border-start-primary { border-left-color: var(--bs-primary) !important; }
.border-start-warning { border-left-color: var(--bs-warning) !important; }
.border-start-info { border-left-color: var(--bs-info) !important; }
</style>
