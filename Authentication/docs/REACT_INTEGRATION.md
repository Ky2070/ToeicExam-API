# React.js Integration Guide for Single-Device Authentication

This guide explains how to integrate the single-device authentication system with your React application.

## Installation

```bash
# If using npm
npm install eventsource

# If using yarn
yarn add eventsource
```

## Implementation

### 1. Authentication Context

```tsx
// src/contexts/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { AuthEventManager } from '../services/AuthEventManager';

interface AuthContextType {
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [authEvents, setAuthEvents] = useState<AuthEventManager | null>(null);

  useEffect(() => {
    // Initialize AuthEventManager
    const eventManager = new AuthEventManager(process.env.REACT_APP_API_URL || '');
    setAuthEvents(eventManager);

    return () => {
      eventManager.disconnect();
    };
  }, []);

  useEffect(() => {
    if (authEvents && accessToken) {
      authEvents.connect(accessToken);
    }
  }, [authEvents, accessToken]);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/v1/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      setAccessToken(data.access);
      setRefreshToken(data.refresh);
      setIsAuthenticated(true);

      // Store tokens
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    setAccessToken(null);
    setRefreshToken(null);
    setIsAuthenticated(false);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    authEvents?.disconnect();
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, accessToken, refreshToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 2. Auth Event Manager Service

```tsx
// src/services/AuthEventManager.ts
export class AuthEventManager {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private onForceLogoutCallback: (() => void) | null = null;

  constructor(private readonly baseUrl: string) {}

  public connect(accessToken: string): void {
    if (this.eventSource) {
      this.disconnect();
    }

    const url = new URL(`${this.baseUrl}/api/v1/auth/sse/notifications/`);
    
    this.eventSource = new EventSource(url.toString(), {
      withCredentials: true,
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });

    this.setupEventListeners();
  }

  public disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
  }

  public onForceLogout(callback: () => void): void {
    this.onForceLogoutCallback = callback;
  }

  private setupEventListeners(): void {
    if (!this.eventSource) return;

    this.eventSource.onopen = () => {
      console.log('SSE connection established');
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
    };

    this.eventSource.addEventListener('FORCE_LOGOUT', (event) => {
      const data = JSON.parse(event.data);
      console.log('Force logout received:', data.message);
      
      if (this.onForceLogoutCallback) {
        this.onForceLogoutCallback();
      }
    });

    this.eventSource.addEventListener('heartbeat', () => {
      console.debug('Heartbeat received');
    });

    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      this.eventSource?.close();

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        setTimeout(() => {
          this.reconnectAttempts++;
          this.reconnectDelay *= 2; // Exponential backoff
          // Attempt to reconnect using the stored access token
          const token = localStorage.getItem('access_token');
          if (token) {
            this.connect(token);
          }
        }, this.reconnectDelay);
      }
    };
  }
}
```

### 3. Protected Route Component

```tsx
// src/components/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};
```

### 4. Login Component Example

```tsx
// src/components/Login.tsx
import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err) {
      setError('Login failed. Please check your credentials.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <div>
        <label>Email:</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      <button type="submit">Login</button>
    </form>
  );
};
```

### 5. App Setup

```tsx
// src/App.tsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
```

## Usage Examples

### 1. Using the Auth Context

```tsx
const MyComponent: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div>
      {isAuthenticated ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <Link to="/login">Login</Link>
      )}
    </div>
  );
};
```

### 2. Handling Force Logout

```tsx
const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const authEvents = new AuthEventManager(process.env.REACT_APP_API_URL || '');
    
    authEvents.onForceLogout(() => {
      logout();
      navigate('/login', { 
        state: { message: 'Your session was ended due to login from another device.' }
      });
    });

    return () => authEvents.disconnect();
  }, [logout, navigate]);

  return <div>Dashboard Content</div>;
};
```

## Environment Setup

Create a `.env` file in your React project root:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Error Handling

The system includes built-in handling for:
- Network errors
- Authentication failures
- Token expiration
- Force logout events
- Connection interruptions

## Security Considerations

1. **Token Storage**:
   - Access tokens are stored in memory (state)
   - Refresh tokens in localStorage (consider secure cookies for production)

2. **CORS**:
   - Ensure your Django backend has proper CORS settings
   - Use credentials mode for SSE connections

3. **SSL**:
   - Always use HTTPS in production
   - Update SSE connection URL accordingly

4. **Token Refresh**:
   - Implement automatic token refresh before expiration
   - Handle refresh token rotation if enabled

## Testing

See the TEST_CASES.md document for detailed testing scenarios and examples.
