<template>
    <div class="dashboard">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Parking Dashboard</h3>
            </div>
            <div class="nav-links">
                <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/parking-lots" class="nav-link">Find Parking</router-link>
                <router-link to="/reservations" class="nav-link">My Reservations</router-link>
                <span class="user-info">Welcome, {{ userInfo.name }}</span>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="dashboard-content">
            <div class="container">
                <h1>Welcome to Your Dashboard</h1>

                <!-- Loading State -->
                <div v-if="loading" class="loading">
                    Loading dashboard data...
                </div>

                <!-- Error State -->
                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <!-- Success Message -->
                <div v-if="successMessage" class="success-message">
                    {{ successMessage }}
                </div>

                <!-- Quick Stats -->
                <div class="stats-grid">
                    <div class="stat-card available">
                        <div class="stat-icon">🅿️</div>
                        <h3>Available Spots</h3>
                        <p class="stat-number">{{ availableSpots }}</p>
                    </div>
                    <div class="stat-card reservations">
                        <div class="stat-icon">📅</div>
                        <h3>My Reservations</h3>
                        <p class="stat-number">{{ userReservations.length }}</p>
                    </div>
                    <div class="stat-card active">
                        <div class="stat-icon">🚗</div>
                        <h3>Active Bookings</h3>
                        <p class="stat-number">{{ activeReservations }}</p>
                    </div>
                    <div class="stat-card lots">
                        <div class="stat-icon">🏢</div>
                        <h3>Parking Lots</h3>
                        <p class="stat-number">{{ parkingLots.length }}</p>
                    </div>
                </div>

                <!-- Active Reservations Section -->
                <div v-if="activeReservationsList.length > 0" class="active-reservations-section">
                    <h2>Active Reservations</h2>
                    <div class="reservations-grid">
                        <div v-for="reservation in activeReservationsList" :key="reservation.id"
                            class="reservation-card active">
                            <div class="reservation-header">
                                <h3>{{ reservation.parking_lot }}</h3>
                                <span class="status-badge active">Active</span>
                            </div>
                            <div class="reservation-details">
                                <div class="detail-row">
                                    <span class="label">Spot:</span>
                                    <span class="value">{{ reservation.spot_number }}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="label">Started:</span>
                                    <span class="value">{{ formatDateTime(reservation.start_time) }}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="label">Ends:</span>
                                    <span class="value">{{ formatDateTime(reservation.end_time) }}</span>
                                </div>
                            </div>
                            <div class="reservation-actions">
                                <button @click="occupySpot(reservation)" class="btn btn-success btn-sm">
                                    Mark as Occupied
                                </button>
                                <button @click="extendReservation(reservation)" class="btn btn-warning btn-sm">
                                    Extend (+1hr)
                                </button>
                                <button @click="releaseSpot(reservation)" class="btn btn-danger btn-sm">
                                    Release Spot
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Booking Section -->
                <div class="quick-booking-section">
                    <h2>Quick Booking</h2>
                    <div class="lots-grid">
                        <div v-for="lot in parkingLots" :key="lot.id" class="lot-card">
                            <div class="lot-header">
                                <h3>{{ lot.name }}</h3>
                                <span class="price">${{ lot.price_per_hour }}/hour</span>
                            </div>
                            <p class="location">📍 {{ lot.location }}</p>

                            <div class="availability-info">
                                <div class="availability-bar">
                                    <div class="availability-fill"
                                        :style="{ width: (lot.available_spots / lot.capacity * 100) + '%' }"></div>
                                </div>
                                <div class="availability-text">
                                    {{ lot.available_spots }} of {{ lot.capacity }} spots available
                                </div>
                            </div>

                            <div class="lot-actions">
                                <router-link :to="`/parking-lots`" class="btn btn-secondary btn-sm">
                                    View Details
                                </router-link>
                                <button @click="quickReserve(lot)"
                                    :disabled="lot.available_spots === 0 || hasActiveReservationInLot(lot.id)"
                                    class="btn btn-primary btn-sm">
                                    {{ lot.available_spots === 0 ? 'Full' : hasActiveReservationInLot(lot.id) ?
                                        'Reserved' : 'Reserve Now' }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recent History -->
                <div class="recent-history-section">
                    <div class="section-header">
                        <h2>Recent Parking History</h2>
                        <router-link to="/reservations" class="btn btn-link">View All</router-link>
                    </div>
                    <div v-if="recentReservations.length === 0" class="no-data">
                        No parking history yet. Book your first spot above!
                    </div>
                    <div v-else class="history-list">
                        <div v-for="reservation in recentReservations" :key="reservation.id" class="history-item">
                            <div class="history-main">
                                <h4>{{ reservation.parking_lot }}</h4>
                                <span :class="['status-badge', reservation.status]">{{ reservation.status }}</span>
                            </div>
                            <div class="history-details">
                                <span>Spot {{ reservation.spot_number }}</span>
                                <span>{{ formatDate(reservation.created_at) }}</span>
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
import { logout as authLogout, getUserInfo } from '../utils/auth.js'

const router = useRouter()
const userInfo = ref({})
const loading = ref(true)
const error = ref('')
const successMessage = ref('')
const parkingLots = ref([])
const userReservations = ref([])

// Get user info
userInfo.value = getUserInfo()

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
        .slice(0, 5) // Show last 5 completed reservations
})

