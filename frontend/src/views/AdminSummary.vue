<template>
    <div class="admin-summary">
        <!-- Navigation -->
        <nav class="navbar">
            <div class="nav-brand">
                <h3>Admin Analytics</h3>
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

        <main class="dashboard-content">
            <div class="container">
                <!-- Header Section -->
                <div class="summary-header">
                    <h1>Administrative Dashboard</h1>
                    <div class="date-range-selector">
                        <select v-model="selectedPeriod" @change="loadAnalytics">
                            <option value="7">Last 7 Days</option>
                            <option value="30">Last 30 Days</option>
                            <option value="90">Last 3 Months</option>
                            <option value="365">Last Year</option>
                            <option value="all">All Time</option>
                        </select>
                    </div>
                </div>

                <!-- Key Metrics Overview -->
                <div class="metrics-overview">
                    <div class="metric-card revenue">
                        <div class="metric-icon">💰</div>
                        <div class="metric-content">
                            <h3>Total Revenue</h3>
                            <p class="metric-value">${{ totalRevenue.toLocaleString('en-US', {
                                minimumFractionDigits: 2
                            }) }}
                            </p>
                            <span class="metric-change" :class="revenueChange >= 0 ? 'positive' : 'negative'">
                                {{ revenueChange >= 0 ? '+' : '' }}{{ revenueChange.toFixed(1) }}%
                            </span>
                        </div>
                    </div>

                    <div class="metric-card bookings">
                        <div class="metric-icon">🚗</div>
                        <div class="metric-content">
                            <h3>Total Bookings</h3>
                            <p class="metric-value">{{ totalBookings.toLocaleString() }}</p>
                            <span class="metric-change" :class="bookingsChange >= 0 ? 'positive' : 'negative'">
                                {{ bookingsChange >= 0 ? '+' : '' }}{{ bookingsChange.toFixed(1) }}%
                            </span>
                        </div>
                    </div>

                    <div class="metric-card occupancy">
                        <div class="metric-icon">📊</div>
                        <div class="metric-content">
                            <h3>Avg Occupancy</h3>
                            <p class="metric-value">{{ averageOccupancy.toFixed(1) }}%</p>
                            <span class="metric-change" :class="occupancyChange >= 0 ? 'positive' : 'negative'">
                                {{ occupancyChange >= 0 ? '+' : '' }}{{ occupancyChange.toFixed(1) }}%
                            </span>
                        </div>
                    </div>

                    <div class="metric-card users">
                        <div class="metric-icon">👥</div>
                        <div class="metric-content">
                            <h3>Active Users</h3>
                            <p class="metric-value">{{ activeUsers.toLocaleString() }}</p>
                            <span class="metric-change" :class="usersChange >= 0 ? 'positive' : 'negative'">
                                {{ usersChange >= 0 ? '+' : '' }}{{ usersChange.toFixed(1) }}%
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Main Analytics Charts -->
                <div class="main-charts">
                    <!-- Revenue Over Time -->
                    <div class="chart-section">
                        <div class="chart-header">
                            <h2>Revenue Analytics</h2>
                            <div class="chart-controls">
                                <button v-for="period in ['daily', 'weekly', 'monthly']" :key="period"
                                    @click="revenueChartPeriod = period; updateRevenueChart()"
                                    :class="{ active: revenueChartPeriod === period }" class="period-btn">
                                    {{ period.charAt(0).toUpperCase() + period.slice(1) }}
                                </button>
                            </div>
                        </div>
                        <div class="chart-container">
                            <canvas ref="revenueChart" class="chart"></canvas>
                        </div>
                    </div>

                    <!-- Parking Lot Performance -->
                    <div class="chart-section">
                        <h2>Parking Lot Performance</h2>
                        <div class="chart-container">
                            <canvas ref="lotPerformanceChart" class="chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Secondary Charts Grid -->
                <div class="secondary-charts">
                    <!-- Booking Trends -->
                    <div class="chart-card">
                        <h3>Booking Trends</h3>
                        <div class="chart-container">
                            <canvas ref="bookingTrendsChart" class="chart"></canvas>
                        </div>
                    </div>

                    <!-- Occupancy Heatmap -->
                    <div class="chart-card">
                        <h3>Hourly Occupancy Pattern</h3>
                        <div class="chart-container">
                            <canvas ref="occupancyHeatmapChart" class="chart"></canvas>
                        </div>
                    </div>

                    <!-- Revenue Distribution -->
                    <div class="chart-card">
                        <h3>Revenue by Parking Lot</h3>
                        <div class="chart-container">
                            <canvas ref="revenueDistributionChart" class="chart"></canvas>
                        </div>
                    </div>

                    <!-- User Activity -->
                    <div class="chart-card">
                        <h3>User Activity Patterns</h3>
                        <div class="chart-container">
                            <canvas ref="userActivityChart" class="chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Detailed Analytics Tables -->
                <div class="analytics-tables">
                    <!-- Top Performing Lots -->
                    <div class="table-section">
                        <h2>Top Performing Parking Lots</h2>
                        <div class="table-container">
                            <table class="analytics-table">
                                <thead>
                                    <tr>
                                        <th>Parking Lot</th>
                                        <th>Revenue</th>
                                        <th>Bookings</th>
                                        <th>Avg Occupancy</th>
                                        <th>Avg Duration</th>
                                        <th>Revenue/Hour</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="lot in topPerformingLots" :key="lot.id">
                                        <td class="lot-name">{{ lot.name }}</td>
                                        <td class="revenue">${{ lot.revenue.toFixed(2) }}</td>
                                        <td>{{ lot.bookings }}</td>
                                        <td>{{ lot.occupancy.toFixed(1) }}%</td>
                                        <td>{{ lot.avgDuration.toFixed(1) }}h</td>
                                        <td>${{ lot.revenuePerHour.toFixed(2) }}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Recent Transactions -->
                    <div class="table-section">
                        <h2>Recent High-Value Transactions</h2>
                        <div class="table-container">
                            <table class="analytics-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>User</th>
                                        <th>Parking Lot</th>
                                        <th>Duration</th>
                                        <th>Amount</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="transaction in recentTransactions" :key="transaction.id">
                                        <td>{{ formatDate(transaction.date) }}</td>
                                        <td>{{ transaction.userName }}</td>
                                        <td>{{ transaction.parkingLot }}</td>
                                        <td>{{ transaction.duration.toFixed(1) }}h</td>
                                        <td class="amount">${{ transaction.amount.toFixed(2) }}</td>
                                        <td>
                                            <span class="status-badge" :class="transaction.status.toLowerCase()">
                                                {{ transaction.status }}
                                            </span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Export and Reports Section -->
                <div class="reports-section">
                    <h2>Reports & Export</h2>
                    <div class="report-actions">
                        <button @click="exportRevenueReport" class="btn btn-primary">
                            📊 Export Revenue Report
                        </button>
                        <button @click="exportOccupancyReport" class="btn btn-secondary">
                            📈 Export Occupancy Report
                        </button>
                        <button @click="exportUserReport" class="btn btn-secondary">
                            👥 Export User Report
                        </button>
                        <button @click="generatePredictiveReport" class="btn btn-accent">
                            🔮 Generate Predictive Analysis
                        </button>
                    </div>
                </div>

                <!-- Loading Overlay -->
                <div v-if="loading" class="loading-overlay">
                    <div class="loading-spinner"></div>
                    <p>Loading analytics data...</p>
                </div>
            </div>
        </main>
    </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
