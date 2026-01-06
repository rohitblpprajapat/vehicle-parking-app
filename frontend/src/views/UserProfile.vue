<template>
    <AppLayout>
        <div class="profile-page">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1 class="h3 mb-0">My Profile</h1>
                <button @click="showPasswordChange = true" class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-key me-1"></i>Change Password
                </button>
            </div>

            <!-- Loading -->
            <div v-if="loading" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <div v-else>
                <!-- Profile Header Card -->
                <BaseCard class="mb-4 bg-white border-0 shadow-sm">
                    <div class="d-flex flex-column flex-md-row align-items-center gap-4">
                        <div class="avatar-circle bg-primary text-white d-flex align-items-center justify-content-center rounded-circle fs-2 fw-bold" style="width: 80px; height: 80px;">
                            {{ userInitials }}
                        </div>
                        <div class="text-center text-md-start flex-grow-1">
                            <h2 class="h4 mb-1">{{ user?.name || 'User' }}</h2>
                            <p class="text-muted mb-2">{{ user?.email }}</p>
                             <div class="d-flex flex-wrap justify-content-center justify-content-md-start gap-2">
                                <BaseBadge v-for="role in user?.roles" :key="role" variant="info">{{ role }}</BaseBadge>
                            </div>
                        </div>
                        
                        <!-- Header Stats -->
                         <div class="d-flex gap-4 text-center">
                            <div>
                                <div class="h4 fw-bold mb-0 text-primary">{{ totalReservations }}</div>
                                <div class="small text-muted text-uppercase">Bookings</div>
                            </div>
                            <div>
                                <div class="h4 fw-bold mb-0 text-success">{{ $currency(totalSpent) }}</div>

                                <div class="small text-muted text-uppercase">Spent</div>
                            </div>
                            <div>
                                <div class="h4 fw-bold mb-0 text-info">{{ totalHours.toFixed(0) }}h</div>
                                <div class="small text-muted text-uppercase">Parked</div>
                            </div>
                        </div>
                    </div>
                </BaseCard>

                <!-- Analytics Section -->
                <div class="mb-4">
                     <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="mb-0">Analytics</h4>
                        <div class="d-flex gap-2">
                            <select class="form-select form-select-sm w-auto" v-model="selectedPeriod" @change="loadAnalytics">
                                <option value="7">Last 7 Days</option>
                                <option value="30">Last 30 Days</option>
                                <option value="90">Last 3 Months</option>
                                <option value="365">Last Year</option>
                            </select>
                             <BaseButton size="sm" variant="outline-primary" @click="exportPersonalReport">
                                📊 Export
                            </BaseButton>
                        </div>
                    </div>

                    <div class="row g-4 mb-4">
                        <!-- Spending Chart -->
                        <div class="col-lg-8">
                             <BaseCard class="h-100">
                                <h5 class="card-title text-muted small text-uppercase mb-3">Spending Over Time</h5>
                                <div style="height: 300px;">
                                    <canvas ref="spendingChart"></canvas>
                                </div>
                             </BaseCard>
                        </div>
                        <!-- Duration Chart -->
                        <div class="col-lg-4">
                             <BaseCard class="h-100">
                                <h5 class="card-title text-muted small text-uppercase mb-3">Duration Distribution</h5>
                                <div style="height: 300px;">
                                    <canvas ref="durationChart"></canvas>
                                </div>
                             </BaseCard>
                        </div>
                    </div>
                    
                    <div class="row g-4 mb-4">
                         <!-- Lot Usage -->
                        <div class="col-md-4">
                            <BaseCard class="h-100">
                                <h5 class="card-title text-muted small text-uppercase mb-3">Parking Lot Usage</h5>
                                <div style="height: 250px;">
                                    <canvas ref="lotUsageChart"></canvas>
                                </div>
                            </BaseCard>
                        </div>
                         <!-- Trends -->
                        <div class="col-md-4">
                             <BaseCard class="h-100">
                                <h5 class="card-title text-muted small text-uppercase mb-3">Monthly Trends</h5>
                                <div style="height: 250px;">
                                    <canvas ref="trendsChart"></canvas>
                                </div>
                            </BaseCard>
                        </div>
                         <!-- Weekly Habits -->
                        <div class="col-md-4">
                             <BaseCard class="h-100">
                                <h5 class="card-title text-muted small text-uppercase mb-3">Weekly Habits</h5>
                                <div style="height: 250px;">
                                    <canvas ref="weeklyHabitsChart"></canvas>
                                </div>
                            </BaseCard>
                        </div>
                    </div>
                </div>

                <!-- Insights & Summary Grid -->
                <div class="row g-4 mb-4">
                    <div class="col-md-8">
                         <BaseCard class="h-100">
                            <h5 class="mb-3">Personal Insights</h5>
                            <div class="row g-3">
                                <div class="col-sm-6">
                                    <div class="p-3 bg-light rounded text-center">
                                        <div class="fs-1 mb-2">time</div>
                                        <div class="small text-muted text-uppercase">Peak Time</div>
                                        <div class="fw-bold">{{ peakParkingTime }}</div>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                    <div class="p-3 bg-light rounded text-center">
                                        <div class="fs-1 mb-2">Cal</div>
                                        <div class="small text-muted text-uppercase">Favorite Day</div>
                                        <div class="fw-bold">{{ favoriteDay }}</div>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                     <div class="p-3 bg-light rounded text-center">
                                        <div class="fs-1 mb-2">bulb</div>
                                        <div class="small text-muted text-uppercase">Tip</div>
                                        <div class="fw-bold small">{{ moneySavingTip }}</div>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                     <div class="p-3 bg-light rounded text-center">
                                        <div class="fs-1 mb-2">chart</div>
                                        <div class="small text-muted text-uppercase">Trend</div>
                                        <div class="fw-bold">{{ usageTrend }}</div>
                                    </div>
                                </div>
                                <div class="col-sm-6">
                                     <div class="p-3 bg-light rounded text-center">
                                        <div class="fs-1 mb-2">⏱️</div>
                                        <div class="small text-muted text-uppercase">Punctuality</div>
                                        <div class="fw-bold" :class="punctualityClass">{{ punctualityScore }}%</div>
                                    </div>
                                </div>
                            </div>
                         </BaseCard>
                    </div>

                    <div class="col-md-4">
                         <BaseCard class="h-100">
                            <h5 class="mb-3">Summary</h5>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Avg / Booking</span>
                                    <span class="fw-bold">{{ $currency(averagePerBooking) }}</span>

                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Avg / Hour</span>
                                    <span class="fw-bold">{{ $currency(averagePerHour) }}</span>

                                </li>
                                 <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Savings</span>
                                    <span :class="savingsVsEstimate >= 0 ? 'text-success' : 'text-danger'" class="fw-bold">
                                        {{ $currency(Math.abs(savingsVsEstimate)) }}

                                    </span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Top Location</span>
                                    <span class="fw-bold text-truncate" style="max-width: 150px;">{{ mostUsedLot || 'N/A' }}</span>
                                </li>
                            </ul>
                         </BaseCard>
                    </div>
                </div>

                <!-- Recent Activity -->
                <BaseCard title="Recent Activity" class="mb-4">
                    <div class="table-responsive">
                        <table class="table table-hover align-middle mb-0">
                            <thead class="bg-light">
                                <tr>
                                    <th>Location</th>
                                    <th>Date</th>
                                    <th>Duration</th>
                                    <th>Cost</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="activity in recentActivity" :key="activity.id">
                                    <td>
                                        <div class="fw-bold">{{ activity.parking_lot }}</div>
                                        <div class="small text-muted">Spot #{{ activity.spot_number }}</div>
                                    </td>
                                    <td>{{ formatDate(activity.date) }}</td>
                                    <td>{{ activity.duration_hours?.toFixed(1) }}h</td>
                                    <td>{{ $currency(activity.cost) }}</td>

                                    <td><BaseBadge :variant="getStatusVariant(activity.status)">{{ activity.status }}</BaseBadge></td>
                                </tr>
                                <tr v-if="recentActivity.length === 0">
                                    <td colspan="5" class="text-center py-3 text-muted">No recent activity</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </BaseCard>

            </div>

             <!-- Change Password Modal -->
            <BaseModal v-if="showPasswordChange" title="Change Password" @close="showPasswordChange = false">
                <form @submit.prevent="changePassword">
                    <BaseInput
                        id="current-password"
                        label="Current Password"
                        type="password"
                        v-model="passwordForm.current"
                        required
                    />
                    <BaseInput
                        id="new-password"
                        label="New Password"
                        type="password"
                        v-model="passwordForm.new"
                        required
                    />
                    <BaseInput
                        id="confirm-password"
                        label="Confirm New Password"
                        type="password"
                        v-model="passwordForm.confirm"
                        required
                    />
                    <div class="d-flex justify-content-end mt-3">
                        <BaseButton variant="secondary" class="me-2" @click="showPasswordChange = false">Cancel</BaseButton>
                        <BaseButton type="submit" variant="primary">Change Password</BaseButton>
                    </div>
                </form>
            </BaseModal>

        </div>
    </AppLayout>