// Data fetching functions
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
            console.error('Failed to fetch parking lots')
        }
    } catch (err) {
        console.error('Error fetching parking lots:', err)
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
        } else {
            console.error('Failed to fetch reservations')
        }
    } catch (err) {
        console.error('Error fetching reservations:', err)
    }
}

// User actions
const quickReserve = async (lot) => {
    if (hasActiveReservationInLot(lot.id)) {
        error.value = 'You already have an active reservation in this parking lot'
        return
    }

    try {
        const token = localStorage.getItem('authToken')
        const response = await fetch('http://127.0.0.1:5000/api/v1/reservations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            },
            body: JSON.stringify({
                lot_id: lot.id,
                duration_hours: 2 // Default 2 hours
            })
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Successfully reserved spot ${data.reservation.spot_number} in ${lot.name}`

            // Refresh data
            await Promise.all([fetchParkingLots(), fetchUserReservations()])

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
    }
}

const occupySpot = async (reservation) => {
    try {
        const token = localStorage.getItem('authToken')
        const response = await fetch(`http://127.0.0.1:5000/api/v1/reservations/${reservation.id}/occupy`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            successMessage.value = 'Spot marked as occupied'
            await fetchUserReservations()

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to occupy spot'
        }
    } catch (err) {
        console.error('Occupy error:', err)
        error.value = 'Network error. Please try again.'
    }
}

