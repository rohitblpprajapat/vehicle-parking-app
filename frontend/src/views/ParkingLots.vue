<template>
    <AppLayout>
        <div class="parking-lots">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h3 mb-0">Available Parking Lots</h1>
                <div class="d-flex gap-3">
                    <div class="text-end">
                        <div class="h4 mb-0 text-success fw-bold">{{ totalAvailableSpots }}</div>
                        <div class="small text-muted text-uppercase">Available Spots</div>
                    </div>
                    <div class="vr"></div>
                    <div class="text-end">
                        <div class="h4 mb-0 text-primary fw-bold">{{ parkingLots.length }}</div>
                        <div class="small text-muted text-uppercase">Locations</div>
                    </div>
                </div>
            </div>

            <!-- Messages -->
            <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
            <div v-if="successMessage" class="alert alert-success" role="alert">{{ successMessage }}</div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <div v-else>
                <!-- Filters -->
                <BaseCard class="mb-4">
                    <div class="row g-3">
                        <div class="col-md-5">
                            <BaseInput
                                id="search"
                                v-model="searchQuery"
                                placeholder="Search by name or location..."
                                class="mb-0"
                            />
                        </div>
                        <div class="col-md-3">
                            <select class="form-select border-0 bg-light" v-model="locationFilter">
                                <option value="">All Locations</option>
                                <option v-for="location in uniqueLocations" :key="location" :value="location">
                                    {{ location }}
                                </option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <select class="form-select border-0 bg-light" v-model="sortBy">
                                <option value="name">Sort by Name</option>
                                <option value="price">Sort by Price</option>
                                <option value="availability">Sort by Availability</option>
                            </select>
                        </div>
                    </div>
                </BaseCard>

                <!-- Grid -->
                <div v-if="filteredAndSortedLots.length > 0" class="row g-4">
                    <div v-for="lot in filteredAndSortedLots" :key="lot.id" class="col-md-6 col-lg-4">
                        <BaseCard class="h-100">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title mb-0">{{ lot.name }}</h5>
                                <BaseBadge :variant="getAvailabilityVariant(lot)">
                                    {{ lot.available_spots }}/{{ lot.capacity }} Left
                                </BaseBadge>
                            </div>
                            
                            <p class="text-muted small mb-3">📍 {{ lot.location }}</p>

                            <div class="mb-3">
                                <div class="progress" style="height: 8px;">
                                    <div 
                                        class="progress-bar" 
                                        role="progressbar" 
                                        :style="{ width: (lot.occupancy_rate || 0) + '%' }"
                                        :class="getProgressBarClass(lot)"
                                    ></div>
                                </div>
                                <div class="d-flex justify-content-between mt-1 text-muted small">
                                    <span>{{ (lot.occupancy_rate || 0).toFixed(0) }}% Occupied</span>
                                    <span>{{ $currency(lot.price_per_hour) }}/hr</span>

                                </div>
                            </div>

                            <div class="d-flex gap-2 mt-auto">
                                <router-link :to="`/parking-lots/${lot.id}`" class="btn btn-outline-secondary btn-sm flex-fill">
                                    Layout
                                </router-link>
                                <BaseButton 
                                    variant="primary" 
                                    size="sm" 
                                    class="flex-fill"
                                    @click="quickReserve(lot)"
                                    :disabled="lot.available_spots === 0 || hasActiveReservationInLot(lot.id) || reserving === lot.id"
                                >
                                    {{ reserving === lot.id ? '...' : lot.available_spots === 0 ? 'Full' : hasActiveReservationInLot(lot.id) ? 'Reserved' : 'Reserve' }}
                                </BaseButton>
                            </div>
                        </BaseCard>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-else class="text-center py-5">
                    <div class="fs-1 mb-3">🅿️</div>
                    <h3>No parking lots found</h3>
                    <p class="text-muted">Try adjusting your search criteria</p>
                </div>
            </div>

            <!-- Reservation Modal -->
            <BaseModal v-if="showReservationModal" :title="`Reserve Spot - ${selectedLot?.name}`" @close="closeReservationModal">
                <div class="mb-4">
                    <label class="form-label fw-bold">Duration</label>
                    <div class="d-grid gap-2 d-md-flex mb-3">
                        <button 
                            v-for="duration in durationOptions" 
                            :key="duration.value"
                            @click="selectedDuration = duration.value"
                            :class="['btn', 'btn-sm', selectedDuration === duration.value ? 'btn-success' : 'btn-outline-secondary']"
                        >
                            {{ duration.label }}
                        </button>
                    </div>
                    <BaseInput
                        id="custom-duration"
                        type="number"
                        v-model.number="selectedDuration"
                        min="0.5"
                        max="24"
                        step="0.5"
                        label="Custom Hours"
                    />
                </div>

                <div class="bg-light p-3 rounded mb-3">
                    <div class="d-flex justify-content-between mb-2">
                        <span>Rate:</span>
                        <span class="fw-bold">{{ $currency(selectedLot?.price_per_hour) }}/hr</span>
                    </div>

                    <div class="mb-3">
                        <BaseInput
                            id="vehicle-number"
                            v-model="vehicleNumber"
                            label="Vehicle Number"
                            placeholder="Enter vehicle registration number"
                            required
                        />
                    </div>

                    <div class="d-flex justify-content-between border-top pt-2">
                        <span class="fw-bold">Total Cost:</span>
                        <span class="fw-bold text-success fs-5">
                            {{ $currency(selectedDuration * (selectedLot?.price_per_hour || 0)) }}

                        </span>
                    </div>
                </div>

                <template #footer>
                    <BaseButton variant="secondary" @click="closeReservationModal">Cancel</BaseButton>
                    <BaseButton variant="primary" @click="confirmReservation" :loading="!!reserving" :disabled="!!reserving || !vehicleNumber">
                        Confirm Reservation
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
        </div>
    </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
