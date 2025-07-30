// Authentication utility functions

export function isAuthenticated() {
    return !!localStorage.getItem('authToken')
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
        token: localStorage.getItem('authToken')
    }
}

export function logout() {
    localStorage.removeItem('authToken')
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