const releaseSpot = async (reservation) => {
    if (!confirm('Are you sure you want to release this spot? This action cannot be undone.')) {
        return
    }

    try {
        const token = localStorage.getItem('authToken')
        const response = await fetch(`http://127.0.0.1:5000/api/v1/reservations/${reservation.id}/release`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Spot released successfully. Duration: ${data.reservation.duration_hours}h, Cost: $${data.reservation.total_cost}`

            // Refresh data
            await Promise.all([fetchParkingLots(), fetchUserReservations()])

            setTimeout(() => {
                successMessage.value = ''
            }, 5000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to release spot'
        }
    } catch (err) {
        console.error('Release error:', err)
        error.value = 'Network error. Please try again.'
    }
}

const extendReservation = async (reservation) => {
    try {
        const token = localStorage.getItem('authToken')
        const response = await fetch(`http://127.0.0.1:5000/api/v1/reservations/${reservation.id}/extend`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            },
            body: JSON.stringify({
                additional_hours: 1
            })
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Reservation extended by 1 hour. Additional cost: $${data.reservation.additional_cost}`
            await fetchUserReservations()

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to extend reservation'
        }
    } catch (err) {
        console.error('Extend error:', err)
        error.value = 'Network error. Please try again.'
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

// Logout function
const logout = () => {
    authLogout()
    router.push('/login')
}

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
.dashboard {
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

/* Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
    border-left: 4px solid #28a745;
    transition: transform 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-card.available {
    border-left-color: #28a745;
}

.stat-card.reservations {
    border-left-color: #007bff;
}

.stat-card.active {
    border-left-color: #ffc107;
}

.stat-card.lots {
    border-left-color: #6f42c1;
}

.stat-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.stat-card h3 {
    margin: 0.5rem 0;
    color: #6c757d;
    font-size: 0.9rem;
    text-transform: uppercase;
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #28a745;
    margin: 0;
}

/* Active Reservations */
.active-reservations-section {
    margin-bottom: 2rem;
}

.active-reservations-section h2 {
    color: #333;
    margin-bottom: 1rem;
}

.reservations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
}

.reservation-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #ffc107;
}

.reservation-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.reservation-header h3 {
    margin: 0;
    color: #333;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.75rem;
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

.reservation-details {
    margin-bottom: 1rem;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.detail-row .label {
    font-weight: 600;
    color: #6c757d;
}

.detail-row .value {
    color: #333;
}

.reservation-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

/* Quick Booking */
.quick-booking-section {
    margin-bottom: 2rem;
}

.quick-booking-section h2 {
    color: #333;
    margin-bottom: 1rem;
}

.lots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.lot-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease;
}

.lot-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
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
}

.price {
    background: #28a745;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.location {
    color: #6c757d;
    margin: 0 0 1rem 0;
}

.availability-info {
    margin-bottom: 1rem;
}

.availability-bar {
    width: 100%;
    height: 8px;
    background: #e9ecef;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}

.availability-fill {
    height: 100%;
    background: linear-gradient(90deg, #dc3545 0%, #ffc107 50%, #28a745 100%);
    transition: width 0.3s ease;
}

.availability-text {
    font-size: 0.85rem;
    color: #6c757d;
    text-align: center;
}

.lot-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: space-between;
}

/* Recent History */
.recent-history-section {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.section-header h2 {
    margin: 0;
    color: #333;
}

.no-data {
    text-align: center;
    color: #6c757d;
    padding: 2rem;
    font-style: italic;
}

.history-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.history-item {
    padding: 1rem;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    background: #f8f9fa;
}

.history-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.history-main h4 {
    margin: 0;
    color: #333;
    font-size: 0.95rem;
}

.history-details {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
    color: #6c757d;
}

/* Buttons */
.btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 500;
    transition: all 0.3s ease;
    font-size: 0.85rem;
}

.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
}

.btn-primary {
    background: #007bff;
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-success {
    background: #28a745;
    color: white;
}

.btn-warning {
    background: #ffc107;
    color: #212529;
}

.btn-danger {
    background: #dc3545;
    color: white;
}

.btn-link {
    background: none;
    color: #007bff;
    text-decoration: none;
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
.nav-brand h3 {
color: #667eea;
margin: 0;
}

.nav-links {
display: flex;
align-items: center;
gap: 1rem;
}

.user-info {
color: #333;
font-weight: 500;
background-color: #f8f9fa;
padding: 0.5rem 1rem;
border-radius: 4px;
}

.nav-link {
text-decoration: none;
color: #333;
padding: 0.5rem 1rem;
border-radius: 4px;
transition: background-color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-active {
background-color: #667eea;
color: white;
}

.btn-logout {
background-color: #dc3545;
color: white;
border: none;
padding: 0.5rem 1rem;
border-radius: 4px;
cursor: pointer;
}

.btn-logout:hover {
background-color: #c82333;
}

.dashboard-content {
padding: 2rem;
}

.container {
max-width: 1200px;
margin: 0 auto;
}

.dashboard-content h1 {
margin-bottom: 2rem;
color: #333;
}

.stats-grid {
display: grid;
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
gap: 1.5rem;
margin-bottom: 3rem;
}

.stat-card {
background: white;
padding: 1.5rem;
border-radius: 8px;
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
text-align: center;
}

.stat-card h3 {
color: #666;
margin-bottom: 1rem;
font-size: 1rem;
}

.stat-number {
font-size: 2.5rem;
font-weight: bold;
color: #667eea;
margin: 0;
}

.quick-actions h2 {
margin-bottom: 1rem;
color: #333;
}

.action-buttons {
display: flex;
gap: 1rem;
flex-wrap: wrap;
}

.btn {
padding: 12px 24px;
border-radius: 6px;
text-decoration: none;
font-weight: 600;
transition: all 0.3s ease;
border: none;
cursor: pointer;
}

.btn-primary {
background-color: #667eea;
color: white;
}

.btn-primary:hover {
background-color: #5a67d8;
}

.btn-secondary {
