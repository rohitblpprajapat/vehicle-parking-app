<template>
    <div class="manage-lots">
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Manage Parking Lots</h3>
            </div>
            <div class="nav-links">
                <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
                <router-link to="/admin/parking-lots" class="nav-link">Manage Lots</router-link>
                <router-link to="/admin/users" class="nav-link">Manage Users</router-link>
                <router-link to="/admin/reservations" class="nav-link">All Reservations</router-link>
                <router-link to="/admin/summary" class="nav-link">Analytics</router-link>
                <button @click="logout" class="btn btn-logout">Logout</button>
            </div>
        </nav>

        <main class="content">
            <div class="container">
                <div class="header">
                    <h1>Parking Lots Management</h1>
                    <button @click="showCreateForm = true" class="btn btn-primary">
                        Create New Parking Lot
                    </button>
                </div>

                <!-- Create/Edit Form Modal -->
                <div v-if="showCreateForm || editingLot" class="modal-overlay" @click="closeForm">
                    <div class="modal" @click.stop>
                        <div class="modal-header">
                            <h2>{{ editingLot ? 'Edit Parking Lot' : 'Create New Parking Lot' }}</h2>
                            <button @click="closeForm" class="close-btn">&times;</button>
                        </div>
                        <form @submit.prevent="submitForm" class="form">
                            <div class="form-group">
                                <label for="name">Name *</label>
                                <input type="text" id="name" v-model="formData.name" required :disabled="formLoading" />
                            </div>
                            <div class="form-group">
                                <label for="location">Location *</label>
                                <input type="text" id="location" v-model="formData.location" required
                                    :disabled="formLoading" />
                            </div>
                            <div class="form-group">
                                <label for="capacity">Capacity (Number of Spots) *</label>
                                <input type="number" id="capacity" v-model="formData.capacity" min="1" required
                                    :disabled="formLoading" />
                            </div>
                            <div class="form-group">
                                <label for="price">Price per Hour ($) *</label>
                                <input type="number" id="price" v-model="formData.price_per_hour" min="0" step="0.50"
                                    required :disabled="formLoading" />
                            </div>
                            <div class="form-actions">
                                <button type="button" @click="closeForm" class="btn btn-secondary"
                                    :disabled="formLoading">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-primary" :disabled="formLoading">
                                    {{ formLoading ? 'Saving...' : (editingLot ? 'Update' : 'Create') }}
                                </button>
                            </div>
                        </form>
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

                <!-- Parking Lots Table -->
                <div v-if="!loading && !error" class="table-container">
                    <table class="lots-table">
                        <thead>
                            <tr>
                                <th style="width: 20%;">Name</th>
                                <th style="width: 18%;">Location</th>
                                <th style="width: 10%; text-align: center;">Capacity</th>
                                <th style="width: 10%; text-align: center;">Available</th>
                                <th style="width: 10%; text-align: center;">Occupied</th>
                                <th style="width: 12%;">Price/Hour</th>
                                <th style="width: 15%;">Occupancy</th>
                                <th style="width: 15%; text-align: center;">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="lot in parkingLots" :key="lot.id">
                                <td class="lot-name">{{ lot.name }}</td>
                                <td class="location">{{ lot.location }}</td>
                                <td class="capacity">{{ lot.capacity }}</td>
                                <td class="available">{{ lot.available_spots }}</td>
                                <td class="occupied">{{ lot.occupied_spots }}</td>
                                <td class="price">${{ lot.price_per_hour }}</td>
                                <td>
                                    <div class="occupancy-cell">
                                        <span>{{ lot.occupancy_rate.toFixed(1) }}%</span>
                                        <div class="mini-bar">
                                            <div class="mini-fill" :style="{ width: lot.occupancy_rate + '%' }"></div>
                                        </div>
                                    </div>
                                </td>
                                <td class="actions">
                                    <button @click="editLot(lot)" class="btn btn-sm btn-secondary">
                                        Edit
                                    </button>
                                    <button @click="deleteLot(lot)" class="btn btn-sm btn-danger">
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)
const error = ref('')
const successMessage = ref('')
const parkingLots = ref([])
const showCreateForm = ref(false)
const editingLot = ref(null)
const formLoading = ref(false)

const formData = ref({
    name: '',
    location: '',
    capacity: '',
    price_per_hour: ''
})

const fetchParkingLots = async () => {
    try {
        loading.value = true
        error.value = ''

        const token = localStorage.getItem('authToken')
        if (!token) {
            router.push('/login')
            return
        }

        const response = await fetch('http://127.0.0.1:5000/api/v1/admin/parking-lots', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            }
        })

        if (response.ok) {
            const data = await response.json()
            parkingLots.value = data.parking_lots
        } else if (response.status === 404) {
            // Fallback to dashboard endpoint if the dedicated endpoint doesn't exist
            const dashboardResponse = await fetch('http://127.0.0.1:5000/api/v1/admin/dashboard', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    "Authentication-Token": token,
                }
            })

            if (dashboardResponse.ok) {
                const dashboardData = await dashboardResponse.json()
                parkingLots.value = dashboardData.parking_lots
            } else {
                const errorData = await dashboardResponse.json()
                error.value = errorData.error || 'Failed to fetch parking lots'
            }
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
    } finally {
        loading.value = false
    }
}

