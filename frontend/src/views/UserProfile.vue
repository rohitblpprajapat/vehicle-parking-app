<template>
    <div class="user-profile">
        <!-- Header Section -->
        <div class="profile-header">
            <div class="user-info">
                <div class="avatar">
                    <span class="avatar-text">{{ userInitials }}</span>
                </div>
                <div class="user-details">
                    <h1>{{ user?.name || 'User' }}</h1>
                    <p class="email">{{ user?.email }}</p>
                    <div class="user-stats">
                        <div class="stat">
                            <span class="stat-value">{{ totalReservations }}</span>
                            <span class="stat-label">Total Bookings</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${{ totalSpent.toFixed(2) }}</span>
                            <span class="stat-label">Total Spent</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">{{ totalHours.toFixed(1) }}h</span>
                            <span class="stat-label">Hours Parked</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="profile-actions">
                <button @click="showPasswordChange = true" class="btn btn-outline">
                    Change Password
                </button>
            </div>
        </div>

        <!-- Analytics Dashboard -->
        <div class="analytics-section">
            <h2>Your Parking Analytics</h2>
            <p class="analytics-subtitle">Track your parking patterns and spending habits</p>

            <!-- Time Period Filter -->
            <div class="filter-controls">
                <select v-model="selectedPeriod" @change="loadAnalytics">
                    <option value="7">Last 7 Days</option>
                    <option value="30">Last 30 Days</option>
                    <option value="90">Last 3 Months</option>
                    <option value="365">Last Year</option>
                </select>
                <button @click="exportPersonalReport" class="btn btn-outline btn-small">
                    📊 Export Report
                </button>
            </div>

            <!-- Charts Grid -->
            <div class="charts-grid">
                <!-- Spending Over Time Chart -->
                <div class="chart-container">
                    <h3>Spending Over Time</h3>
                    <canvas ref="spendingChart" class="chart"></canvas>
                </div>

                <!-- Parking Duration Distribution -->
                <div class="chart-container">
                    <h3>Parking Duration Distribution</h3>
                    <canvas ref="durationChart" class="chart"></canvas>
                </div>

                <!-- Parking Lot Usage -->
                <div class="chart-container">
                    <h3>Parking Lot Usage</h3>
                    <canvas ref="lotUsageChart" class="chart"></canvas>
                </div>

                <!-- Favorite Locations Chart -->
                <div class="chart-container">
                    <h3>Your Favorite Parking Locations</h3>
                    <canvas ref="favoriteLocationsChart" class="chart"></canvas>
                </div>

                <!-- Cost Comparison Chart -->
                <div class="chart-container">
                    <h3>Cost vs Time Analysis</h3>
                    <canvas ref="costComparisonChart" class="chart"></canvas>
                </div>
            </div>

            <!-- Personal Insights -->
            <div class="insights-section">
                <h3>Personal Insights</h3>
                <div class="insights-grid">
                    <div class="insight-card">
                        <div class="insight-icon">🕐</div>
                        <div class="insight-content">
                            <h4>Peak Parking Time</h4>
                            <p>{{ peakParkingTime }}</p>
                        </div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-icon">🏆</div>
                        <div class="insight-content">
                            <h4>Favorite Day</h4>
                            <p>{{ favoriteDay }}</p>
                        </div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-icon">💡</div>
                        <div class="insight-content">
                            <h4>Money-Saving Tip</h4>
                            <p>{{ moneySavingTip }}</p>
                        </div>
                    </div>
                    <div class="insight-card">
                        <div class="insight-icon">📈</div>
                        <div class="insight-content">
                            <h4>Usage Trend</h4>
                            <p>{{ usageTrend }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Spending Summary -->
        <div class="spending-summary">
            <h2>Spending Summary</h2>
            <div class="summary-cards">
                <div class="summary-card">
                    <h4>Average per Booking</h4>
                    <p class="amount">${{ averagePerBooking.toFixed(2) }}</p>
                </div>
                <div class="summary-card">
                    <h4>Average per Hour</h4>
                    <p class="amount">${{ averagePerHour.toFixed(2) }}</p>
                </div>
                <div class="summary-card">
                    <h4>Savings vs Estimate</h4>
                    <p class="amount" :class="savingsVsEstimate >= 0 ? 'positive' : 'negative'">
                        ${{ Math.abs(savingsVsEstimate).toFixed(2) }}
                        <span class="savings-label">
                            {{ savingsVsEstimate >= 0 ? 'Saved' : 'Extra' }}
                        </span>
                    </p>
                </div>
                <div class="summary-card">
                    <h4>Most Used Lot</h4>
                    <p class="lot-name">{{ mostUsedLot || 'N/A' }}</p>
                </div>
            </div>
        </div>

        <!-- Recent Activity -->
        <div class="recent-activity">
            <h2>Recent Parking History</h2>
            <div class="activity-list">
                <div v-for="activity in recentActivity" :key="activity.id" class="activity-item">
                    <div class="activity-icon">
                        <i class="icon-parking"></i>
                    </div>
                    <div class="activity-details">
                        <h4>{{ activity.parking_lot }}</h4>
                        <p>Spot {{ activity.spot_number }} • {{ formatDate(activity.date) }}</p>
                        <div class="activity-meta">
                            <span class="duration">{{ activity.duration_hours?.toFixed(1) }}h</span>
                            <span class="cost">${{ activity.cost.toFixed(2) }}</span>
                            <span class="status" :class="activity.status">{{ activity.status }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Change Password Modal -->
        <div v-if="showPasswordChange" class="modal-overlay" @click="showPasswordChange = false">
            <div class="modal" @click.stop>
                <h3>Change Password</h3>
                <form @submit.prevent="changePassword">
                    <div class="form-group">
                        <label>Current Password</label>
                        <input type="password" v-model="passwordForm.current" required>
                    </div>
                    <div class="form-group">
                        <label>New Password</label>
                        <input type="password" v-model="passwordForm.new" required>
                    </div>
                    <div class="form-group">
                        <label>Confirm New Password</label>
                        <input type="password" v-model="passwordForm.confirm" required>
                    </div>
                    <div class="form-actions">
                        <button type="button" @click="showPasswordChange = false" class="btn btn-outline">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary">
                            Change Password
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import 'chartjs-adapter-date-fns'

Chart.register(...registerables)

export default {
    name: 'UserProfile',
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
                favoriteLocations: null,
                costComparison: null
            },
            loading: true
        }
    },
    computed: {
        userInitials() {
            if (!this.user?.name) return 'U'
            return this.user.name.split(' ').map(n => n[0]).join('').toUpperCase()
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
            return 'Stable usage ➡️'
        }
    },
    async mounted() {
        await this.loadUserData()
        await this.loadAnalytics()
        this.loading = false
    },
    beforeUnmount() {
        // Destroy charts to prevent memory leaks
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy()
        })
    },
    methods: {
        async loadUserData() {
            try {
                const token = localStorage.getItem('token')
                const response = await fetch('/api/v1/auth/me', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                const data = await response.json()
                this.user = data.user
            } catch (error) {
                console.error('Error loading user data:', error)
                this.$router.push('/login')
            }
        },
        async loadAnalytics() {
            try {
                const token = localStorage.getItem('token')

                // Load spending summary
                const summaryResponse = await fetch(`/api/v1/user/spending-summary?days=${this.selectedPeriod}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                this.spendingSummary = await summaryResponse.json()
                this.recentActivity = this.spendingSummary.recent_activity || []

                // Load detailed history for charts
                const historyResponse = await fetch(`/api/v1/reservations/history?limit=100`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                const historyData = await historyResponse.json()
                this.parkingHistory = historyData.history || []

                this.$nextTick(() => {
                    this.createCharts()
                })
            } catch (error) {
                console.error('Error loading analytics:', error)
            }
        },
        createCharts() {
            this.createSpendingChart()
            this.createDurationChart()
            this.createLotUsageChart()
            this.createTrendsChart()
            this.createFavoriteLocationsChart()
            this.createCostComparisonChart()
        },
        createSpendingChart() {
            const ctx = this.$refs.spendingChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.spending) {
                this.charts.spending.destroy()
            }

            // Group spending by date
            const spendingByDate = {}
            this.parkingHistory.forEach(item => {
                const date = new Date(item.timestamps.created_at).toDateString()
                spendingByDate[date] = (spendingByDate[date] || 0) + item.cost_breakdown.final_cost
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
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: value => `$${value.toFixed(2)}`
                            }
                        }
                    }
                }
            })
        },
        createDurationChart() {
            const ctx = this.$refs.durationChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.duration) {
                this.charts.duration.destroy()
            }

            // Group by duration ranges
            const ranges = {
                '0-1h': 0,
                '1-3h': 0,
                '3-6h': 0,
                '6-12h': 0,
                '12h+': 0
            }

            this.parkingHistory.forEach(item => {
                const hours = item.duration.actual_hours || item.duration.reserved_hours || 0
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
                        backgroundColor: [
                            '#10B981',
                            '#3B82F6',
                            '#F59E0B',
                            '#EF4444',
                            '#8B5CF6'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            })
        },
        createLotUsageChart() {
            const ctx = this.$refs.lotUsageChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.lotUsage) {
                this.charts.lotUsage.destroy()
            }

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
                        backgroundColor: '#3B82F6',
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            })
        },
        createTrendsChart() {
            const ctx = this.$refs.trendsChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.trends) {
                this.charts.trends.destroy()
            }

            // Group by month
            const monthlyData = {}
            this.parkingHistory.forEach(item => {
                const month = new Date(item.timestamps.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short'
                })
                if (!monthlyData[month]) {
                    monthlyData[month] = { bookings: 0, spending: 0 }
                }
                monthlyData[month].bookings++
                monthlyData[month].spending += item.cost_breakdown.final_cost
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
                            borderColor: '#10B981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            yAxisID: 'y'
                        },
                        {
                            label: 'Spending ($)',
                            data: spendingData,
                            borderColor: '#3B82F6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,
                            grid: {
                                drawOnChartArea: false
                            },
                            ticks: {
                                callback: value => `$${value.toFixed(0)}`
                            }
                        }
                    }
                }
            })
        },
        createFavoriteLocationsChart() {
            const ctx = this.$refs.favoriteLocationsChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.favoriteLocations) {
                this.charts.favoriteLocations.destroy()
            }

            const lotData = this.spendingSummary?.spending_by_parking_lot || []
            const labels = lotData.slice(0, 5).map(lot => lot.lot_name)
            const visitData = lotData.slice(0, 5).map(lot => lot.visits)

            this.charts.favoriteLocations = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Visits',
                            data: visitData,
                            borderColor: '#3B82F6',
                            backgroundColor: 'rgba(59, 130, 246, 0.2)',
                            pointBackgroundColor: '#3B82F6',
                            pointBorderColor: '#ffffff',
                            pointHoverBackgroundColor: '#ffffff',
                            pointHoverBorderColor: '#3B82F6'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    }
                }
            })
        },
        createCostComparisonChart() {
            const ctx = this.$refs.costComparisonChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.costComparison) {
                this.charts.costComparison.destroy()
            }

            // Create scatter plot of cost vs duration
            const scatterData = this.parkingHistory.map(item => ({
                x: item.duration.actual_hours || item.duration.reserved_hours || 0,
                y: item.cost_breakdown.final_cost
            }))

            this.charts.costComparison = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Cost vs Duration',
                        data: scatterData,
                        backgroundColor: 'rgba(59, 130, 246, 0.6)',
                        borderColor: '#3B82F6',
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.parsed.x.toFixed(1)}h: $${context.parsed.y.toFixed(2)}`
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Duration (hours)'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Cost ($)'
                            },
                            ticks: {
                                callback: value => `$${value.toFixed(2)}`
                            }
                        }
                    }
                }
            })
        },
        async exportPersonalReport() {
            try {
                const token = localStorage.getItem('token')
                const response = await fetch(`/api/v1/user/export-report?days=${this.selectedPeriod}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                const blob = await response.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `personal-parking-report-${this.selectedPeriod}days.csv`
                a.click()
                window.URL.revokeObjectURL(url)
            } catch (error) {
                console.error('Error exporting personal report:', error)
                alert('Failed to export personal report')
            }
        },
        async changePassword() {
            if (this.passwordForm.new !== this.passwordForm.confirm) {
                alert('New passwords do not match')
                return
            }

            try {
                const token = localStorage.getItem('token')
                const response = await fetch('/api/v1/auth/change-password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        current_password: this.passwordForm.current,
                        new_password: this.passwordForm.new
                    })
                })

                if (response.ok) {
                    alert('Password changed successfully')
                    this.showPasswordChange = false
                    this.passwordForm = { current: '', new: '', confirm: '' }
                } else {
                    const error = await response.json()
                    alert(error.error || 'Failed to change password')
                }
            } catch (error) {
                console.error('Error changing password:', error)
                alert('Failed to change password')
            }
        },
        formatDate(dateString) {
            return new Date(dateString).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
        }
    }
}
</script>

<style scoped>
.user-profile {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

.profile-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.user-info {
    display: flex;
    gap: 1.5rem;
}

.avatar {
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #3B82F6, #1D4ED8);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 2rem;
    font-weight: bold;
}

.user-details h1 {
    margin: 0 0 0.5rem 0;
    color: #1F2937;
    font-size: 2rem;
}

.email {
    color: #6B7280;
    margin: 0 0 1rem 0;
}

.user-stats {
    display: flex;
    gap: 2rem;
}

.stat {
    text-align: center;
}

.stat-value {
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
    color: #1F2937;
}

.stat-label {
    font-size: 0.875rem;
    color: #6B7280;
}

.profile-actions {
    display: flex;
    gap: 1rem;
}

.analytics-section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.analytics-section h2 {
    margin-top: 0;
    color: #1F2937;
}

.analytics-subtitle {
    color: #6B7280;
    margin-bottom: 1.5rem;
    font-size: 1rem;
}

.filter-controls {
    margin-bottom: 2rem;
    display: flex;
    gap: 1rem;
    align-items: center;
}

.filter-controls select {
    padding: 0.5rem 1rem;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    background: white;
}

.btn-small {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
}

.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}

.chart-container {
    background: #F9FAFB;
    padding: 1.5rem;
    border-radius: 8px;
}

.chart-container h3 {
    margin-top: 0;
    margin-bottom: 1rem;
    color: #374151;
    font-size: 1.125rem;
}

.chart {
    height: 300px !important;
}

.insights-section {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid #E5E7EB;
}

.insights-section h3 {
    margin-bottom: 1.5rem;
    color: #1F2937;
    font-size: 1.25rem;
}

.insights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.insight-card {
    background: #F9FAFB;
    padding: 1.5rem;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 1rem;
    border-left: 4px solid #3B82F6;
}

.insight-icon {
    font-size: 2rem;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.insight-content h4 {
    margin: 0 0 0.25rem 0;
    color: #374151;
    font-size: 0.875rem;
    font-weight: 600;
}

.insight-content p {
    margin: 0;
    color: #1F2937;
    font-weight: 500;
}

.spending-summary {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.spending-summary h2 {
    margin-top: 0;
    color: #1F2937;
}

.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.summary-card {
    background: #F9FAFB;
    padding: 1.5rem;
    border-radius: 8px;
    text-align: center;
}

.summary-card h4 {
    margin: 0 0 0.5rem 0;
    color: #6B7280;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.amount {
    font-size: 2rem;
    font-weight: bold;
    margin: 0;
    color: #1F2937;
}

.amount.positive {
    color: #10B981;
}

.amount.negative {
    color: #EF4444;
}

.savings-label {
    display: block;
    font-size: 0.75rem;
    font-weight: normal;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

.lot-name {
    font-size: 1.25rem;
    font-weight: bold;
    margin: 0;
    color: #3B82F6;
}

.recent-activity {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.recent-activity h2 {
    margin-top: 0;
    color: #1F2937;
}

.activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.activity-item {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: #F9FAFB;
    border-radius: 8px;
}

.activity-icon {
    width: 40px;
    height: 40px;
    background: #3B82F6;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    flex-shrink: 0;
}

.activity-details h4 {
    margin: 0 0 0.25rem 0;
    color: #1F2937;
}

.activity-details p {
    margin: 0 0 0.5rem 0;
    color: #6B7280;
    font-size: 0.875rem;
}

.activity-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
}

.duration {
    color: #10B981;
    font-weight: 500;
}

.cost {
    color: #3B82F6;
    font-weight: 500;
}

.status {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 500;
}

.status.completed {
    background: #D1FAE5;
    color: #065F46;
}

.status.active {
    background: #DBEAFE;
    color: #1E40AF;
}

.status.cancelled {
    background: #FEE2E2;
    color: #991B1B;
}

.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    font-weight: 500;
    text-decoration: none;
    display: inline-block;
    text-align: center;
    transition: all 0.2s;
}

.btn-primary {
    background: #3B82F6;
    color: white;
}

.btn-primary:hover {
    background: #2563EB;
}

.btn-outline {
    background: transparent;
    color: #3B82F6;
    border: 1px solid #3B82F6;
}

.btn-outline:hover {
    background: #3B82F6;
    color: white;
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
    padding: 2rem;
    border-radius: 12px;
    max-width: 400px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.modal h3 {
    margin-top: 0;
    color: #1F2937;
}

.form-group {
    margin-bottom: 1rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #374151;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    box-sizing: border-box;
}

.form-group input:focus {
    outline: none;
    border-color: #3B82F6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
}

@media (max-width: 768px) {
    .user-profile {
        padding: 1rem;
    }

    .profile-header {
        flex-direction: column;
        gap: 1.5rem;
    }

    .user-info {
        flex-direction: column;
        text-align: center;
    }

    .user-stats {
        justify-content: center;
    }

    .charts-grid {
        grid-template-columns: 1fr;
    }

    .summary-cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .activity-item {
        flex-direction: column;
        text-align: center;
    }
}
</style>
