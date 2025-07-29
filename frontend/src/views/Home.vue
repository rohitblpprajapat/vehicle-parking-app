<template>
    <div class="home">
        <header class="hero-section">
            <div class="hero-content">
                <h1>Vehicle Parking Management System</h1>
                <p>Find and reserve parking spots easily</p>
                <div class="cta-buttons">
                    <router-link to="/login" class="btn btn-primary">Get Started</router-link>
                    <router-link to="/parking-lots" class="btn btn-secondary">View Parking Lots</router-link>
                </div>
            </div>
        </header>

        <section class="features">
            <div class="container">
                <h2>Features</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>Real-time Availability</h3>
                        <p>Check parking spot availability in real-time</p>
                    </div>
                    <div class="feature-card">
                        <h3>Easy Reservations</h3>
                        <p>Reserve your parking spot in advance</p>
                    </div>
                    <div class="feature-card">
                        <h3>Multiple Locations</h3>
                        <p>Access parking lots across different locations</p>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
// Home page logic here
</script>

<style scoped>
.home {
    min-height: 100vh;
}

.hero-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 100px 20px;
    text-align: center;
}

.hero-content h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero-content p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

.cta-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.btn {
    padding: 12px 24px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-primary {
    background-color: #4CAF50;
    color: white;
}

.btn-primary:hover {
    background-color: #45a049;
}

.btn-secondary {
    background-color: transparent;
    color: white;
    border: 2px solid white;
}

.btn-secondary:hover {
    background-color: white;
    color: #667eea;
}

.features {
    padding: 80px 20px;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

.features h2 {
    text-align: center;
    margin-bottom: 3rem;
    font-size: 2.5rem;
    color: #333;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.feature-card h3 {
    color: #667eea;
    margin-bottom: 1rem;
}

.feature-card p {
    color: #666;
    line-height: 1.6;
}
</style>
