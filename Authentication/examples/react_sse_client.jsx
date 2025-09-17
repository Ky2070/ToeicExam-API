import React, { useState, useEffect, useRef, useContext } from 'react';

// Example AuthContext (adjust based on your auth implementation)
const AuthContext = React.createContext();

/**
 * SSE Client Hook for handling Server-Sent Events
 * 
 * This hook manages the SSE connection lifecycle and provides
 * a clean interface for React components to use SSE functionality.
 */
const useSSE = (url, accessToken, options = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [error, setError] = useState(null);
  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  
  const {
    onMessage = () => {},
    onError = () => {},
    onOpen = () => {},
    onClose = () => {},
    reconnectDelay = 3000,
    maxReconnectAttempts = 5
  } = options;
  
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const connect = React.useCallback(() => {
    if (!accessToken || !url) {
      setError('Missing access token or URL');
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      // Create SSE connection with authorization header
      const eventSource = new EventSource(`${url}?token=${encodeURIComponent(accessToken)}`, {
        withCredentials: true
      });

      // Alternative: If your backend supports Authorization header in EventSource
      // Note: Most browsers don't support custom headers in EventSource
      // You might need to pass token as query parameter or use WebSocket instead
      
      eventSourceRef.current = eventSource;

      eventSource.onopen = (event) => {
        console.log('SSE connection opened');
        setIsConnected(true);
        setError(null);
        setReconnectAttempts(0);
        onOpen(event);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setLastMessage(data);
          onMessage(data, event);
        } catch (err) {
          console.warn('Failed to parse SSE message:', event.data);
          setLastMessage({ raw: event.data });
          onMessage({ raw: event.data }, event);
        }
      };

      eventSource.onerror = (event) => {
        console.error('SSE error:', event);
        setIsConnected(false);
        setError('Connection error');
        onError(event);
        
        // Attempt to reconnect
        if (reconnectAttempts < maxReconnectAttempts) {
          console.log(`Attempting to reconnect in ${reconnectDelay}ms... (attempt ${reconnectAttempts + 1})`);
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, reconnectDelay);
        } else {
          console.error('Max reconnect attempts reached');
          setError('Connection failed after multiple attempts');
        }
      };

      // Handle specific event types
      eventSource.addEventListener('heartbeat', (event) => {
        console.log('Heartbeat received');
        // Optional: Update last activity timestamp
      });

      eventSource.addEventListener('message', (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'FORCE_LOGOUT') {
            console.warn('Force logout received:', data.data.message);
            // Handle force logout
            onMessage(data, event);
          }
        } catch (err) {
          console.warn('Failed to parse message event:', event.data);
        }
      });

    } catch (err) {
      console.error('Failed to create EventSource:', err);
      setError('Failed to create connection');
      onError(err);
    }
  }, [url, accessToken, onMessage, onError, onOpen, reconnectDelay, maxReconnectAttempts, reconnectAttempts]);

  const disconnect = React.useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    setIsConnected(false);
    onClose();
  }, [onClose]);

  useEffect(() => {
    if (accessToken) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [accessToken, connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    error,
    connect,
    disconnect,
    reconnectAttempts
  };
};

/**
 * SSE Manager Component
 * 
 * This component handles SSE connections and force logout events.
 * It should be placed at the root level of your application.
 */
const SSEManager = ({ children }) => {
  const { accessToken, logout, user } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);

  const handleSSEMessage = (data, event) => {
    console.log('SSE Message received:', data);
    
    if (data.type === 'FORCE_LOGOUT') {
      // Show notification to user
      const message = data.data?.message || 'Your session has been terminated.';
      
      // Add to notifications
      setNotifications(prev => [...prev, {
        id: Date.now(),
        type: 'warning',
        message: message,
        timestamp: new Date()
      }]);

      // Force logout after a brief delay to show the message
      setTimeout(() => {
        alert(message);
        logout();
      }, 1000);
    } else {
      // Handle other message types
      setNotifications(prev => [...prev, {
        id: Date.now(),
        type: 'info',
        message: `Received: ${data.type || 'message'}`,
        timestamp: new Date()
      }]);
    }
  };

  const handleSSEError = (error) => {
    console.error('SSE Error:', error);
    setNotifications(prev => [...prev, {
      id: Date.now(),
      type: 'error',
      message: 'Connection error occurred',
      timestamp: new Date()
    }]);
  };

  const { isConnected, error, reconnectAttempts } = useSSE(
    'http://localhost:8000/api/v1/auth/sse/notifications/',
    accessToken,
    {
      onMessage: handleSSEMessage,
      onError: handleSSEError,
      reconnectDelay: 3000,
      maxReconnectAttempts: 5
    }
  );

  // Remove old notifications
  useEffect(() => {
    const cleanup = setInterval(() => {
      setNotifications(prev => 
        prev.filter(notif => Date.now() - notif.timestamp.getTime() < 30000)
      );
    }, 5000);

    return () => clearInterval(cleanup);
  }, []);

  return (
    <>
      {children}
      
      {/* SSE Status Indicator (optional) */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{
          position: 'fixed',
          top: 10,
          right: 10,
          padding: '8px 12px',
          backgroundColor: isConnected ? '#4CAF50' : '#f44336',
          color: 'white',
          borderRadius: '4px',
          fontSize: '12px',
          zIndex: 9999
        }}>
          SSE: {isConnected ? 'Connected' : 'Disconnected'}
          {error && ` (${error})`}
          {reconnectAttempts > 0 && ` - Reconnecting... (${reconnectAttempts})`}
        </div>
      )}

      {/* Notifications Display */}
      <div style={{
        position: 'fixed',
        top: 60,
        right: 10,
        width: '300px',
        zIndex: 9998
      }}>
        {notifications.map(notif => (
          <div
            key={notif.id}
            style={{
              padding: '12px',
              marginBottom: '8px',
              backgroundColor: notif.type === 'error' ? '#f44336' : 
                             notif.type === 'warning' ? '#ff9800' : '#2196F3',
              color: 'white',
              borderRadius: '4px',
              fontSize: '14px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}
          >
            {notif.message}
            <div style={{ fontSize: '11px', opacity: 0.8, marginTop: '4px' }}>
              {notif.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
    </>
  );
};

/**
 * Example usage in your main App component
 */
const App = () => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));

  const login = async (email, password) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access);
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        
        // Fetch user profile
        const userResponse = await fetch('http://localhost:8000/api/v1/auth/user/', {
          headers: {
            'Authorization': `Bearer ${data.access}`,
          },
        });
        
        if (userResponse.ok) {
          const userData = await userResponse.json();
          setUser(userData);
        }
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    setAccessToken(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    // Redirect to login page
    window.location.href = '/login';
  };

  const authContextValue = {
    user,
    accessToken,
    login,
    logout,
    isAuthenticated: !!user && !!accessToken
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      <div className="App">
        {authContextValue.isAuthenticated ? (
          <SSEManager>
            {/* Your main application content */}
            <div>
              <h1>Welcome, {user?.username}!</h1>
              <button onClick={logout}>Logout</button>
              {/* Rest of your app */}
            </div>
          </SSEManager>
        ) : (
          <LoginForm onLogin={login} />
        )}
      </div>
    </AuthContext.Provider>
  );
};

