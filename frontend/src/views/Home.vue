<template>
    <AppLayout>
        <div class="home">
            <header class="text-center py-5 mb-5 bg-light rounded-3 shadow-sm hero-section">
                <div class="container py-5">
                    <h1 class="display-3 fw-bold text-primary mb-3">Vehicle Parking Management</h1>
                    <p class="lead text-muted mb-4">Find and reserve parking spots easily, anytime, anywhere.</p>
                    <div class="d-flex gap-3 justify-content-center">
                        <router-link to="/login" class="btn btn-primary btn-lg px-5">Get Started</router-link>
                        <router-link to="/parking-lots" class="btn btn-outline-primary btn-lg px-5">View Lots</router-link>
                    </div>
                </div>
            </header>

            <section class="mb-5">
                <div class="text-center mb-5">
                    <h2 class="fw-bold">Why Choose Us?</h2>
                    <p class="text-muted">Simple, fast, and secure parking solutions</p>
                </div>
                
                <div class="row g-4">
                    <div class="col-md-4">
                        <BaseCard class="h-100 text-center border-0 shadow-sm hover-up">
                            <div class="mb-3 text-primary">
                                <i class="bi bi-clock-history fs-1"></i>
                            </div>
                            <h3 class="h5 fw-bold mb-3">Real-time Availability</h3>
                            <p class="text-muted mb-0">Check parking spot availability in real-time across multiple locations to save time.</p>
                        </BaseCard>
                    </div>
                    
                    <div class="col-md-4">
                        <BaseCard class="h-100 text-center border-0 shadow-sm hover-up">
                            <div class="mb-3 text-success">
                                <i class="bi bi-calendar-check fs-1"></i>
                            </div>
                            <h3 class="h5 fw-bold mb-3">Easy Reservations</h3>
                            <p class="text-muted mb-0">Reserve your preferred parking spot in advance with just a few clicks.</p>
                        </BaseCard>
                    </div>
                    
                    <div class="col-md-4">
                        <BaseCard class="h-100 text-center border-0 shadow-sm hover-up">
                            <div class="mb-3 text-info">
                                <i class="bi bi-geo-alt fs-1"></i>
                            </div>
                            <h3 class="h5 fw-bold mb-3">Multiple Locations</h3>
                            <p class="text-muted mb-0">Access a wide network of parking lots conveniently located around the city.</p>
                        </BaseCard>
                    </div>
                </div>
            </section>
        </div>
    </AppLayout>
</template>

<script setup>
import AppLayout from '../components/layout/AppLayout.vue'
import BaseCard from '../components/common/BaseCard.vue'
</script>

<style scoped>
.hero-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.hover-up {
    transition: transform 0.3s ease;
}

.hover-up:hover {
    transform: translateY(-5px);
}
</style>
