# Test Cases for Single-Device Authentication System

## Backend Tests (Django)

### Unit Tests

```python
# Authentication/tests/test_authentication.py

class SingleDeviceAuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse("token_obtain")
        self.refresh_url = reverse("token_refresh")
        self.user_profile_url = reverse("user_profile")
        
        # Create test user
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_successful_login(self):
        """Test successful login returns valid tokens"""
        response = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_multiple_device_login(self):
        """Test login behavior across multiple devices"""
        # First device login
        response1 = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )
        token1 = response1.data["access"]
        
        # Second device login
        response2 = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )
        token2 = response2.data["access"]
        
        # First device token should be invalid
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Second device token should work
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token_behavior(self):
        """Test refresh token functionality"""
        # Initial login
        response = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )
        refresh_token = response.data["refresh"]
        
        # Refresh token should work
        response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_concurrent_refresh_requests(self):
        """Test handling of concurrent refresh token requests"""
        # Initial login
        response = self.client.post(
            self.login_url,
            {"email": self.user_data["email"], "password": self.user_data["password"]},
        )
        refresh_token = response.data["refresh"]
        
        # Multiple refresh requests
        response1 = self.client.post(
            self.refresh_url, {"refresh": refresh_token}
        )
        response2 = self.client.post(
            self.refresh_url, {"refresh": refresh_token}
        )
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Both tokens should be valid
        token1 = response1.data["access"]
        token2 = response2.data["access"]
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")
        response = self.client.get(self.user_profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Frontend Tests (React)

### Unit Tests

```typescript
// src/services/__tests__/AuthEventManager.test.ts
import { AuthEventManager } from '../AuthEventManager';

describe('AuthEventManager', () => {
    let authManager: AuthEventManager;
    let mockEventSource: any;

    beforeEach(() => {
        // Mock EventSource
        mockEventSource = {
            close: jest.fn(),
            addEventListener: jest.fn(),
            removeEventListener: jest.fn(),
        };
        (global as any).EventSource = jest.fn(() => mockEventSource);
        
        authManager = new AuthEventManager('http://localhost:8000');
    });

    test('connects successfully', () => {
        authManager.connect('test-token');
        expect(EventSource).toHaveBeenCalled();
    });

    test('handles force logout event', () => {
        const mockCallback = jest.fn();
        authManager.onForceLogout(mockCallback);
        
        // Simulate force logout event
        const event = new MessageEvent('FORCE_LOGOUT', {
            data: JSON.stringify({ message: 'Logged out' })
        });
        
        mockEventSource.addEventListener.mock.calls[0][1](event);
        expect(mockCallback).toHaveBeenCalled();
    });

    test('disconnects properly', () => {
        authManager.connect('test-token');
        authManager.disconnect();
        expect(mockEventSource.close).toHaveBeenCalled();
    });
});

