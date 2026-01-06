<template>
    <div class="login-page d-flex align-items-center justify-content-center bg-light min-vh-100">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6 col-lg-5">
                    <BaseCard class="shadow-lg border-0">
                        <template #header>
                             <ul class="nav nav-tabs card-header-tabs w-100 justify-content-center border-bottom-0">
                                <li class="nav-item w-50 text-center">
                                    <a :class="['nav-link', { active: activeTab === 'login' }]" 
                                       href="#" 
                                       @click.prevent="activeTab = 'login'">Login</a>
                                </li>
                                <li class="nav-item w-50 text-center">
                                    <a :class="['nav-link', { active: activeTab === 'register' }]" 
                                       href="#" 
                                       @click.prevent="activeTab = 'register'">Register</a>
                                </li>
                            </ul>
                        </template>

                        <div class="p-3">
                            <!-- Login Form -->
                            <form v-if="activeTab === 'login'" @submit.prevent="handleLogin">
                                <h3 class="text-center mb-4">Welcome Back</h3>
                                
                                <BaseInput 
                                    id="email" 
                                    label="Email Address" 
                                    type="email" 
                                    v-model="loginForm.email" 
                                    required 
                                    placeholder="name@example.com"
                                />

                                <BaseInput 
                                    id="password" 
                                    label="Password" 
                                    type="password" 
                                    v-model="loginForm.password" 
                                    required 
                                    placeholder="Enter your password"
                                />

                                <BaseButton 
                                    type="submit" 
                                    variant="primary" 
                                    size="lg" 
                                    block 
                                    :loading="loading"
                                    class="mt-4"
                                >
                                    Login
                                </BaseButton>
                            </form>

                            <!-- Register Form -->
                            <form v-else @submit.prevent="handleRegister">
                                <h3 class="text-center mb-4">Create Account</h3>

                                <BaseInput 
                                    id="reg-name" 
                                    label="Full Name" 
                                    type="text" 
                                    v-model="registerForm.name" 
                                    required 
                                    placeholder="John Doe"
                                />

                                <BaseInput 
                                    id="reg-email" 
                                    label="Email Address" 
                                    type="email" 
                                    v-model="registerForm.email" 
                                    required 
                                    placeholder="name@example.com"
                                />

                                <BaseInput 
                                    id="reg-password" 
                                    label="Password" 
                                    type="password" 
                                    v-model="registerForm.password" 
                                    required 
                                    placeholder="Choose a password (min 6 chars)"
                                />

                                <BaseInput 
                                    id="confirm-password" 
                                    label="Confirm Password" 
                                    type="password" 
                                    v-model="registerForm.confirmPassword" 
                                    required 
                                    placeholder="Confirm your password"
                                />

                                <BaseButton 
                                    type="submit" 
                                    variant="success" 
                                    size="lg" 
                                    block 
                                    :loading="loading"
                                    class="mt-4"
                                >
                                    Register
                                </BaseButton>
                            </form>

                            <div v-if="message" :class="['alert mt-4 text-center', messageType === 'error' ? 'alert-danger' : 'alert-success']" role="alert">
                                {{ message }}
                            </div>
                        </div>
                    </BaseCard>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseCard from '../components/common/BaseCard.vue'
import BaseInput from '../components/common/BaseInput.vue'
import BaseButton from '../components/common/BaseButton.vue'
import { API_BASE_URL } from '@/config'
import { setSession } from '../utils/auth.js'

const router = useRouter()

// Reactive data
const activeTab = ref('login')
const loading = ref(false)
const message = ref('')
const messageType = ref('')

const loginForm = ref({
    email: '',
    password: ''
})

const registerForm = ref({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
})

// Login function
const handleLogin = async () => {
    if (!loginForm.value.email || !loginForm.value.password) {
        showMessage('Please fill in all fields', 'error')
        return
    }

    loading.value = true
    message.value = ''

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                identity: loginForm.value.email,
                password: loginForm.value.password
            })
        })

        const data = await response.json()

        if (response.ok) {
            // Store the session info (token is now HttpOnly cookie)
            setSession(data.response.user)

            showMessage('Login successful!', 'success')

            // Redirect based on user role
            setTimeout(() => {
                const roles = data.response.user.roles || []
                if (roles.includes('admin')) {
                    router.push('/admin/dashboard')
                } else {
                    router.push('/dashboard')
                }
            }, 1000)
        } else {
            showMessage(data.response.errors?.[0] || 'Login failed', 'error')
        }
    } catch (error) {
        console.error('Login error:', error)
        showMessage('Network error. Please try again.', 'error')
    } finally {
        loading.value = false
    }
}

// Register function
const handleRegister = async () => {
    if (!registerForm.value.name || !registerForm.value.email || !registerForm.value.password || !registerForm.value.confirmPassword) {
        showMessage('Please fill in all fields', 'error')
        return
    }

    if (registerForm.value.password !== registerForm.value.confirmPassword) {
        showMessage('Passwords do not match', 'error')
        return
    }

    if (registerForm.value.password.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error')
        return
    }

    loading.value = true
    message.value = ''

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: registerForm.value.name,
                email: registerForm.value.email,
                password: registerForm.value.password
            })
        })

        const data = await response.json()

        if (response.ok) {
            showMessage('Registration successful! Please login.', 'success')

            // Clear form and switch to login tab
            registerForm.value = {
                name: '',
                email: '',
                password: '',
                confirmPassword: ''
            }

            setTimeout(() => {
                activeTab.value = 'login'
                loginForm.value.email = data.response.user.email
            }, 1500)
        } else {
            showMessage(data.response?.errors?.[0] || 'Registration failed', 'error')
        }
    } catch (error) {
        console.error('Registration error:', error)
        showMessage('Network error. Please try again.', 'error')
    } finally {
        loading.value = false
    }
}

// Helper function to show messages
const showMessage = (msg, type) => {
    message.value = msg
    messageType.value = type

    // Auto-hide success messages after 3 seconds
    if (type === 'success') {
        setTimeout(() => {
            message.value = ''
        }, 3000)
    }
}
</script>

<style scoped>
.nav-link {
    font-weight: 500;
    color: #6c757d;
}
.nav-link.active {
    color: #0d6efd;
    font-weight: 600;
    background-color: transparent;
    border-bottom: 3px solid #0d6efd !important;
}
</style>