import BaseInput from '../components/common/BaseInput.vue'
import BaseButton from '../components/common/BaseButton.vue'
import BaseBadge from '../components/common/BaseBadge.vue'
import BaseModal from '../components/common/BaseModal.vue'
import PaymentModal from '../components/common/PaymentModal.vue'
import { API_BASE_URL } from '@/config'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const successMessage = ref('')
const parkingLots = ref([])
const userReservations = ref([])
const searchQuery = ref('')
const locationFilter = ref('')
const sortBy = ref('name')
const showReservationModal = ref(false)
const selectedLot = ref(null)
const selectedDuration = ref(2)
const vehicleNumber = ref('')
const reserving = ref(null)
const showPaymentModal = ref(false)
const estimatedCost = ref(0)


const durationOptions = [
    { label: '30m', value: 0.5 },
    { label: '1h', value: 1 },
    { label: '2h', value: 2 },
    { label: '4h', value: 4 },
    { label: '8h', value: 8 },
    { label: '24h', value: 24 }
]

// Computed properties
const totalAvailableSpots = computed(() => {
    return parkingLots.value.reduce((total, lot) => total + lot.available_spots, 0)
})

const uniqueLocations = computed(() => {
    const locations = parkingLots.value.map(lot => lot.location)
    return [...new Set(locations)].sort()
})

const filteredAndSortedLots = computed(() => {
    let filtered = parkingLots.value.map(lot => ({
        ...lot,
        occupied_spots: lot.capacity - lot.available_spots,
        occupancy_rate: ((lot.capacity - lot.available_spots) / lot.capacity) * 100
    }))

    // Filter by search query
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(lot =>
            lot.name.toLowerCase().includes(query) ||
            lot.location.toLowerCase().includes(query)
        )
    }

    // Filter by location
    if (locationFilter.value) {
        filtered = filtered.filter(lot => lot.location === locationFilter.value)
    }

    // Sort
    filtered.sort((a, b) => {
        switch (sortBy.value) {
            case 'price':
                return a.price_per_hour - b.price_per_hour
            case 'availability':
                return b.available_spots - a.available_spots
            default:
                return a.name.localeCompare(b.name)
        }
    })

    return filtered
})

const activeReservations = computed(() => {
    return userReservations.value.filter(res => res.status === 'active')
})

// Data fetching
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
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to fetch parking lots'

            if (response.status === 401 || response.status === 403) {
                router.push('/login')
            }
        }
    } catch (err) {
        console.error('Fetch error:', err)
        error.value = 'Network error. Please try again.'
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

const confirmReservation = () => {
    if (!selectedLot.value) return
    if (!vehicleNumber.value) {
        error.value = 'Vehicle number is required'
        return
    }
    
    // Calculate cost
    estimatedCost.value = selectedLot.value.price_per_hour * selectedDuration.value
    
    // Close reservation modal
    showReservationModal.value = false
    
    // Open payment modal
    showPaymentModal.value = true
}

const handlePaymentSuccess = async () => {
    // Close payment modal
    showPaymentModal.value = false
    
    // Original reservation logic
    await finalizeReservation()
}

const finalizeReservation = async () => {
    if (!selectedLot.value) return
    if (!vehicleNumber.value) {
        error.value = 'Vehicle number is required'
        return
    }

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
                duration_hours: selectedDuration.value,
                vehicle_number: vehicleNumber.value
            })
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Successfully reserved spot ${data.reservation.spot_number} in ${selectedLot.value.name}`

            // Refresh data
            await Promise.all([fetchParkingLots(), fetchUserReservations()])

            closeReservationModal()

            setTimeout(() => {
                successMessage.value = ''
            }, 5000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to reserve spot'
        }
    } catch (err) {
        console.error('Reservation error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        reserving.value = null
    }
}

// Helper functions
const hasActiveReservationInLot = (lotId) => {
    return activeReservations.value.some(res => {
        const lot = parkingLots.value.find(l => l.name === res.parking_lot)
        return lot && lot.id === lotId
    })
}

const getAvailabilityVariant = (lot) => {
    const percentage = (lot.available_spots / lot.capacity) * 100
    if (percentage === 0) return 'secondary'
    if (percentage <= 20) return 'danger'
    if (percentage <= 50) return 'warning'
    return 'success'
}

const getProgressBarClass = (lot) => {
    const percentage = (lot.occupancy_rate)
    if (percentage >= 100) return 'bg-danger'
    if (percentage >= 80) return 'bg-warning'
    return 'bg-success'
}

const closeReservationModal = () => {
    showReservationModal.value = false
    selectedLot.value = null
    selectedDuration.value = 2
    vehicleNumber.value = ''
}

onMounted(async () => {
    loading.value = true
    try {
        await Promise.all([fetchParkingLots(), fetchUserReservations()])
    } catch (err) {
        error.value = 'Failed to load parking data'
    } finally {
        loading.value = false
    }
})
</script>

<style scoped>
/* Scoped styles can be minimal now, as we use Bootstrap classes */
</style>
