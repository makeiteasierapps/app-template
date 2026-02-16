const API_BASE = '/api';

async function fetchApi(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers,
        credentials: 'same-origin',
    });

    if (response.status === 401) {
        // Only redirect if we're not already on an auth page
        if (
            !window.location.pathname.startsWith('/login') &&
            !window.location.pathname.startsWith('/register')
        ) {
            window.location.href = '/login';
        }
        throw new Error('Unauthorized');
    }

    return response;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(identifier, password) {
    const response = await fetchApi('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ identifier, password }),
    });
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Login failed');
    }
    return response.json();
}

export async function register({ email, password, firstName, lastName }) {
    const response = await fetchApi('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
            email,
            password,
            first_name: firstName,
            last_name: lastName,
        }),
    });
    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Registration failed');
    }
    return response.json();
}

export async function getSession() {
    const response = await fetch(`${API_BASE}/auth/session`, {
        credentials: 'same-origin',
    });
    if (!response.ok) return null;
    return response.json();
}

export async function logout() {
    await fetchApi('/auth/logout', { method: 'POST' }).catch(() => {});
}
