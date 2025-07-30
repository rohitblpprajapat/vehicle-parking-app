<template>
    <div class="reservations">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>My Reservations</h3>
            </div>
            <div class="nav-links">
                <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/parking-lots" class="nav-link">Find Parking</router-link>
                <router-link to="/reservations" class="nav-link">My Reservations</router-link>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="content">
            <div class="container">
                <div class="header">
                    <h1>My Parking Reservations</h1>
                    <div class="header-stats">
                        <div class="stat-item">
                            <span class="stat-number">{{ activeReservations.length }}</span>
                            <span class="stat-label">Active</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number">{{ totalReservations }}</span>
                            <span class="stat-label">Total</span>
                        </div>
                    </div>
                </div>

                <!-- Loading State -->
                <div v-if="loading" class="loading">
                    Loading your reservations...
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
                <div class="filters" v-if="!loading && reservations.length > 0">
                    <div class="filter-tabs">
                        <button v-for="status in statusFilters" :key="status.value"
                            @click="selectedStatus = status.value"
                            :class="['filter-tab', { active: selectedStatus === status.value }]">
                            {{ status.label }}
                            <span class="count">({{ getReservationsByStatus(status.value).length }})</span>
                        </button>
                    </div>
                    <div class="search-controls">
                        <input v-model="searchQuery" type="text" placeholder="Search by parking lot..."
                            class="search-input">
                        <select v-model="sortBy" class="sort-select">
                            <option value="recent">Most Recent</option>
                            <option value="oldest">Oldest First</option>
                            <option value="spot">By Spot</option>
                            <option value="cost">By Cost</option>
                        </select>
                    </div>
                </div>

                <!-- Reservations List -->
                <div v-if="!loading && !error" class="reservations-list">
                    <!-- Active Reservations Section -->
                    <div v-if="displayedReservations.filter(r => r.status === 'active').length > 0 && selectedStatus !== 'completed' && selectedStatus !== 'expired'"
                        class="reservations-section">
                        <h2 class="section-title">🟢 Active Reservations</h2>
                        <div class="reservations-grid">
                            <div v-for="reservation in displayedReservations.filter(r => r.status === 'active')"
                                :key="reservation.id" class="reservation-card active">
                                <div class="card-header">
                                    <h3>{{ reservation.parking_lot }}</h3>
                                    <span class="status-badge active">{{ reservation.status }}</span>
                                </div>

                                <div class="card-body">
                                    <div class="reservation-details">
                                        <div class="detail-row">
                                            <span class="label">🅿️ Spot:</span>
                                            <span class="value">{{ reservation.spot_number }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">📅 Reserved:</span>
                                            <span class="value">{{ formatDate(reservation.reservation_time) }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">⏰ Duration:</span>
                                            <span class="value">{{ reservation.duration }} hours</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">💰 Cost:</span>
                                            <span class="value">${{ reservation.cost }}</span>
                                        </div>
                                        <div v-if="reservation.occupied_at" class="detail-row">
                                            <span class="label">🚗 Occupied:</span>
                                            <span class="value">{{ formatDate(reservation.occupied_at) }}</span>
                                        </div>
                                        <div v-if="reservation.expires_at" class="detail-row">
                                            <span class="label">⏰ Expires:</span>
                                            <span class="value expires">{{ formatDate(reservation.expires_at) }}</span>
                                        </div>
                                    </div>
                                </div>

                                <div class="card-actions">
                                    <button v-if="!reservation.occupied_at" @click="occupySpot(reservation)"
                                        :disabled="occupying === reservation.id" class="btn btn-primary">
                                        {{ occupying === reservation.id ? 'Occupying...' : '🚗 Occupy Spot' }}
                                    </button>
                                    <button v-if="reservation.occupied_at" @click="releaseSpot(reservation)"
                                        :disabled="releasing === reservation.id" class="btn btn-success">
                                        {{ releasing === reservation.id ? 'Releasing...' : '🔓 Release Spot' }}
                                    </button>
                                    <button v-if="!reservation.occupied_at" @click="cancelReservation(reservation)"
                                        :disabled="cancelling === reservation.id" class="btn btn-danger">
                                        {{ cancelling === reservation.id ? 'Cancelling...' : '❌ Cancel Booking' }}
                                    </button>
                                    <button @click="extendReservation(reservation)"
                                        :disabled="extending === reservation.id" class="btn btn-secondary">
                                        {{ extending === reservation.id ? 'Extending...' : '⏰ Extend' }}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Completed/Other Reservations Section -->
                    <div v-if="displayedReservations.filter(r => r.status !== 'active').length > 0"
                        class="reservations-section">
                        <h2 class="section-title">📋 Reservation History</h2>
                        <div class="reservations-grid">
                            <div v-for="reservation in displayedReservations.filter(r => r.status !== 'active')"
                                :key="reservation.id" :class="['reservation-card', reservation.status]">
                                <div class="card-header">
                                    <h3>{{ reservation.parking_lot }}</h3>
                                    <span :class="['status-badge', reservation.status]">{{ reservation.status }}</span>
                                </div>

                                <div class="card-body">
                                    <div class="reservation-details">
                                        <div class="detail-row">
                                            <span class="label">🅿️ Spot:</span>
                                            <span class="value">{{ reservation.spot_number }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">📅 Reserved:</span>
                                            <span class="value">{{ formatDate(reservation.reservation_time) }}</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">⏰ Duration:</span>
                                            <span class="value">{{ reservation.duration }} hours</span>
                                        </div>
                                        <div class="detail-row">
                                            <span class="label">💰 Cost:</span>
                                            <span class="value">${{ reservation.cost }}</span>
                                        </div>
                                        <div v-if="reservation.occupied_at" class="detail-row">
                                            <span class="label">🚗 Occupied:</span>
                                            <span class="value">{{ formatDate(reservation.occupied_at) }}</span>
                                        </div>
                                        <div v-if="reservation.released_at" class="detail-row">
                                            <span class="label">🔓 Released:</span>
                                            <span class="value">{{ formatDate(reservation.released_at) }}</span>
                                        </div>
                                        <div v-if="reservation.actual_duration_hours" class="detail-row">
                                            <span class="label">📊 Actual Duration:</span>
                                            <span class="value">{{ reservation.actual_duration_hours }} hours</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-if="!loading && !error && reservations.length === 0" class="empty-state">
                    <div class="empty-icon">🅿️</div>
                    <h3>No reservations yet</h3>
                    <p>You haven't made any parking reservations.</p>
                    <router-link to="/parking-lots" class="btn btn-primary">Find Parking</router-link>
                </div>

                <!-- No Results State -->
                <div v-if="!loading && !error && reservations.length > 0 && displayedReservations.length === 0"
                    class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>No matching reservations</h3>
                    <p>Try adjusting your search or filters.</p>
                </div>

                <!-- Extend Duration Modal -->
                <div v-if="showExtendModal" class="modal-overlay" @click="closeExtendModal">
                    <div class="modal" @click.stop>
                        <div class="modal-header">
                            <h2>Extend Reservation</h2>
                            <button @click="closeExtendModal" class="close-btn">&times;</button>
                        </div>
                        <div class="modal-body">
                            <div class="extend-form">
                                <div class="current-reservation">
                                    <h4>Current Reservation</h4>
                                    <p><strong>{{ selectedReservation?.parking_lot }}</strong> - Spot {{
                                        selectedReservation?.spot_number }}</p>
                                    <p>Expires: {{ formatDate(selectedReservation?.expires_at) }}</p>
                                </div>

                                <div class="form-group">
                                    <label>Additional Duration (hours):</label>
                                    <div class="duration-options">
                                        <button v-for="duration in extendDurationOptions" :key="duration.value"
                                            @click="extendDuration = duration.value"
                                            :class="['duration-btn', { active: extendDuration === duration.value }]">
                                            {{ duration.label }}
                                        </button>
                                    </div>
                                    <input v-model.number="extendDuration" type="number" min="0.5" max="12" step="0.5"
                                        class="custom-duration" placeholder="Custom hours">
                                </div>

                                <div class="extend-calculation">
                                    <div class="cost-row">
                                        <span>Additional Duration:</span>
                                        <span>{{ extendDuration }} hours</span>
                                    </div>
                                    <div class="cost-row">
                                        <span>Rate:</span>
                                        <span>${{ selectedReservation?.hourly_rate || 0 }}/hour</span>
                                    </div>
                                    <div class="cost-row total">
                                        <span>Additional Cost:</span>
                                        <span>${{ (extendDuration * (selectedReservation?.hourly_rate || 0)).toFixed(2)
                                            }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button @click="closeExtendModal" class="btn btn-secondary">Cancel</button>
                            <button @click="confirmExtend" class="btn btn-primary" :disabled="extending">
                                {{ extending ? 'Extending...' : 'Confirm Extension' }}
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
const reservations = ref([])
const searchQuery = ref('')
const selectedStatus = ref('all')
const sortBy = ref('recent')
const occupying = ref(null)
const releasing = ref(null)
const extending = ref(null)
const cancelling = ref(null)
const showExtendModal = ref(false)
const selectedReservation = ref(null)
const extendDuration = ref(2)

const statusFilters = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Completed', value: 'completed' },
    { label: 'Expired', value: 'expired' }
]

const extendDurationOptions = [
    { label: '30 min', value: 0.5 },
    { label: '1 hour', value: 1 },
    { label: '2 hours', value: 2 },
    { label: '4 hours', value: 4 },
    { label: '6 hours', value: 6 }
]

// Computed properties
const totalReservations = computed(() => reservations.value.length)

const activeReservations = computed(() => {
    return reservations.value.filter(res => res.status === 'active')
})

const getReservationsByStatus = (status) => {
    if (status === 'all') return reservations.value
    return reservations.value.filter(res => res.status === status)
}

const filteredReservations = computed(() => {
    let filtered = selectedStatus.value === 'all'
        ? reservations.value
        : reservations.value.filter(res => res.status === selectedStatus.value)

    // Apply search filter
    if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(res =>
            res.parking_lot.toLowerCase().includes(query) ||
            res.spot_number.toString().includes(query)
        )
    }

    return filtered
})

const displayedReservations = computed(() => {
    const filtered = filteredReservations.value

    // Sort reservations
    return filtered.sort((a, b) => {
        switch (sortBy.value) {
            case 'oldest':
                return new Date(a.reservation_time) - new Date(b.reservation_time)
            case 'spot':
                return a.spot_number - b.spot_number
            case 'cost':
                return b.cost - a.cost
            default: // recent
                return new Date(b.reservation_time) - new Date(a.reservation_time)
        }
    })
})

// Data fetching
const fetchReservations = async () => {
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
            reservations.value = data.reservations
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
    }
}

// User actions
const occupySpot = async (reservation) => {
    try {
        occupying.value = reservation.id
        const token = localStorage.getItem('authToken')

        const response = await fetch(`http://127.0.0.1:5000/api/v1/reservations/${reservation.id}/occupy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            successMessage.value = `Successfully occupied spot ${reservation.spot_number}`
            await fetchReservations()

            setTimeout(() => {
                successMessage.value = ''
            }, 5000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to occupy spot'
        }
    } catch (err) {
        console.error('Occupy error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        occupying.value = null
    }
}

const releaseSpot = async (reservation) => {
    try {
        releasing.value = reservation.id
        const token = localStorage.getItem('authToken')

        const response = await fetch(`http://127.0.0.1:5000/api/v1/reservations/${reservation.id}/release`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Successfully released spot ${reservation.spot_number}. Duration: ${data.actual_duration_hours} hours, Final cost: $${data.final_cost}`
            await fetchReservations()

            setTimeout(() => {
                successMessage.value = ''
            }, 8000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to release spot'
        }
    } catch (err) {
        console.error('Release error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        releasing.value = null
    }
}

const extendReservation = (reservation) => {
    selectedReservation.value = reservation
    showExtendModal.value = true
}

const confirmExtend = async () => {
    if (!selectedReservation.value) return

    try {
        extending.value = selectedReservation.value.id
        const token = localStorage.getItem('authToken')

        const response = await fetch(`http://127.0.0.1:5000/api/v1/reservations/${selectedReservation.value.id}/extend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            },
            body: JSON.stringify({
                additional_hours: extendDuration.value
            })
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = `Successfully extended reservation by ${extendDuration.value} hours. New expiry: ${formatDate(data.new_expires_at)}`
            await fetchReservations()
            closeExtendModal()

            setTimeout(() => {
                successMessage.value = ''
            }, 6000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to extend reservation'
        }
    } catch (err) {
        console.error('Extend error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        extending.value = null
    }
}

const cancelReservation = async (reservation) => {
    if (!confirm(`Are you sure you want to cancel your reservation for spot ${reservation.spot_number} at ${reservation.parking_lot}? This action cannot be undone.`)) {
        return
    }

    try {
        cancelling.value = reservation.id
        const token = localStorage.getItem('authToken')

        const response = await fetch(`http://127.0.0.1:5000/api/v1/reservations/${reservation.id}/cancel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            successMessage.value = `Successfully cancelled reservation for spot ${reservation.spot_number}`
            await fetchReservations()

            setTimeout(() => {
                successMessage.value = ''
            }, 5000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to cancel reservation'
        }
    } catch (err) {
        console.error('Cancel error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        cancelling.value = null
    }
}

// Helper functions
const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

const closeExtendModal = () => {
    showExtendModal.value = false
    selectedReservation.value = null
    extendDuration.value = 2
}

const logout = () => {
    authLogout()
    router.push('/login')
}

onMounted(async () => {
    loading.value = true
    try {
        await fetchReservations()
    } catch (err) {
        error.value = 'Failed to load reservation data'
    } finally {
        loading.value = false
    }
})

</script>

<style scoped>
.reservations {
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
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.filter-tab {
    background: #f8f9fa;
    border: 2px solid #e9ecef;
    color: #6c757d;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-weight: 500;
}

.filter-tab:hover {
    border-color: #28a745;
    color: #28a745;
}

.filter-tab.active {
    background: #28a745;
    border-color: #28a745;
    color: white;
}

.count {
    font-size: 0.8rem;
    opacity: 0.8;
}

.search-controls {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.search-input,
.sort-select {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    font-size: 0.9rem;
}

.search-input {
    flex: 1;
    min-width: 250px;
}

.sort-select {
    min-width: 150px;
}

.reservations-list {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.reservations-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section-title {
    color: #333;
    margin: 0 0 1.5rem 0;
    font-size: 1.3rem;
    font-weight: 600;
}

.reservations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
}

.reservation-card {
    background: white;
    border-radius: 12px;
    border: 2px solid #e9ecef;
    overflow: hidden;
    transition: all 0.3s ease;
}

.reservation-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.reservation-card.active {
    border-color: #28a745;
    background: linear-gradient(135deg, #fff 0%, #f8fff9 100%);
}

.reservation-card.completed {
    border-color: #6c757d;
    opacity: 0.9;
}

.reservation-card.expired {
    border-color: #dc3545;
    background: linear-gradient(135deg, #fff 0%, #fff8f8 100%);
}

.card-header {
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header h3 {
    margin: 0;
    color: #333;
    font-size: 1.1rem;
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

.status-badge.completed {
    background: #d1ecf1;
    color: #0c5460;
}

.status-badge.expired {
    background: #f8d7da;
    color: #721c24;
}

.card-body {
    padding: 1.5rem;
}

.reservation-details {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid #f8f9fa;
}

.detail-row:last-child {
    border-bottom: none;
}

.label {
    font-weight: 500;
    color: #6c757d;
    font-size: 0.9rem;
}

.value {
    font-weight: 600;
    color: #333;
}

.value.expires {
    color: #dc3545;
    font-weight: 700;
}

.card-actions {
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: white;
    border-radius: 12px;
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

.extend-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.current-reservation {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.current-reservation h4 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.current-reservation p {
    margin: 0.25rem 0;
    color: #6c757d;
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

.extend-calculation {
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
    text-align: center;
    flex: 1;
}

.btn-primary {
    background: #28a745;
    color: white;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-success {
    background: #20c997;
    color: white;
}

.btn-danger {
    background: #dc3545;
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