import 'chartjs-adapter-date-fns'

Chart.register(...registerables)

export default {
    name: 'AdminSummary',
    data() {
        return {
            selectedPeriod: '30',
            revenueChartPeriod: 'daily',
            loading: true,

            // Analytics Data
            analyticsData: null,

            // Charts
            charts: {
                revenue: null,
                lotPerformance: null,
                bookingTrends: null,
                occupancyHeatmap: null,
                revenueDistribution: null,
                userActivity: null
            },

            // Computed metrics
            previousPeriodData: null
        }
    },
    computed: {
        totalRevenue() {
            return this.analyticsData?.summary?.total_revenue || 0
        },
        totalBookings() {
            return this.analyticsData?.summary?.total_bookings || 0
        },
        averageOccupancy() {
            return this.analyticsData?.summary?.average_occupancy || 0
        },
        activeUsers() {
            return this.analyticsData?.summary?.active_users || 0
        },
        revenueChange() {
            if (!this.previousPeriodData) return 0
            const current = this.totalRevenue
            const previous = this.previousPeriodData.total_revenue || 1
            return ((current - previous) / previous) * 100
        },
        bookingsChange() {
            if (!this.previousPeriodData) return 0
            const current = this.totalBookings
            const previous = this.previousPeriodData.total_bookings || 1
            return ((current - previous) / previous) * 100
        },
        occupancyChange() {
            if (!this.previousPeriodData) return 0
            const current = this.averageOccupancy
            const previous = this.previousPeriodData.average_occupancy || 1
            return ((current - previous) / previous) * 100
        },
        usersChange() {
            if (!this.previousPeriodData) return 0
            const current = this.activeUsers
            const previous = this.previousPeriodData.active_users || 1
            return ((current - previous) / previous) * 100
        },
        topPerformingLots() {
            return this.analyticsData?.parking_lots?.slice(0, 10) || []
        },
        recentTransactions() {
            return this.analyticsData?.recent_transactions?.slice(0, 20) || []
        }
    },
    async mounted() {
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
        async loadAnalytics() {
            try {
                const token = localStorage.getItem('authToken')

                // Load current period data
                const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/analytics?days=${this.selectedPeriod}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': token
                    }
                })
                if (response.ok) {
                    this.analyticsData = await response.json()
                }

                // Load previous period for comparison
                const prevResponse = await fetch(`http://127.0.0.1:5000/api/v1/admin/analytics/previous?days=${this.selectedPeriod}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': token
                    }
                })
                if (prevResponse.ok) {
                    this.previousPeriodData = await prevResponse.json()
                }

                this.$nextTick(() => {
                    this.createCharts()
                })
            } catch (error) {
                console.error('Error loading analytics:', error)
            }
        },
        createCharts() {
            this.createRevenueChart()
            this.createLotPerformanceChart()
            this.createBookingTrendsChart()
            this.createOccupancyHeatmapChart()
            this.createRevenueDistributionChart()
            this.createUserActivityChart()
        },
        createRevenueChart() {
            const ctx = this.$refs.revenueChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.revenue) {
                this.charts.revenue.destroy()
            }

            const revenueData = this.analyticsData?.revenue_over_time || []
            const labels = revenueData.map(item => item.date)
            const data = revenueData.map(item => item.revenue)

            this.charts.revenue = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [{
                        label: 'Revenue',
                        data,
                        borderColor: '#10B981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
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
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: '#10B981',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: value => `$${value.toLocaleString()}`
                            }
                        },
                        x: {
                            ticks: {
                                maxTicksLimit: 10
                            }
                        }
                    }
                }
            })
        },
        createLotPerformanceChart() {
            const ctx = this.$refs.lotPerformanceChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.lotPerformance) {
                this.charts.lotPerformance.destroy()
            }

            const lotData = this.analyticsData?.parking_lots?.slice(0, 8) || []
            const labels = lotData.map(lot => lot.name)
            const revenueData = lotData.map(lot => lot.revenue)
            const occupancyData = lotData.map(lot => lot.occupancy)

            this.charts.lotPerformance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Revenue ($)',
                            data: revenueData,
                            backgroundColor: '#3B82F6',
                            borderRadius: 4,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Occupancy (%)',
                            data: occupancyData,
                            backgroundColor: '#F59E0B',
                            borderRadius: 4,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,
                            ticks: {
                                callback: value => `$${value.toLocaleString()}`
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                drawOnChartArea: false
                            },
                            ticks: {
                                callback: value => `${value}%`
                            }
                        }
                    }
                }
            })
        },
        createBookingTrendsChart() {
            const ctx = this.$refs.bookingTrendsChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.bookingTrends) {
                this.charts.bookingTrends.destroy()
            }

            const bookingData = this.analyticsData?.booking_trends || []
            const labels = bookingData.map(item => item.date)
            const data = bookingData.map(item => item.bookings)

            this.charts.bookingTrends = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [{
                        label: 'Bookings',
                        data,
                        backgroundColor: '#8B5CF6',
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
                            beginAtZero: true
                        }
                    }
                }
            })
        },
        createOccupancyHeatmapChart() {
            const ctx = this.$refs.occupancyHeatmapChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.occupancyHeatmap) {
                this.charts.occupancyHeatmap.destroy()
            }

            // Create hourly occupancy data
            const hourlyData = this.analyticsData?.hourly_occupancy || []
            const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`)
            const occupancyByHour = hours.map(hour => {
                const hourData = hourlyData.find(item => item.hour === parseInt(hour))
                return hourData ? hourData.occupancy : 0
            })

            this.charts.occupancyHeatmap = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: hours,
                    datasets: [{
                        label: 'Occupancy %',
                        data: occupancyByHour,
                        borderColor: '#EF4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
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
                            max: 100,
                            ticks: {
                                callback: value => `${value}%`
                            }
                        }
                    }
                }
            })
        },
        createRevenueDistributionChart() {
            const ctx = this.$refs.revenueDistributionChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.revenueDistribution) {
                this.charts.revenueDistribution.destroy()
            }

            const lotData = this.analyticsData?.parking_lots?.slice(0, 6) || []
            const labels = lotData.map(lot => lot.name)
            const data = lotData.map(lot => lot.revenue)

            this.charts.revenueDistribution = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels,
                    datasets: [{
                        data,
                        backgroundColor: [
                            '#3B82F6',
                            '#10B981',
                            '#F59E0B',
                            '#EF4444',
                            '#8B5CF6',
                            '#06B6D4'
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
        createUserActivityChart() {
            const ctx = this.$refs.userActivityChart?.getContext('2d')
            if (!ctx) return

            if (this.charts.userActivity) {
                this.charts.userActivity.destroy()
            }

            const activityData = this.analyticsData?.user_activity || []
            const labels = activityData.map(item => item.date)
            const newUsers = activityData.map(item => item.new_users)
            const activeUsers = activityData.map(item => item.active_users)

            this.charts.userActivity = new Chart(ctx, {
                type: 'line',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'New Users',
                            data: newUsers,
                            borderColor: '#10B981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Active Users',
                            data: activeUsers,
                            borderColor: '#3B82F6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        },
        updateRevenueChart() {
            this.createRevenueChart()
        },
        async exportRevenueReport() {
            try {
                const token = localStorage.getItem('authToken')
                const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/reports/revenue?days=${this.selectedPeriod}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': token
                    }
                })
                const blob = await response.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `revenue-report-${this.selectedPeriod}days.csv`
                a.click()
                window.URL.revokeObjectURL(url)
            } catch (error) {
                console.error('Error exporting revenue report:', error)
                alert('Failed to export revenue report')
            }
        },
        async exportOccupancyReport() {
            try {
                const token = localStorage.getItem('authToken')
                const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/reports/occupancy?days=${this.selectedPeriod}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': token
                    }
                })
                const blob = await response.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `occupancy-report-${this.selectedPeriod}days.csv`
                a.click()
                window.URL.revokeObjectURL(url)
            } catch (error) {
                console.error('Error exporting occupancy report:', error)
                alert('Failed to export occupancy report')
            }
        },
        async exportUserReport() {
            try {
                const token = localStorage.getItem('authToken')
                const response = await fetch(`http://127.0.0.1:5000/api/v1/admin/reports/users?days=${this.selectedPeriod}`, {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': token
                    }
                })
                const blob = await response.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `user-report-${this.selectedPeriod}days.csv`
                a.click()
                window.URL.revokeObjectURL(url)
            } catch (error) {
                console.error('Error exporting user report:', error)
                alert('Failed to export user report')
            }
        },
        async generatePredictiveReport() {
            try {
                const token = localStorage.getItem('authToken')
                const response = await fetch('http://127.0.0.1:5000/api/v1/admin/reports/predictive', {
                    headers: {
                        'Content-Type': 'application/json',
                        'Authentication-Token': token
                    }
                })
                const data = await response.json()

                // Create a new window to show the predictive analysis
                const newWindow = window.open('', '_blank')
                newWindow.document.write(`
                    <html>
                        <head><title>Predictive Analysis Report</title></head>
                        <body>
                            <h1>Predictive Analysis Report</h1>
                            <pre>${JSON.stringify(data, null, 2)}</pre>
                        </body>
                    </html>
                `)
                newWindow.document.close()
            } catch (error) {
                console.error('Error generating predictive report:', error)
                alert('Failed to generate predictive report')
            }
        },
        logout() {
            localStorage.removeItem('authToken')
            this.$router.push('/login')
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
.admin-summary {
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

.btn-logout {
    background: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
}

.btn-logout:hover {
    background: #c82333;
}

.dashboard-content {
    padding: 2rem;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
}

.summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.summary-header h1 {
    color: #1F2937;
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
}

.date-range-selector select {
    padding: 0.75rem 1rem;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    background: white;
    font-size: 1rem;
    color: #374151;
}

.metrics-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.metric-card {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    display: flex;
    align-items: center;
    gap: 1.5rem;
    border-left: 4px solid;
}

.metric-card.revenue {
    border-left-color: #10B981;
}

.metric-card.bookings {
    border-left-color: #3B82F6;
}

.metric-card.occupancy {
    border-left-color: #F59E0B;
}

.metric-card.users {
    border-left-color: #8B5CF6;
}

.metric-icon {
    font-size: 2.5rem;
    width: 60px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #F3F4F6;
    border-radius: 12px;
}

.metric-content h3 {
    margin: 0 0 0.5rem 0;
    color: #6B7280;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
}

.metric-value {
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
    font-weight: 700;
    color: #1F2937;
}

.metric-change {
    font-size: 0.875rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

.metric-change.positive {
    color: #059669;
    background: #D1FAE5;
}

.metric-change.negative {
    color: #DC2626;
    background: #FEE2E2;
}

.main-charts {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    margin-bottom: 3rem;
}

.chart-section {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.chart-header h2 {
    margin: 0;
    color: #1F2937;
    font-size: 1.5rem;
}

.chart-controls {
    display: flex;
    gap: 0.5rem;
}

.period-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #D1D5DB;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.875rem;
    transition: all 0.2s;
}

.period-btn:hover {
    background: #F3F4F6;
}

.period-btn.active {
    background: #3B82F6;
    color: white;
    border-color: #3B82F6;
}

.chart-container {
    height: 400px;
    position: relative;
}

.chart {
    height: 100% !important;
}

.secondary-charts {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.chart-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.chart-card h3 {
    margin: 0 0 1rem 0;
    color: #1F2937;
    font-size: 1.125rem;
}

.chart-card .chart-container {
    height: 300px;
}

.analytics-tables {
    display: grid;
    gap: 2rem;
    margin-bottom: 3rem;
}

.table-section {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.table-section h2 {
    margin: 0 0 1.5rem 0;
    color: #1F2937;
}

.table-container {
    overflow-x: auto;
}

.analytics-table {
    width: 100%;
    border-collapse: collapse;
}

.analytics-table th,
.analytics-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #E5E7EB;
}

.analytics-table th {
    background: #F9FAFB;
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.analytics-table .lot-name {
    font-weight: 600;
    color: #1F2937;
}

.analytics-table .revenue,
.analytics-table .amount {
    font-weight: 600;
    color: #059669;
}

.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-badge.completed {
    background: #D1FAE5;
    color: #065F46;
}

.status-badge.active {
    background: #DBEAFE;
    color: #1E40AF;
}

.status-badge.cancelled {
    background: #FEE2E2;
    color: #991B1B;
}

.reports-section {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin-bottom: 2rem;
}

.reports-section h2 {
    margin: 0 0 1.5rem 0;
    color: #1F2937;
}

.report-actions {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    font-weight: 600;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s;
}

.btn-primary {
    background: #3B82F6;
    color: white;
}

.btn-primary:hover {
    background: #2563EB;
}

.btn-secondary {
    background: #6B7280;
    color: white;
}

.btn-secondary:hover {
    background: #4B5563;
}

.btn-accent {
    background: #8B5CF6;
    color: white;
}

.btn-accent:hover {
    background: #7C3AED;
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    color: white;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top: 4px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@media (max-width: 1024px) {
    .main-charts {
        grid-template-columns: 1fr;
    }

    .secondary-charts {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    }
}

@media (max-width: 768px) {
    .admin-summary {
        padding: 1rem;
    }

    .summary-header {
        flex-direction: column;
        gap: 1rem;
        text-align: center;
    }

    .metrics-overview {
        grid-template-columns: 1fr;
    }

    .secondary-charts {
        grid-template-columns: 1fr;
    }

    .report-actions {
        flex-direction: column;
    }

    .chart-card .chart-container {
        height: 250px;
    }
}
</style>
