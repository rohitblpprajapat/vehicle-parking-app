<template>
    <div class="parking-lots">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Parking Lots</h3>
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
                <h1>Available Parking Lots</h1>

                <div class="filters">
                    <input v-model="searchQuery" type="text" placeholder="Search parking lots..." class="search-input">
                    <select v-model="locationFilter" class="location-filter">
                        <option value="">All Locations</option>
                        <option value="downtown">Downtown</option>
                        <option value="uptown">Uptown</option>
                        <option value="mall">Shopping Mall</option>
                    </select>
                </div>

                <div class="lots-grid">
                    <div v-for="lot in filteredLots" :key="lot.id" class="lot-card">
                        <div class="lot-header">
                            <h3>{{ lot.name }}</h3>
                            <span class="availability" :class="getAvailabilityClass(lot)">
                                {{ lot.available }}/{{ lot.capacity }} available
                            </span>
                        </div>
                        <p class="location">📍 {{ lot.location }}</p>
                        <p class="price">💰 ${{ lot.price }}/hour</p>

                        <div class="lot-actions">
                            <button @click="viewDetails(lot)" class="btn btn-secondary">
                                View Details
                            </button>
                            <button @click="reserveSpot(lot)" class="btn btn-primary" :disabled="lot.available === 0">
                                Reserve Spot
                            </button>
                        </div>
                    </div>
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
const searchQuery = ref('')
const locationFilter = ref('')
const parkingLots = ref([
    {
        id: 1,
        name: 'Central Plaza Parking',
        location: 'Downtown',
        capacity: 100,
        available: 25,
        price: 5
    },
    {
        id: 2,
        name: 'Mall Parking Garage',
        location: 'Shopping Mall',
        capacity: 200,
        available: 150,
        price: 3
    },
    {
        id: 3,
        name: 'Business District Lot',
        location: 'Uptown',
        capacity: 80,
        available: 0,
        price: 8
    },
    {
        id: 4,
        name: 'City Center Parking',
        location: 'Downtown',
        capacity: 150,
        available: 75,
        price: 6
    }
])

// Computed properties
const filteredLots = computed(() => {
    return parkingLots.value.filter(lot => {
        const matchesSearch = lot.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            lot.location.toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesLocation = !locationFilter.value ||
            lot.location.toLowerCase().includes(locationFilter.value.toLowerCase())
        return matchesSearch && matchesLocation
    })
})

// Methods
const getAvailabilityClass = (lot) => {
    const ratio = lot.available / lot.capacity
    if (ratio === 0) return 'unavailable'
    if (ratio < 0.3) return 'low'
    if (ratio < 0.7) return 'medium'
    return 'high'
}

const viewDetails = (lot) => {
    alert(`Viewing details for ${lot.name}\nLocation: ${lot.location}\nCapacity: ${lot.capacity}\nAvailable: ${lot.available}`)
}

const reserveSpot = (lot) => {
    if (lot.available > 0) {
        alert(`Reserving a spot at ${lot.name}`)
        // Here you would typically navigate to a reservation form or make an API call
    }
}

const logout = () => {
    localStorage.removeItem('authToken')
    router.push('/login')
}

onMounted(() => {
    // Fetch parking lots data from API
    console.log('Parking lots page mounted')
})
</script>

<style scoped>
.parking-lots {
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

.content h1 {
    margin-bottom: 2rem;
    color: #333;
}

.filters {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.search-input,
.location-filter {
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.search-input {
    flex: 1;
    min-width: 250px;
}

.location-filter {
    min-width: 150px;
}

.lots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.lot-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
}

.lot-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.lot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.lot-header h3 {
    margin: 0;
    color: #333;
}

.availability {
    font-size: 0.9rem;
    font-weight: bold;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

.availability.high {
    background-color: #d4edda;
    color: #155724;
}

.availability.medium {
    background-color: #fff3cd;
    color: #856404;
}

.availability.low {
    background-color: #f8d7da;
    color: #721c24;
}

.availability.unavailable {
    background-color: #f5c6cb;
    color: #721c24;
}

.location,
.price {
    margin: 0.5rem 0;
    color: #666;
}

.lot-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
}

.btn {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    font-weight: 600;
    transition: background-color 0.3s;
    flex: 1;
}

.btn-primary {
    background-color: #667eea;
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background-color: #5a67d8;
}

.btn-primary:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #5a6268;
}
</style>
