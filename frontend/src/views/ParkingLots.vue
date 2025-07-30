<template>
    <div class="parking-lots">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Find Parking</h3>
            </div>
            <div class="nav-links">
                <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/parking-lots" class="nav-link">Find Parking</router-link>
                <router-link to="/reservations" class="nav-link">My Reservations</router-link>
                <router-link to="/profile" class="nav-link">Profile</router-link>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="content">
            <div class="container">
                <div class="header">
                    <h1>Available Parking Lots</h1>
                    <div class="header-stats">
                        <div class="stat-item">
                            <span class="stat-number">{{ totalAvailableSpots }}</span>
                            <span class="stat-label">Available Spots</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{{ parkingLots.length }}</span>
                            <span class="stat-label">Parking Lots</span>
                        </div>
                    </div>
                </div>

                <!-- Loading State -->
                <div v-if="loading" class="loading">
                    Loading parking lots...
                </div>

                <!-- Error State -->
                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <!-- Success Message -->
                <div v-if="successMessage" class="success-message">
                    {{ successMessage }}
                </div>

                <!-- Filters -->
                <div class="filters">
                    <input v-model="searchQuery" type="text" placeholder="Search by name or location..."
                        class="search-input">
                    <select v-model="locationFilter" class="location-filter">
                        <option value="">All Locations</option>
                        <option v-for="location in uniqueLocations" :key="location" :value="location">
                            {{ location }}
                        </option>
                    </select>
                    <select v-model="sortBy" class="sort-filter">
                        <option value="name">Sort by Name</option>
                        <option value="price">Sort by Price</option>
                        <option value="availability">Sort by Availability</option>
                        <option value="distance">Sort by Distance</option>
                    </select>
                </div>

                <!-- Parking Lots Grid -->
                <div v-if="!loading && !error" class="lots-grid">
                    <div v-for="lot in filteredAndSortedLots" :key="lot.id" class="lot-card">
                        <div class="lot-header">
                            <h3>{{ lot.name }}</h3>
                            <div class="lot-badges">
                                <span :class="['availability-badge', getAvailabilityClass(lot)]">
                                    {{ lot.available_spots }}/{{ lot.capacity }} available
                                </span>
                                <span class="price-badge">${{ lot.price_per_hour }}/hr</span>
                            </div>
                        </div>

                        <div class="lot-info">
                            <p class="location">📍 {{ lot.location }}</p>
                            <div class="occupancy-display">
                                <div class="occupancy-bar">
                                    <div class="occupancy-fill" :style="{ width: (lot.occupancy_rate || 0) + '%' }">
                                    </div>
                                </div>
                                <span class="occupancy-text">{{ (lot.occupancy_rate || 0).toFixed(1) }}% occupied</span>
                            </div>
                        </div>

                        <div class="lot-stats">
                            <div class="stat">
                                <span class="stat-value">{{ lot.capacity }}</span>
                                <span class="stat-label">Total Spots</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{{ lot.available_spots }}</span>
                                <span class="stat-label">Available</span>
                            </div>
                            <div class="stat">
                                <span class="stat-value">{{ lot.occupied_spots }}</span>
                                <span class="stat-label">Occupied</span>
                            </div>
                        </div>

                        <div class="lot-actions">
                            <button @click="viewLotDetails(lot)" class="btn btn-secondary">
                                View Layout
                            </button>
                            <button @click="quickReserve(lot)"
                                :disabled="lot.available_spots === 0 || hasActiveReservationInLot(lot.id) || reserving === lot.id"
                                class="btn btn-primary">
                                <span v-if="reserving === lot.id">Reserving...</span>
                                <span v-else-if="lot.available_spots === 0">Full</span>
                                <span v-else-if="hasActiveReservationInLot(lot.id)">Already Reserved</span>
                                <span v-else>Reserve Now</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-if="!loading && !error && filteredAndSortedLots.length === 0" class="empty-state">
                    <div class="empty-icon">🅿️</div>
                    <h3>No parking lots found</h3>
                    <p>Try adjusting your search criteria or filters.</p>
                </div>

                <!-- Reservation Duration Modal -->
                <div v-if="showReservationModal" class="modal-overlay" @click="closeReservationModal">
                    <div class="modal" @click.stop>
                        <div class="modal-header">
                            <h2>Reserve Spot - {{ selectedLot?.name }}</h2>
                            <button @click="closeReservationModal" class="close-btn">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="reservation-form">
                                <div class="form-group">
                                    <label>Duration (hours):</label>
                                    <div class="duration-options">
                                        <button v-for="duration in durationOptions" :key="duration.value"
                                            @click="selectedDuration = duration.value"
                                            :class="['duration-btn', { active: selectedDuration === duration.value }]">
                                            {{ duration.label }}
                                        </button>
                                    </div>
                                    <input v-model.number="selectedDuration" type="number" min="0.5" max="24" step="0.5"
                                        class="custom-duration" placeholder="Custom hours">
                                </div>
                                <div class="cost-calculation">
                                    <div class="cost-row">
                                        <span>Duration:</span>
                                        <span>{{ selectedDuration }} hours</span>
                                    </div>
                                    <div class="cost-row">
                                        <span>Rate:</span>
                                        <span>${{ selectedLot?.price_per_hour }}/hour</span>
                                    </div>
                                    <div class="cost-row total">
                                        <span>Total Cost:</span>
                                        <span>${{ (selectedDuration * (selectedLot?.price_per_hour || 0)).toFixed(2)
                                            }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button @click="closeReservationModal" class="btn btn-secondary">Cancel</button>
                            <button @click="confirmReservation" class="btn btn-primary" :disabled="reserving">
                                {{ reserving ? 'Reserving...' : 'Confirm Reservation' }}
                            </button>
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
import { logout as authLogout } from '../utils/auth.js'

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
const reserving = ref(null)

const durationOptions = [
    { label: '30 min', value: 0.5 },
    { label: '1 hour', value: 1 },
    { label: '2 hours', value: 2 },
    { label: '4 hours', value: 4 },
    { label: '8 hours', value: 8 },
    { label: '24 hours', value: 24 }
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
            case 'distance':
                // For now, just sort by name as we don't have distance data
                return a.name.localeCompare(b.name)
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
        const token = localStorage.getItem('authToken')
        const response = await fetch('http://127.0.0.1:5000/api/v1/parking-lots', {
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
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
        const token = localStorage.getItem('authToken')
        const response = await fetch('http://127.0.0.1:5000/api/v1/reservations', {
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
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
        return
    }

    selectedLot.value = lot
    showReservationModal.value = true
}

const confirmReservation = async () => {
    if (!selectedLot.value) return

    try {
        reserving.value = selectedLot.value.id
        const token = localStorage.getItem('authToken')

        const response = await fetch('http://127.0.0.1:5000/api/v1/reservations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            },
            body: JSON.stringify({
                lot_id: selectedLot.value.id,
                duration_hours: selectedDuration.value
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

const viewLotDetails = (lot) => {
    router.push(`/parking-lots/${lot.id}`)
}

// Helper functions
const hasActiveReservationInLot = (lotId) => {
    return activeReservations.value.some(res => {
        const lot = parkingLots.value.find(l => l.name === res.parking_lot)
        return lot && lot.id === lotId
    })
}

const getAvailabilityClass = (lot) => {
    const percentage = (lot.available_spots / lot.capacity) * 100
    if (percentage === 0) return 'full'
    if (percentage <= 20) return 'low'
    if (percentage <= 50) return 'medium'
    return 'high'
}

const closeReservationModal = () => {
    showReservationModal.value = false
    selectedLot.value = null
    selectedDuration.value = 2
}

const logout = () => {
    authLogout()
    router.push('/login')
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
.parking-lots {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.navbar {
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
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
    max-width: 1200px;
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
    gap: 2rem;
}

.stat-item {
    text-align: center;
}

.stat-number {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    color: #28a745;
}

.stat-label {
    display: block;
    font-size: 0.85rem;
    color: #6c757d;
    text-transform: uppercase;
}

.loading,
.error-message,
.success-message {
    text-align: center;
    padding: 1rem;
    border-radius: 8px;
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

.filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.search-input,
.location-filter,
.sort-filter {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    font-size: 0.9rem;
    min-width: 200px;
}

.lots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
}

.lot-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #e9ecef;
    transition: all 0.3s ease;
}

.lot-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.lot-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.lot-header h3 {
    margin: 0;
    color: #333;
    font-size: 1.2rem;
}

.lot-badges {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-end;
}

.availability-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.availability-badge.high {
    background: #d4edda;
    color: #155724;
}

.availability-badge.medium {
    background: #fff3cd;
    color: #856404;
}

.availability-badge.low {
    background: #f8d7da;
    color: #721c24;
}

.availability-badge.full {
    background: #d1ecf1;
    color: #0c5460;
}

.price-badge {
    background: #28a745;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.lot-info {
    margin-bottom: 1rem;
}

.location {
    color: #6c757d;
    margin: 0 0 1rem 0;
    font-size: 0.9rem;
}

.occupancy-display {
    margin-bottom: 1rem;
}

.occupancy-bar {
    width: 100%;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.occupancy-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745 0%, #ffc107 60%, #dc3545 100%);
    transition: width 0.3s ease;
}

.occupancy-text {
    font-size: 0.8rem;
    color: #6c757d;
}

.lot-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.stat {
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 1.2rem;
    font-weight: 700;
    color: #333;
}

.stat-label {
    display: block;
    font-size: 0.75rem;
    color: #6c757d;
    text-transform: uppercase;
}

.lot-actions {
    display: flex;
    gap: 0.75rem;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #6c757d;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

/* Modal Styles */
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

.modal {
    background: white;
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
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
}

.reservation-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: #333;
}

.duration-options {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.duration-btn {
    padding: 0.75rem;
    border: 2px solid #e9ecef;
    background: white;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.duration-btn:hover {
    border-color: #28a745;
}

.duration-btn.active {
    background: #28a745;
    color: white;
    border-color: #28a745;
}

.custom-duration {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    font-size: 0.9rem;
}

.cost-calculation {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
}

.cost-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.cost-row.total {
    border-top: 1px solid #dee2e6;
    padding-top: 0.5rem;
    margin-top: 0.5rem;
    font-weight: 700;
    font-size: 1.1rem;
    color: #28a745;
}

.modal-footer {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    padding: 1.5rem;
    border-top: 1px solid #e9ecef;
}

/* Buttons */
.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 500;
    transition: all 0.3s ease;
    font-size: 0.9rem;
    flex: 1;
    text-align: center;
}

.btn-primary {
    background: #28a745;
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
