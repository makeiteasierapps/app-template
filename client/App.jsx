function App() {
    return (
        <main className="min-h-screen flex items-center justify-center bg-background text-foreground">
            <div className="max-w-xl px-6 py-8 rounded-xl border border-border shadow-sm bg-card">
                <h1 className="text-3xl font-bold mb-2">__PROJECT_NAME__</h1>
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
            </div>
        </main>
    );
}

export default App;
