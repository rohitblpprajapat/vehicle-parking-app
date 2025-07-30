<template>
    <div class="parking-lot-details">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Parking Lot Details</h3>
            </div>
            <div class="nav-links">
                <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/admin/parking-lots" class="nav-link">Manage Lots</router-link>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="content">
            <div class="container">
                <!-- Loading State -->
                <div v-if="loading" class="loading">
                    Loading parking lot details...
                </div>

                <!-- Error State -->
                <div v-if="error" class="error-message">
                    {{ error }}
                </div>

                <!-- Parking Lot Details -->
                <div v-if="!loading && !error && parkingLot" class="details-container">
                    <!-- Header Section -->
                    <div class="details-header">
                        <div class="header-info">
                            <h1>{{ parkingLot.name }}</h1>
                            <p class="location">{{ parkingLot.location }}</p>
                        </div>
                        <div class="header-actions">
                            <router-link to="/admin/parking-lots" class="btn btn-secondary">
                                ← Back to Lots
                            </router-link>
                        </div>
                    </div>

                    <!-- Summary Cards -->
                    <div class="summary-grid">
                        <div class="summary-card">
                            <div class="card-icon capacity-icon">🏗️</div>
                            <div class="card-content">
                                <h3>Total Capacity</h3>
                                <p class="card-value">{{ parkingLot.capacity }}</p>
                                <span class="card-label">spots</span>
                            </div>
                        </div>
                        <div class="summary-card">
                            <div class="card-icon available-icon">✅</div>
                            <div class="card-content">
                                <h3>Available</h3>
                                <p class="card-value available">{{ parkingLot.available_spots }}</p>
                                <span class="card-label">spots</span>
                            </div>
                        </div>
                        <div class="summary-card">
                            <div class="card-icon occupied-icon">🚗</div>
                            <div class="card-content">
                                <h3>Occupied</h3>
                                <p class="card-value occupied">{{ parkingLot.occupied_spots }}</p>
                                <span class="card-label">spots</span>
                            </div>
                        </div>
                        <div class="summary-card">
                            <div class="card-icon price-icon">💰</div>
                            <div class="card-content">
                                <h3>Price per Hour</h3>
                                <p class="card-value price">${{ parkingLot.price_per_hour }}</p>
                                <span class="card-label">per hour</span>
                            </div>
                        </div>
                    </div>

                    <!-- Occupancy Overview -->
                    <div class="occupancy-section">
                        <h2>Occupancy Overview</h2>
                        <div class="occupancy-bar-large">
                            <div class="occupancy-fill-large" :style="{ width: parkingLot.occupancy_rate + '%' }"></div>
                        </div>
                        <p class="occupancy-text">
                            {{ parkingLot.occupancy_rate.toFixed(1) }}% occupied
                            ({{ parkingLot.occupied_spots }} of {{ parkingLot.capacity }} spots)
                        </p>
                    </div>

                    <!-- Parking Spots Grid -->
                    <div class="spots-section">
                        <h2>Parking Spots Layout</h2>
                        <div class="spots-legend">
                            <div class="legend-item">
                                <div class="spot-indicator available"></div>
                                <span>Available</span>
                            </div>
                            <div class="legend-item">
                                <div class="spot-indicator occupied"></div>
                                <span>Occupied</span>
                            </div>
                        </div>
                        <div class="spots-grid">
                            <div v-for="spot in parkingLot.spots" :key="spot.id"
                                :class="['spot', { 'occupied': spot.is_occupied }]"
                                :title="`Spot ${spot.spot_number} - ${spot.is_occupied ? 'Occupied' : 'Available'}`">
                                {{ spot.spot_number }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref('')
const parkingLot = ref(null)

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
        const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/parking-lots/${lotId}/spots`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            parkingLot.value = {
                ...data.parking_lot,
                spots: data.spots,
                occupied_spots: data.spots.filter(spot => spot.is_occupied).length,
                available_spots: data.spots.filter(spot => !spot.is_occupied).length,
                occupancy_rate: (data.spots.filter(spot => spot.is_occupied).length / data.parking_lot.capacity * 100)
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

const logout = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('userEmail')
    router.push('/login')
}

onMounted(() => {
    fetchParkingLotDetails()
})
</script>

<style scoped>
.parking-lot-details {
    min-height: 100vh;
    background-color: #f8f9fa;
}

.navbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.loading,
.error-message {
    text-align: center;
    padding: 2rem;
    border-radius: 8px;
    margin-bottom: 2rem;
}

.error-message {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.details-container {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.details-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid #e9ecef;
}

.header-info h1 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
    font-size: 2rem;
}

.location {
    color: #6c757d;
    font-size: 1.1rem;
    font-style: italic;
    margin: 0;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.summary-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.summary-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.card-icon {
    font-size: 2rem;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
}

.capacity-icon {
    background: #e3f2fd;
}

.available-icon {
    background: #e8f5e8;
}

.occupied-icon {
    background: #ffebee;
}

.price-icon {
    background: #fff3e0;
}

.card-content h3 {
    margin: 0 0 0.5rem 0;
    color: #495057;
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
}

.card-value {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c3e50;
}

.card-value.available {
    color: #28a745;
}

.card-value.occupied {
    color: #dc3545;
}

.card-value.price {
    color: #667eea;
}

.card-label {
    color: #6c757d;
    font-size: 0.85rem;
}

.occupancy-section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.occupancy-section h2 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
}

.occupancy-bar-large {
    width: 100%;
    height: 20px;
    background: #e9ecef;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.occupancy-fill-large {
    height: 100%;
    background: linear-gradient(90deg, #28a745 0%, #ffc107 60%, #fd7e14 80%, #dc3545 100%);
    transition: width 0.5s ease;
    border-radius: 10px;
}

.occupancy-text {
    text-align: center;
    color: #495057;
    font-weight: 600;
    margin: 0;
}

.spots-section h2 {
    margin: 0 0 1rem 0;
    color: #2c3e50;
}

.spots-legend {
    display: flex;
    gap: 2rem;
    margin-bottom: 1.5rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.spot-indicator {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid #dee2e6;
}

.spot-indicator.available {
    background: #28a745;
    border-color: #1e7e34;
}

.spot-indicator.occupied {
    background: #dc3545;
    border-color: #bd2130;
}

.spots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 0.75rem;
    max-height: 600px;
    overflow-y: auto;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e9ecef;
}

.spot {
    width: 80px;
    height: 60px;
    background: #28a745;
    border: 2px solid #1e7e34;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.spot:hover {
    transform: scale(1.05);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.spot.occupied {
    background: #dc3545;
    border-color: #bd2130;
}

.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 500;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.btn-secondary {
    background: #6c757d;
    color: white;
}

.btn-logout {
    background: #dc3545;
    color: white;
}

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>