const submitForm = async () => {
    try {
        formLoading.value = true
        const token = localStorage.getItem('authToken')

        const url = editingLot.value
            ? `http://127.0.0.1:5000/api/v1/admin/parking-lots/${editingLot.value.id}`
            : 'http://127.0.0.1:5000/api/v1/admin/parking-lots'

        const method = editingLot.value ? 'PUT' : 'POST'

        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                "Authentication-Token": token,
            },
            body: JSON.stringify({
                name: formData.value.name,
                location: formData.value.location,
                capacity: parseInt(formData.value.capacity),
                price_per_hour: parseFloat(formData.value.price_per_hour)
            })
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = data.message
            closeForm()
            fetchParkingLots()

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to save parking lot'
        }
    } catch (err) {
        console.error('Submit error:', err)
        error.value = 'Network error. Please try again.'
    } finally {
        formLoading.value = false
    }
}

const editLot = (lot) => {
    editingLot.value = lot
    formData.value = {
        name: lot.name,
        location: lot.location,
        capacity: lot.capacity,
        price_per_hour: lot.price_per_hour
    }
}

const deleteLot = async (lot) => {
    if (!confirm(`Are you sure you want to delete "${lot.name}"? This action cannot be undone.`)) {
        return
    }

    try {
        const token = localStorage.getItem('authToken')

        const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/parking-lots/${lot.id}`, {
            method: 'DELETE',
            headers: {
                "Authentication-Token": token
            }
        })

        if (response.ok) {
            const data = await response.json()
            successMessage.value = data.message
            fetchParkingLots()

            setTimeout(() => {
                successMessage.value = ''
            }, 3000)
        } else {
            const errorData = await response.json()
            error.value = errorData.error || 'Failed to delete parking lot'
        }
    } catch (err) {
        console.error('Delete error:', err)
        error.value = 'Network error. Please try again.'
    }
}

const closeForm = () => {
    showCreateForm.value = false
    editingLot.value = null
    formData.value = {
        name: '',
        location: '',
        capacity: '',
        price_per_hour: ''
    }
    error.value = ''
}

const logout = () => {
    localStorage.removeItem('authToken')
    localStorage.removeItem('userEmail')
    router.push('/login')
}

onMounted(() => {
    fetchParkingLots()
})
</script>

<style scoped>
.manage-lots {
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
    border-radius: 8px;
    padding: 0;
    max-width: 500px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid #dee2e6;
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

.form {
    padding: 1.5rem;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #333;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    font-size: 1rem;
    box-sizing: border-box;
}

.form-group input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
}

.loading,
.error-message,
.success-message {
    text-align: center;
    padding: 1rem;
    border-radius: 4px;
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

.table-container {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border: 1px solid #e9ecef;
}

.lots-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
}

.lots-table th,
.lots-table td {
    padding: 1.25rem 1rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
    color: #333;
    vertical-align: middle;
}

.lots-table th {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    font-weight: 700;
    color: #495057;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
    border-bottom: 2px solid #dee2e6;
}

.lots-table tbody tr {
    transition: background-color 0.2s ease;
}

.lots-table tbody tr:hover {
    background-color: #f8f9fa;
}

.lots-table tbody tr:nth-child(even) {
    background-color: #fdfdfd;
}

.lots-table tbody tr:nth-child(even):hover {
    background-color: #f1f3f4;
}

.lot-name {
    font-weight: 700;
    color: #2c3e50;
    font-size: 1rem;
}

.location {
    color: #6c757d;
    font-weight: 500;
    font-style: italic;
}

.capacity {
    color: #495057;
    font-weight: 600;
    text-align: center;
    background-color: #f8f9fa;
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    display: inline-block;
    min-width: 40px;
}

.available {
    color: #28a745;
    font-weight: 700;
    text-align: center;
}

.occupied {
    color: #dc3545;
    font-weight: 700;
    text-align: center;
}

.price {
    font-weight: 700;
    color: #667eea;
    font-size: 1.1rem;
}

.occupancy-cell {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 120px;
}

.occupancy-cell span {
    font-weight: 600;
    color: #495057;
    min-width: 45px;
}

.mini-bar {
    width: 80px;
    height: 10px;
    background: #e9ecef;
    border-radius: 5px;
    overflow: hidden;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

.mini-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745 0%, #ffc107 70%, #dc3545 100%);
    transition: width 0.3s ease;
    border-radius: 5px;
}

.actions {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
}

.btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    font-weight: 500;
    transition: all 0.3s ease;
    font-size: 0.9rem;
}

.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.8rem;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn-secondary {
    background: #6c757d;
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

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}
</style>
