<template>
    <AppLayout>
        <div class="manage-lots">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h2 mb-0">Manage Parking Lots</h1>
                <BaseButton variant="primary" @click="openCreateForm">
                    <i class="bi bi-plus-lg me-1"></i>Create New Parking Lot
                </BaseButton>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="alert alert-danger" role="alert">
                {{ error }}
            </div>

            <!-- Success Message -->
            <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                {{ successMessage }}
                <button type="button" class="btn-close" @click="successMessage = ''"></button>
            </div>

            <!-- Parking Lots Table -->
            <BaseCard v-if="!loading && !error" class="border-0 shadow-sm">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="bg-light">
                            <tr>
                                <th>Name</th>
                                <th>Location</th>
                                <th class="text-center">Capacity</th>
                                <th class="text-center">Available</th>
                                <th class="text-center">Occupied</th>
                                <th>Price/Hour</th>
                                <th>Occupancy</th>
                                <th class="text-end">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="lot in parkingLots" :key="lot.id">
                                <td class="fw-bold">{{ lot.name }}</td>
                                <td class="text-muted fst-italic">{{ lot.location }}</td>
                                <td class="text-center">
                                    <span class="badge bg-light text-dark border">{{ lot.capacity }}</span>
                                </td>
                                <td class="text-center text-success fw-bold">{{ lot.available_spots }}</td>
                                <td class="text-center text-danger fw-bold">{{ lot.occupied_spots }}</td>
                                <td class="text-primary fw-bold">{{ $currency(lot.price_per_hour) }}</td>

                                <td style="width: 15%">
                                    <div class="d-flex align-items-center">
                                        <div class="progress flex-grow-1 me-2" style="height: 6px;">
                                            <div 
                                                class="progress-bar" 
                                                :class="getOccupancyClass(lot.occupancy_rate)"
                                                role="progressbar" 
                                                :style="{ width: lot.occupancy_rate + '%' }"
                                            ></div>
                                        </div>
                                        <small class="text-muted">{{ lot.occupancy_rate.toFixed(0) }}%</small>
                                    </div>
                                </td>
                                <td class="text-end">
                                    <BaseButton size="sm" variant="outline-primary" class="me-2" @click="editLot(lot)">
                                        <i class="bi bi-pencil"></i>
                                    </BaseButton>
                                    <BaseButton size="sm" variant="outline-danger" @click="deleteLot(lot)">
                                        <i class="bi bi-trash"></i>
                                    </BaseButton>
                                </td>
                            </tr>
                            <tr v-if="parkingLots.length === 0">
                                <td colspan="8" class="text-center py-4 text-muted">
                                    No parking lots found. Create one to get started.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </BaseCard>

            <!-- Create/Edit Form Modal -->
            <BaseModal 
                v-if="showCreateForm || editingLot" 
                :title="editingLot ? 'Edit Parking Lot' : 'Create New Parking Lot'" 
                @close="closeForm"
            >
                <form @submit.prevent="submitForm">
                    <BaseInput
                        id="name"
                        label="Name *"
                        v-model="formData.name"
                        required
                        placeholder="e.g. Downtown Garage"
                    />
                    <BaseInput
                        id="location"
                        label="Location *"
                        v-model="formData.location"
                        required
                        placeholder="e.g. 123 Main St"
                    />
                    <div class="row">
                        <div class="col-md-6">
                            <BaseInput
                                id="capacity"
                                label="Capacity *"
                                type="number"
                                v-model="formData.capacity"
                                required
                                min="1"
                            />
                        </div>
                        <div class="col-md-6">
                             <BaseInput
                                id="price"
                                label="Price per Hour (₹) *"

                                type="number"
                                v-model="formData.price_per_hour"
                                required
                                min="0"
                                step="0.50"
                            />
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-end mt-4">
                        <BaseButton variant="secondary" class="me-2" @click="closeForm" :disabled="formLoading">
                            Cancel
                        </BaseButton>
                        <BaseButton type="submit" variant="primary" :loading="formLoading">
                            {{ editingLot ? 'Update' : 'Create' }}
                        </BaseButton>
                    </div>
                </form>
            </BaseModal>
        </div>
    </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
import BaseButton from '../components/common/BaseButton.vue'
import BaseModal from '../components/common/BaseModal.vue'
import BaseInput from '../components/common/BaseInput.vue'
import { API_BASE_URL } from '@/config'

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

const getOccupancyClass = (rate) => {
    if (rate < 50) return 'bg-success'
    if (rate < 80) return 'bg-warning'
    return 'bg-danger'
}

const fetchParkingLots = async () => {
    try {
        loading.value = true
        error.value = ''

        const token = localStorage.getItem('authToken')
        if (!token) {
            router.push('/login')
            return
        }

        const response = await fetch(`${API_BASE_URL}/admin/parking-lots`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            }
        })

        if (response.ok) {
            const data = await response.json()
            parkingLots.value = data.parking_lots
        } else if (response.status === 404) {
            // Fallback to dashboard endpoint if the dedicated endpoint doesn't exist
            const dashboardResponse = await fetch(`${API_BASE_URL}/admin/dashboard`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
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

const openCreateForm = () => {
    showCreateForm.value = true
    editingLot.value = null
    formData.value = {
        name: '',
        location: '',
        capacity: '',
        price_per_hour: ''
    }
}

const submitForm = async () => {
    try {
        formLoading.value = true
        const token = localStorage.getItem('authToken')

        const url = editingLot.value

            ? `${API_BASE_URL}/admin/parking-lots/${editingLot.value.id}`
            : `${API_BASE_URL}/admin/parking-lots`

        const method = editingLot.value ? 'PUT' : 'POST'

        const response = await fetch(url, {
            method,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
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
    showCreateForm.value = false // Ensure showCreateForm is false when editing, logic handled by v-if="showCreateForm || editingLot"
    // Actually, my v-if logic `showCreateForm || editingLot` means if I set editingLot, it opens.
    // I should be careful not to trigger create mode.
    
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

        const response = await fetch(`${API_BASE_URL}/admin/parking-lots/${lot.id}`, {
            method: 'DELETE',
            credentials: 'include',
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
}

onMounted(() => {
    fetchParkingLots()
})
</script>

<style scoped>
/* No additional styles needed with Bootstrap + Components */
</style>
