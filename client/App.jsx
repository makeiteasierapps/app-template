import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Login from '@/pages/Login';
import Register from '@/pages/Register';

function Home() {
    const { user, logout } = useAuth();

    return (
        <main className="min-h-screen flex items-center justify-center bg-background text-foreground">
            <div className="max-w-xl px-6 py-8 rounded-xl border border-border shadow-sm bg-card">
                <h1 className="text-3xl font-bold mb-2">__PROJECT_NAME__</h1>
                {user && (
                    <p className="text-sm text-muted-foreground mb-4">
                        Signed in as{' '}
                        <span className="font-medium text-foreground">
                            {user.email}
                        </span>
                    </p>
                )}
                <p className="text-muted-foreground">
                    Your new full-stack project starter is ready. Start building
                    your app in
                    <code className="px-1 mx-1 rounded bg-muted text-xs">
                        client/
                    </code>{' '}
                    for the frontend and
                    <code className="px-1 mx-1 rounded bg-muted text-xs">
                        server/
                    </code>{' '}
                    for the backend.
                </p>
                {user && (
                    <button
                        onClick={logout}
                        className="mt-4 inline-flex items-center justify-center h-9 px-4 rounded-md border border-input bg-background text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
                    >
                        Sign out
                    </button>
                )}
            </div>
        </main>
    );
}

function AppRoutes() {
    const { user } = useAuth();

    return (
        <Routes>
            <Route
                path="/login"
                element={user ? <Navigate to="/" replace /> : <Login />}
            />
            <Route
                path="/register"
                element={user ? <Navigate to="/" replace /> : <Register />}
            />
            <Route
                path="/*"
                element={
                    <ProtectedRoute>
                        <Home />
                    </ProtectedRoute>
                }
            />
        </Routes>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <AppRoutes />
        </AuthProvider>
    );
}
