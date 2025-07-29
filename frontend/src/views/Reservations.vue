<template>
    <div class="reservations">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>My Reservations</h3>
            </div>
            <div class="nav-links">
                <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/parking-lots" class="nav-link">Parking Lots</router-link>
                <router-link to="/reservations" class="nav-link">My Reservations</router-link>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="content">
            <div class="container">
                <div class="header">
                    <h1>My Reservations</h1>
                    <router-link to="/parking-lots" class="btn btn-primary">Make New Reservation</router-link>
                </div>

                <div class="filters">
                    <select v-model="statusFilter" class="status-filter">
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="upcoming">Upcoming</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                    </select>
                </div>

                <div class="reservations-list" v-if="filteredReservations.length > 0">
                    <div v-for="reservation in filteredReservations" :key="reservation.id" class="reservation-card">
                        <div class="reservation-header">
                            <h3>{{ reservation.parkingLot }}</h3>
                            <span class="status" :class="reservation.status">
                                {{ reservation.status.toUpperCase() }}
                            </span>
                        </div>

                        <div class="reservation-details">
                            <div class="detail-item">
                                <span class="label">📍 Location:</span>
                                <span>{{ reservation.location }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">🚗 Spot:</span>
                                <span>{{ reservation.spotNumber }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">📅 Date:</span>
                                <span>{{ formatDate(reservation.date) }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">⏰ Time:</span>
                                <span>{{ reservation.startTime }} - {{ reservation.endTime }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">💰 Total Cost:</span>
                                <span>${{ reservation.totalCost }}</span>
                            </div>
                        </div>

                        <div class="reservation-actions">
                            <button v-if="reservation.status === 'upcoming'" @click="cancelReservation(reservation.id)"
                                class="btn btn-danger">
                                Cancel
                            </button>
                            <button v-if="reservation.status === 'active'" @click="extendReservation(reservation.id)"
                                class="btn btn-secondary">
                                Extend
                            </button>
                            <button @click="viewDetails(reservation)" class="btn btn-outline">
                                View Details
                            </button>
                        </div>
                    </div>
                </div>

                <div v-else class="no-reservations">
                    <h3>No reservations found</h3>
                    <p>You don't have any reservations yet.</p>
                    <router-link to="/parking-lots" class="btn btn-primary">Find Parking</router-link>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const statusFilter = ref('')
const reservations = ref([
    {
        id: 1,
        parkingLot: 'Central Plaza Parking',
        location: 'Downtown',
        spotNumber: 'A-15',
        date: '2025-07-29',
        startTime: '09:00',
        endTime: '17:00',
        totalCost: 40,
        status: 'active'
    },
    {
        id: 2,
        parkingLot: 'Mall Parking Garage',
        location: 'Shopping Mall',
        spotNumber: 'B-32',
        date: '2025-07-30',
        startTime: '14:00',
        endTime: '18:00',
        totalCost: 12,
        status: 'upcoming'
    },
    {
        id: 3,
        parkingLot: 'City Center Parking',
        location: 'Downtown',
        spotNumber: 'C-08',
        date: '2025-07-25',
        startTime: '10:00',
        endTime: '16:00',
        totalCost: 36,
        status: 'completed'
    }
])

// Computed properties
const filteredReservations = computed(() => {
    if (!statusFilter.value) return reservations.value
    return reservations.value.filter(reservation =>
        reservation.status === statusFilter.value
    )
})

// Methods
const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}

const cancelReservation = (reservationId) => {
    if (confirm('Are you sure you want to cancel this reservation?')) {
        const reservation = reservations.value.find(r => r.id === reservationId)
        if (reservation) {
            reservation.status = 'cancelled'
            alert('Reservation cancelled successfully')
        }
    }
}

const extendReservation = (reservationId) => {
    alert(`Extending reservation ${reservationId}`)
    // Here you would typically open a form to extend the reservation
}

const viewDetails = (reservation) => {
    alert(`Viewing details for reservation at ${reservation.parkingLot}`)
    // Here you could navigate to a detailed view or show a modal
}

const logout = () => {
    localStorage.removeItem('authToken')
    router.push('/login')
}

onMounted(() => {
    // Fetch reservations data from API
    console.log('Reservations page mounted')
})
</script>

<style scoped>
.reservations {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.navbar {
    background: white;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand h3 {
    color: #667eea;
    margin: 0;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 1rem;
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
    flex-wrap: wrap;
    gap: 1rem;
}

.header h1 {
    margin: 0;
    color: #333;
}

.filters {
    margin-bottom: 2rem;
}

.status-filter {
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    min-width: 150px;
}

.reservations-list {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.reservation-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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

.status {
    font-size: 0.8rem;
    font-weight: bold;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
}

.status.active {
    background-color: #d4edda;
    color: #155724;
}

.status.upcoming {
    background-color: #cce5ff;
    color: #004085;
}

.status.completed {
    background-color: #d1ecf1;
    color: #0c5460;
}

.status.cancelled {
    background-color: #f8d7da;
    color: #721c24;
}

.reservation-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.detail-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.label {
    font-weight: 600;
    color: #666;
    font-size: 0.9rem;
}

.reservation-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.btn {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.3s;
    text-decoration: none;
    text-align: center;
}

.btn-primary {
    background-color: #667eea;
    color: white;
}

.btn-primary:hover {
    background-color: #5a67d8;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #5a6268;
}

.btn-danger {
    background-color: #dc3545;
    color: white;
}

.btn-danger:hover {
    background-color: #c82333;
}

.btn-outline {
    background-color: transparent;
    color: #667eea;
    border: 1px solid #667eea;
}

.btn-outline:hover {
    background-color: #667eea;
    color: white;
}

.no-reservations {
    text-align: center;
    padding: 3rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.no-reservations h3 {
    color: #666;
    margin-bottom: 1rem;
}

.no-reservations p {
    color: #999;
    margin-bottom: 2rem;
}
</style>
