// SSE Client Example

class AuthEventManager {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.eventSource = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second delay
    }

    connect(accessToken) {
        if (this.eventSource) {
            this.disconnect();
        }

        this.eventSource = new EventSource(`${this.baseUrl}/api/v1/auth/sse/notifications/`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        // Handle connection open
        this.eventSource.onopen = () => {
            console.log('SSE connection established');
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
        };

        // Handle force logout events
        this.eventSource.addEventListener('FORCE_LOGOUT', (event) => {
            const data = JSON.parse(event.data);
            console.log('Force logout received:', data.message);
            
            // Clean up local session
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            
            // Disconnect SSE
            this.disconnect();
            
            // Notify application about forced logout
            this.handleForcedLogout(data.message);
        });

        // Handle heartbeat events
        this.eventSource.addEventListener('heartbeat', () => {
            console.log('Heartbeat received');
        });

        // Handle errors
        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            this.eventSource.close();
            
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                setTimeout(() => {
                    this.reconnectAttempts++;
                    this.reconnectDelay *= 2; // Exponential backoff
                    this.connect(accessToken);
                }, this.reconnectDelay);
            }
        };
    }

    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
    }

    handleForcedLogout(message) {
        // Example: Show a modal to the user
        alert(message);
        
        // Example: Redirect to login page
        window.location.href = '/login';
    }
}

// Usage example:
const authEvents = new AuthEventManager('http://localhost:8000');

// Connect when user logs in
function onLogin(accessToken) {
    authEvents.connect(accessToken);
}

// Disconnect when user logs out
function onLogout() {
    authEvents.disconnect();
}

// React component example
function AuthEventHandler({ accessToken }) {
    React.useEffect(() => {
        if (accessToken) {
            const authEvents = new AuthEventManager(process.env.REACT_APP_API_URL);
            authEvents.connect(accessToken);
            
            return () => {
                authEvents.disconnect();
            };
        }
    }, [accessToken]);

    return null;
}