/**
 * Simple Login Form Component
 */
const LoginForm = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await onLogin(email, password);
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: '400px', margin: '0 auto', padding: '20px' }}>
      <h2>Login</h2>
      {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
      
      <div style={{ marginBottom: '15px' }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ width: '100%', padding: '10px', fontSize: '16px' }}
        />
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: '100%', padding: '10px', fontSize: '16px' }}
        />
      </div>
      
      <button
        type="submit"
        disabled={loading}
        style={{
          width: '100%',
          padding: '12px',
          fontSize: '16px',
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

// Alternative: Simple SSE test component for debugging
const SSETestComponent = () => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Test the simple SSE endpoint without authentication
    const eventSource = new EventSource('http://localhost:8000/api/v1/auth/sse/test/');

    eventSource.onopen = () => {
      setIsConnected(true);
      console.log('Test SSE connection opened');
    };

    eventSource.onmessage = (event) => {
      console.log('Test SSE message:', event.data);
      setMessages(prev => [...prev, {
        id: Date.now(),
        data: event.data,
        timestamp: new Date()
      }]);
    };

    eventSource.onerror = (error) => {
      console.error('Test SSE error:', error);
      setIsConnected(false);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div style={{ padding: '20px' }}>
      <h3>SSE Test Component</h3>
      <p>Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      <div>
        <h4>Messages:</h4>
        {messages.map(msg => (
          <div key={msg.id} style={{ padding: '5px', border: '1px solid #ccc', margin: '5px 0' }}>
            <strong>{msg.timestamp.toLocaleTimeString()}:</strong> {msg.data}
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;
export { SSEManager, useSSE, SSETestComponent };
