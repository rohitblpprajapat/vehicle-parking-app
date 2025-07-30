<template>
    <div class="login-page">
        <div class="login-container">
            <div class="login-card">
                <div class="tab-container">
                    <div class="tabs">
                        <button :class="['tab', { active: activeTab === 'login' }]" @click="activeTab = 'login'">
                            Login
                        </button>
                        <button :class="['tab', { active: activeTab === 'register' }]" @click="activeTab = 'register'">
                            Register
                        </button>
                    </div>

                    <!-- Login Form -->
                    <div v-if="activeTab === 'login'" class="form-container">
                        <h2>Login</h2>
                        <form @submit.prevent="handleLogin" class="auth-form">
                            <div class="form-group">
                                <label for="email">Email:</label>
                                <input type="email" id="email" v-model="loginForm.email" required :disabled="loading"
                                    placeholder="Enter your email" />
                            </div>
                            <div class="form-group">
                                <label for="password">Password:</label>
                                <input type="password" id="password" v-model="loginForm.password" required
                                    :disabled="loading" placeholder="Enter your password" />
                            </div>
                            <button type="submit" :disabled="loading" class="auth-button">
                                {{ loading ? 'Logging in...' : 'Login' }}
                            </button>
                        </form>
                    </div>

                    <!-- Register Form -->
                    <div v-else class="form-container">
                        <h2>Register</h2>
                        <form @submit.prevent="handleRegister" class="auth-form">
                            <div class="form-group">
                                <label for="reg-name">Full Name:</label>
                                <input type="text" id="reg-name" v-model="registerForm.name" required
                                    :disabled="loading" placeholder="Enter your full name" />
                            </div>
                            <div class="form-group">
                                <label for="reg-email">Email:</label>
                                <input type="email" id="reg-email" v-model="registerForm.email" required
                                    :disabled="loading" placeholder="Enter your email" />
                            </div>
                            <div class="form-group">
                                <label for="reg-password">Password:</label>
                                <input type="password" id="reg-password" v-model="registerForm.password" required
                                    :disabled="loading" placeholder="Choose a password" />
                            </div>
                            <div class="form-group">
                                <label for="confirm-password">Confirm Password:</label>
                                <input type="password" id="confirm-password" v-model="registerForm.confirmPassword"
                                    required :disabled="loading" placeholder="Confirm your password" />
                            </div>
                            <button type="submit" :disabled="loading" class="auth-button">
                                {{ loading ? 'Registering...' : 'Register' }}
                            </button>
                        </form>
                    </div>

                    <div v-if="message" :class="['message', messageType]">
                        {{ message }}
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

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
        const response = await fetch('http://127.0.0.1:5000/api/v1/auth/login', {
            method: 'POST',
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
            // Store the token and user info
            localStorage.setItem('authToken', data.response.user.authentication_token)
            localStorage.setItem('userEmail', data.response.user.email)
            localStorage.setItem('userName', data.response.user.name)
            localStorage.setItem('userRoles', JSON.stringify(data.response.user.roles))

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
        const response = await fetch('http://127.0.0.1:5000/api/v1/auth/register', {
            method: 'POST',
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
.login-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.login-container {
    width: 100%;
    max-width: 450px;
}

.login-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.tab-container {
    width: 100%;
}

.tabs {
    display: flex;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #eee;
}

.tab {
    flex: 1;
    padding: 12px 20px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: #666;
    border-bottom: 2px solid transparent;
    transition: all 0.3s ease;
}

.tab:hover {
    color: #667eea;
}

.tab.active {
    color: #667eea;
    border-bottom-color: #667eea;
    font-weight: 600;
}

.form-container {
    text-align: center;
}

.form-container h2 {
    margin-bottom: 1.5rem;
    color: #333;
    font-size: 1.8rem;
}

.auth-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-group {
    text-align: left;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: #333;
    font-weight: 500;
}

.form-group input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
    transition: border-color 0.3s ease;
    box-sizing: border-box;
}

.form-group input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.form-group input:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
}

.auth-button {
    padding: 12px 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-top: 1rem;
}

.auth-button:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.auth-button:active {
    transform: translateY(0);
}

.auth-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

.message {
    margin-top: 1rem;
    padding: 12px;
    border-radius: 6px;
    text-align: center;
    font-weight: 500;
}

.message.success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.message.error {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}
</style>