// src/contexts/__tests__/AuthContext.test.tsx
import { render, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../AuthContext';

describe('AuthContext', () => {
    test('provides authentication state', () => {
        const TestComponent = () => {
            const { isAuthenticated } = useAuth();
            return <div>{isAuthenticated ? 'Authenticated' : 'Not authenticated'}</div>;
        };

        const { getByText } = render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        expect(getByText('Not authenticated')).toBeInTheDocument();
    });

    test('handles login successfully', async () => {
        const TestComponent = () => {
            const { login, isAuthenticated } = useAuth();
            
            const handleLogin = async () => {
                await login('test@example.com', 'password');
            };

            return (
                <div>
                    <button onClick={handleLogin}>Login</button>
                    <div>{isAuthenticated ? 'Authenticated' : 'Not authenticated'}</div>
                </div>
            );
        };

        const { getByText } = render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        await act(async () => {
            getByText('Login').click();
        });

        expect(getByText('Authenticated')).toBeInTheDocument();
    });
});
```

### Integration Tests

```typescript
// src/tests/integration/Authentication.test.tsx
import { render, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '../../contexts/AuthContext';
import { Login } from '../../components/Login';
import { Dashboard } from '../../components/Dashboard';

describe('Authentication Flow', () => {
    test('full login flow', async () => {
        const { getByLabelText, getByText } = render(
            <AuthProvider>
                <Login />
            </AuthProvider>
        );

        // Fill in login form
        fireEvent.change(getByLabelText('Email:'), {
            target: { value: 'test@example.com' }
        });
        fireEvent.change(getByLabelText('Password:'), {
            target: { value: 'password123' }
        });

        // Submit form
        fireEvent.click(getByText('Login'));

        // Wait for navigation
        await waitFor(() => {
            expect(window.location.pathname).toBe('/dashboard');
        });
    });

    test('force logout scenario', async () => {
        const { getByText } = render(
            <AuthProvider>
                <Dashboard />
            </AuthProvider>
        );

        // Simulate SSE force logout event
        const event = new MessageEvent('FORCE_LOGOUT', {
            data: JSON.stringify({ message: 'Logged out from another device' })
        });
        window.dispatchEvent(event);

        // Verify redirect to login
        await waitFor(() => {
            expect(window.location.pathname).toBe('/login');
            expect(getByText('Your session was ended')).toBeInTheDocument();
        });
    });
});
```

## End-to-End Tests (Cypress)

```typescript
// cypress/integration/authentication.spec.ts
describe('Authentication System', () => {
    beforeEach(() => {
        cy.visit('/login');
    });

    it('handles single device enforcement', () => {
        // Login on first device
        cy.login('test@example.com', 'password123');
        cy.url().should('include', '/dashboard');

        // Open new browser (simulating second device)
        cy.login('test@example.com', 'password123', { newBrowser: true });

        // Check first device is logged out
        cy.get('.logout-message')
            .should('contain', 'Your account was logged in from another device');
        cy.url().should('include', '/login');
    });

    it('maintains session with valid refresh token', () => {
        cy.login('test@example.com', 'password123');
        
        // Wait for access token to expire
        cy.wait(5000); // Adjust based on token lifetime
        
        // Verify auto-refresh maintains session
        cy.get('.dashboard')
            .should('exist');
    });

    it('handles network interruptions', () => {
        cy.login('test@example.com', 'password123');
        
        // Simulate network disconnect
        cy.disconnectNetwork();
        
        // Verify reconnection attempt
        cy.get('.connection-status')
            .should('contain', 'Reconnecting');
            
        // Restore network
        cy.connectNetwork();
        
        // Verify reconnection
        cy.get('.connection-status')
            .should('contain', 'Connected');
    });
});
```

## Manual Testing Checklist

### Basic Authentication
- [ ] User can register successfully
- [ ] User can login successfully
- [ ] User can logout successfully
- [ ] Access token works for protected routes
- [ ] Invalid credentials are properly handled

### Single Device Enforcement
- [ ] Login from new device invalidates old device's session
- [ ] Old device receives force logout notification
- [ ] Old device is redirected to login page
- [ ] Old device shows appropriate message
- [ ] New device maintains active session

### Token Management
- [ ] Access tokens expire as configured
- [ ] Refresh tokens work correctly
- [ ] Invalid tokens are rejected
- [ ] Token refresh maintains session
- [ ] Token rotation works if enabled

### SSE Connection
- [ ] SSE connection established on login
- [ ] Heartbeat messages received
- [ ] Connection recovers from network interruptions
- [ ] Connection closes on logout
- [ ] Force logout events received and handled

### Error Handling
- [ ] Network errors handled gracefully
- [ ] Invalid tokens show appropriate errors
- [ ] Server errors show user-friendly messages
- [ ] Connection retries work as expected
- [ ] Rate limiting handled appropriately

### Security
- [ ] Tokens stored securely
- [ ] CSRF protection works
- [ ] XSS protection in place
- [ ] No sensitive data in logs
- [ ] CORS properly configured

## Performance Testing

### Load Tests
```python
# tests/performance/test_load.py
from locust import HttpUser, task, between

class AuthenticationUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.login()
    
    @task
    def access_protected_route(self):
        self.client.get("/api/v1/auth/user/", 
            headers={"Authorization": f"Bearer {self.access_token}"})
    
    @task
    def refresh_token(self):
        response = self.client.post("/api/v1/auth/refresh/",
            json={"refresh": self.refresh_token})
        self.access_token = response.json()["access"]
```

### Stress Tests
- Concurrent login attempts
- Multiple refresh token requests
- SSE connection limits
- Redis connection pool limits

## Security Testing

### OWASP Top 10 Checks
- [ ] Injection vulnerabilities
- [ ] Broken authentication
- [ ] Sensitive data exposure
- [ ] XML external entities
- [ ] Broken access control
- [ ] Security misconfiguration
- [ ] Cross-site scripting
- [ ] Insecure deserialization
- [ ] Using components with known vulnerabilities
- [ ] Insufficient logging and monitoring

### Token Security
- [ ] Token encryption
- [ ] Token signing
- [ ] Token expiration
- [ ] Token storage
- [ ] Token transmission
