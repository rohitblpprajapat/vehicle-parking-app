// Authentication utility functions

export function isAuthenticated() {
    // Check if we have a login flag (assuming session cookie exists)
    return !!localStorage.getItem('isLoggedIn')
}

export function getUserRoles() {
    const roles = localStorage.getItem('userRoles')
    return roles ? JSON.parse(roles) : []
}

export function hasRole(role) {
    const roles = getUserRoles()
    return roles.includes(role)
}

export function isAdmin() {
    return hasRole('admin')
}

export function getUserInfo() {
    return {
        email: localStorage.getItem('userEmail'),
        name: localStorage.getItem('userName'),
        roles: getUserRoles(),
        // Token is no longer accessible via JS (HttpOnly Cookie)
        token: null
    }
}

export function setSession(user) {
    localStorage.setItem('isLoggedIn', 'true')
    localStorage.setItem('userEmail', user.email)
    localStorage.setItem('userName', user.name)
    localStorage.setItem('userRoles', JSON.stringify(user.roles))
}

export function logout() {
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('authToken') // Clean up old token if present
    localStorage.removeItem('userEmail')
    localStorage.removeItem('userName')
    localStorage.removeItem('userRoles')
}

export function redirectBasedOnRole(router) {
    if (isAdmin()) {
        router.push('/admin/dashboard')
    } else if (isAuthenticated()) {
        router.push('/dashboard')
    } else {
        router.push('/login')
    }
}