</template>

<script>
import { 
    Chart, 
    LineController, 
    LineElement, 
    PointElement, 
    LinearScale, 
    Title, 
    CategoryScale, 
    Tooltip, 
    Legend, 
    DoughnutController, 
    ArcElement, 
    BarController, 
    BarElement, 
    RadarController, 
    RadialLinearScale,
    ScatterController,
    TimeScale,
    Filler
} from 'chart.js'
import 'chartjs-adapter-date-fns'

// Register Chart.js components manually to avoid tree-shaking issues or missing global registry
Chart.register(
    LineController, 
    LineElement, 
    PointElement, 
    LinearScale, 
    Title, 
    CategoryScale, 
    Tooltip, 
    Legend, 
    DoughnutController, 
    ArcElement, 
    BarController, 
    BarElement, 
    RadarController, 
    RadialLinearScale,
    ScatterController,
    TimeScale,
    Filler
)

import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
import BaseButton from '../components/common/BaseButton.vue'
import BaseBadge from '../components/common/BaseBadge.vue'
import BaseModal from '../components/common/BaseModal.vue'
import BaseInput from '../components/common/BaseInput.vue'
import { logout as authLogout, getUserInfo } from '../utils/auth.js'
import { API_BASE_URL } from '@/config'

export default {
    name: 'UserProfile',
    components: {
        AppLayout,
        BaseCard,
        BaseButton,
        BaseBadge,
        BaseModal,
        BaseInput
    },
    data() {
        return {
            user: null,
            spendingSummary: null,
            parkingHistory: [],
            recentActivity: [],
            selectedPeriod: '30',
            showPasswordChange: false,
            passwordForm: {
                current: '',
                new: '',
                confirm: ''
            },
            charts: {
                spending: null,
                duration: null,
                lotUsage: null,
                trends: null,
                weeklyHabits: null,
                // favoriteLocations: null, // Removed as simpler grid is used
                // costComparison: null // Removed for cleaner UI
            },
            loading: true,
            chartCreationInProgress: false
        }
    },
    computed: {
        userInitials() {
            if (!this.user?.name) return 'U'
            return this.user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
        },
        totalReservations() {
            return this.spendingSummary?.summary?.total_reservations || 0
        },
        totalSpent() {
            return this.spendingSummary?.summary?.total_spent || 0
        },
        totalHours() {
            return this.spendingSummary?.summary?.total_hours_parked || 0
        },
        averagePerBooking() {
            return this.spendingSummary?.summary?.average_cost_per_reservation || 0
        },
        averagePerHour() {
            return this.spendingSummary?.summary?.average_cost_per_hour || 0
        },
        savingsVsEstimate() {
            return this.spendingSummary?.summary?.savings_vs_estimate || 0
        },
        mostUsedLot() {
            const lots = this.spendingSummary?.spending_by_parking_lot || []
            return lots.length > 0 ? lots[0].lot_name : null
        },
        peakParkingTime() {
            const hourlyData = this.spendingSummary?.hourly_usage || []
            if (hourlyData.length === 0) return 'N/A'
            const peakHour = hourlyData.reduce((max, curr) => curr.count > max.count ? curr : max)
            return `${peakHour.hour}:00 - ${peakHour.hour + 1}:00`
        },
        favoriteDay() {
            const dailyData = this.spendingSummary?.daily_usage || []
            if (dailyData.length === 0) return 'N/A'
            const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            const favDay = dailyData.reduce((max, curr) => curr.count > max.count ? curr : max)
            return days[favDay.day_of_week]
        },
        moneySavingTip() {
            const avgHourly = this.averagePerHour
            if (avgHourly > 5) return 'Consider shorter parking sessions'
            if (avgHourly < 2) return 'You\'re finding great deals!'
            return 'Look for off-peak discounts'
        },
        usageTrend() {
            const thisMonth = this.spendingSummary?.summary?.total_reservations || 0
            const lastMonth = this.spendingSummary?.previous_month_reservations || 0
            if (thisMonth > lastMonth) return 'Increasing usage 📈'
            if (thisMonth < lastMonth) return 'Decreasing usage 📉'
            if (thisMonth < lastMonth) return 'Decreasing usage 📉'
            return 'Stable usage ➡️'
        },
        punctualityScore() {
            return this.spendingSummary?.summary?.punctuality_score || 100
        },
        punctualityClass() {
            const score = this.punctualityScore
            if (score >= 90) return 'text-success'
            if (score >= 70) return 'text-warning'
            return 'text-danger'
        }
    },
    async mounted() {
        await this.loadUserData()
        await this.loadAnalytics()
        this.loading = false
    },
    beforeUnmount() {
        this.destroyAllCharts()
    },
    methods: {
        async loadUserData() {
            try {
                try {
                     const response = await fetch(`${API_BASE_URL}/auth/me`, {
                        credentials: 'include',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    })
                    if (response.ok) {
                        const data = await response.json()
                        this.user = data.user
                    } else {
                        throw new Error('API failed')
                    }
                } catch (e) {
                     // Fallback
                     const info = getUserInfo()
                     if (info) this.user = { 
                        name: info.name, 
                        email: info.email, 
                        roles: info.roles || ['user'] 
                    }
                }
            } catch (error) {
                console.error('Error loading user data:', error)
                this.$router.push('/login')
            }
        },
        async loadAnalytics() {
            try {
                const summaryResponse = await fetch(`${API_BASE_URL}/user/spending-summary?days=${this.selectedPeriod}`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                })
                if (summaryResponse.ok) {
                    this.spendingSummary = await summaryResponse.json()
                    this.recentActivity = this.spendingSummary.recent_activity || []
                }

                const historyResponse = await fetch(`${API_BASE_URL}/reservations?limit=100`, {
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' }
                })
                if (historyResponse.ok) {
                    const historyData = await historyResponse.json()
                    this.parkingHistory = historyData.reservations || []
                }

                this.$nextTick(() => {
                    this.createCharts()
                })
            } catch (error) {
                console.error('Error loading analytics:', error)
            }
        },
        destroyAllCharts() {
            Object.keys(this.charts).forEach(key => {
                if (this.charts[key]) {
                    this.charts[key].destroy()
                    this.charts[key] = null
                }
            })
        },
        createCharts() {
            if (this.chartCreationInProgress) return
            this.chartCreationInProgress = true

            try {
                this.destroyAllCharts()
                setTimeout(() => {
                    if (this.$refs.spendingChart) this.createSpendingChart()
                    if (this.$refs.durationChart) this.createDurationChart()
                    if (this.$refs.lotUsageChart) this.createLotUsageChart()
                    if (this.$refs.trendsChart) this.createTrendsChart()
                    if (this.$refs.weeklyHabitsChart) this.createWeeklyHabitsChart()
                    this.chartCreationInProgress = false
                }, 100)
            } catch (error) {
                console.error('Error creating charts:', error)
                this.chartCreationInProgress = false
            }
        },
        createSpendingChart() {
            const ctx = this.$refs.spendingChart?.getContext('2d')
            if (!ctx) return

            const spendingByDate = {}
            this.parkingHistory.forEach(item => {
                const date = new Date(item.created_at || item.start_time || item.reservation_time).toDateString()
                const cost = item.total_cost || item.cost || 0
                spendingByDate[date] = (spendingByDate[date] || 0) + cost
            })

            const labels = Object.keys(spendingByDate).sort()
            const data = labels.map(date => spendingByDate[date])

            this.charts.spending = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [{
                        label: 'Daily Spending',
                        data,
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true } }
                }
            })
        },
        createDurationChart() {
            const ctx = this.$refs.durationChart?.getContext('2d')
            if (!ctx) return
            
            const ranges = { '0-1h': 0, '1-3h': 0, '3-6h': 0, '6-12h': 0, '12h+': 0 }
            this.parkingHistory.forEach(item => {
                const hours = item.duration_hours || item.duration || 0
                if (hours <= 1) ranges['0-1h']++
                else if (hours <= 3) ranges['1-3h']++
                else if (hours <= 6) ranges['3-6h']++
                else if (hours <= 12) ranges['6-12h']++
                else ranges['12h+']++
            })

            this.charts.duration = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(ranges),
                    datasets: [{
                        data: Object.values(ranges),
                        backgroundColor: ['#198754', '#0d6efd', '#ffc107', '#dc3545', '#6f42c1']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            })
        },
        createLotUsageChart() {
             const ctx = this.$refs.lotUsageChart?.getContext('2d')
            if (!ctx) return

            const lotData = this.spendingSummary?.spending_by_parking_lot || []
            const labels = lotData.map(lot => lot.lot_name)
            const data = lotData.map(lot => lot.visits)

            this.charts.lotUsage = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Visits',
                        data,
                        backgroundColor: '#0d6efd',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                }
            })
        },
        createTrendsChart() {
            const ctx = this.$refs.trendsChart?.getContext('2d')
            if (!ctx) return
             // Group by month
            const monthlyData = {}
            this.parkingHistory.forEach(item => {
                const date = item.created_at || item.start_time || item.reservation_time || new Date()
                const month = new Date(date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short'
                })
                if (!monthlyData[month]) {
                    monthlyData[month] = { bookings: 0, spending: 0 }
                }
                monthlyData[month].bookings++
                monthlyData[month].spending += (item.total_cost || item.cost || 0)
            })

            const labels = Object.keys(monthlyData).sort()
            const bookingsData = labels.map(month => monthlyData[month].bookings)
            const spendingData = labels.map(month => monthlyData[month].spending)

            this.charts.trends = new Chart(ctx, {
                 type: 'line',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Bookings',
                            data: bookingsData,
                            borderColor: '#198754',
                            backgroundColor: 'rgba(25, 135, 84, 0.1)',
                            yAxisID: 'y'
                        },
                        {
                            label: 'Spending (₹)',

                            data: spendingData,
                            borderColor: '#0d6efd',
                            backgroundColor: 'rgba(13, 110, 253, 0.1)',
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                         y: { type: 'linear', display: true, position: 'left', beginAtZero: true },
                        y1: { type: 'linear', display: true, position: 'right', beginAtZero: true, grid: { drawOnChartArea: false } }
                    }
                }
            })
        },
        createWeeklyHabitsChart() {
            const ctx = this.$refs.weeklyHabitsChart?.getContext('2d')
            if (!ctx) return
            
            const weeklyData = this.spendingSummary?.daily_usage || []
            // Sort by order of week if needed, but backend sends Sunday...Saturday dict usually. 
            // We'll rely on backend sending list of objects or handle dict.
            // Backend sends: [{'day': 'Monday', 'visits': 5}, ...]
            
            const daysOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weeklyData.sort((a, b) => daysOrder.indexOf(a.day) - daysOrder.indexOf(b.day))
            
            const labels = weeklyData.map(d => d.day.substring(0, 3)) // Mon, Tue...
            const data = weeklyData.map(d => d.visits)
            
            this.charts.weeklyHabits = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Visits',
                        data,
                        backgroundColor: '#6f42c1',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                }
            })
        },
        async exportPersonalReport() {
             try {
                const response = await fetch(`${API_BASE_URL}/user/export-report?days=${this.selectedPeriod}`, {
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                const blob = await response.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `report.csv`
                a.click()
                window.URL.revokeObjectURL(url)
            } catch (error) {
                console.error('Error exporting:', error)
                alert('Export failed')
            }
        },
        async changePassword() {
            if (this.passwordForm.new !== this.passwordForm.confirm) {
                alert('Passwords do not match')
                return
            }
            try {
                const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        current_password: this.passwordForm.current,
                        new_password: this.passwordForm.new
                    })
                })
                if (response.ok) {
                    alert('Password changed')
                    this.showPasswordChange = false
                    this.passwordForm = { current: '', new: '', confirm: '' }
                } else {
                    const data = await response.json()
                    alert(data.error || 'Failed')
                }
            } catch (e) {
                alert('Error changing password')
            }
        },
        getStatusVariant(status) {
            switch(status) {
                case 'active': return 'success'
                case 'completed': return 'secondary'
                case 'cancelled': return 'danger'
                default: return 'info'
            }
        },
        formatDate(date) {
            return new Date(date).toLocaleDateString()
        }
    }
}
</script>

<style scoped>
/* Scoped styles mainly for specific chart heights or custom overrides not in bootstrap */
.avatar-circle {
    font-size: 2rem;
}
</style>
