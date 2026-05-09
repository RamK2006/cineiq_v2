# CINEIQ Testing Guide

## 🧪 Testing Strategy

CINEIQ uses a comprehensive testing approach covering unit tests, integration tests, and end-to-end tests.

## Backend Testing

### Setup

```bash
cd backend
pip install pytest pytest-asyncio pytest-cov httpx
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_recommendations.py

# Run with verbose output
pytest -v
```

### Test Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── test_api/
│   ├── test_movies.py       # Movie endpoints
│   ├── test_search.py       # Search endpoints
│   ├── test_recommendations.py
│   ├── test_users.py
│   └── test_watch_together.py
├── test_services/
│   ├── test_tmdb_client.py
│   ├── test_embedding.py
│   └── test_recommendation.py
└── test_ml/
    ├── test_svd_model.py
    └── test_ncf_model.py
```

### Example Test: Recommendations

```python
# backend/tests/test_api/test_recommendations.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_recommendations():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/recommend",
            json={"limit": 10, "exclude_watched": True},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) <= 10
        
        # Check recommendation structure
        rec = data["recommendations"][0]
        assert "tmdb_id" in rec
        assert "title" in rec
        assert "predicted_rating" in rec
        assert "explanation" in rec

@pytest.mark.asyncio
async def test_similar_movies():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/similar/27205",  # Inception
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "similar_movies" in data
        assert len(data["similar_movies"]) > 0
```

### Example Test: ML Models

```python
# backend/tests/test_ml/test_svd_model.py
import pytest
import pickle
from app.core.config import settings

def test_svd_model_loads():
    """Test that SVD model can be loaded"""
    with open(settings.SVD_MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    assert model is not None
    assert hasattr(model, 'predict')

def test_svd_prediction():
    """Test SVD prediction"""
    with open(settings.SVD_MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    # Test prediction
    prediction = model.predict(uid="user123", iid=27205)
    
    assert prediction.est >= 0.5
    assert prediction.est <= 5.0
```

### Mocking External Services

```python
# backend/tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_tmdb_client():
    """Mock TMDB API client"""
    with patch('app.services.tmdb_client.TMDBClient') as mock:
        mock_instance = mock.return_value
        mock_instance.get_movie = AsyncMock(return_value={
            "id": 27205,
            "title": "Inception",
            "overview": "Test overview",
            "genres": [{"name": "Sci-Fi"}]
        })
        yield mock_instance

@pytest.fixture
def mock_qdrant():
    """Mock Qdrant client"""
    with patch('qdrant_client.QdrantClient') as mock:
        mock_instance = mock.return_value
        mock_instance.search = AsyncMock(return_value=[])
        yield mock_instance
```

## Frontend Testing

### Setup

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom jest
```

### Run Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Example Test: Movie Card Component

```typescript
// frontend/app/components/__tests__/MovieCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import MovieCard from '../MovieCard'

describe('MovieCard', () => {
  const mockMovie = {
    tmdb_id: 27205,
    title: 'Inception',
    poster_url: 'https://...',
    vote_average: 8.8,
    genres: ['Sci-Fi', 'Thriller']
  }

  it('renders movie information', () => {
    render(<MovieCard movie={mockMovie} />)
    
    expect(screen.getByText('Inception')).toBeInTheDocument()
    expect(screen.getByText('8.8')).toBeInTheDocument()
  })

  it('handles click event', () => {
    const handleClick = jest.fn()
    render(<MovieCard movie={mockMovie} onClick={handleClick} />)
    
    fireEvent.click(screen.getByText('Inception'))
    expect(handleClick).toHaveBeenCalledWith(27205)
  })
})
```

## Integration Testing

### Database Integration Tests

```python
# backend/tests/test_integration/test_database.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, User, Rating
import uuid

@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine(
        "postgresql+asyncpg://test:test@localhost:5432/test_cineiq",
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    yield async_session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_create_user_and_rating(test_db):
    """Test creating user and rating"""
    async with test_db() as session:
        # Create user
        user = User(
            id=uuid.uuid4(),
            clerk_id="test_user",
            email="test@example.com",
            display_name="Test User"
        )
        session.add(user)
        await session.flush()
        
        # Create rating
        rating = Rating(
            id=uuid.uuid4(),
            user_id=user.id,
            tmdb_id=27205,
            rating=4.5
        )
        session.add(rating)
        await session.commit()
        
        # Verify
        assert user.id is not None
        assert rating.id is not None
```

## End-to-End Testing

### Playwright Setup

```bash
cd frontend
npm install --save-dev @playwright/test
npx playwright install
```

### E2E Test Example

```typescript
// frontend/tests/e2e/movie-search.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Movie Search', () => {
  test('should search for movies', async ({ page }) => {
    await page.goto('http://localhost:3000/search')
    
    // Enter search query
    await page.fill('input[placeholder*="search"]', 'inception')
    await page.click('button:has-text("Search")')
    
    // Wait for results
    await page.waitForSelector('[data-testid="movie-card"]')
    
    // Verify results
    const results = await page.$$('[data-testid="movie-card"]')
    expect(results.length).toBeGreaterThan(0)
    
    // Check first result
    const firstResult = await page.textContent('[data-testid="movie-card"]:first-child')
    expect(firstResult).toContain('Inception')
  })

  test('should navigate to movie detail', async ({ page }) => {
    await page.goto('http://localhost:3000/search')
    
    await page.fill('input[placeholder*="search"]', 'inception')
    await page.click('button:has-text("Search")')
    
    await page.waitForSelector('[data-testid="movie-card"]')
    await page.click('[data-testid="movie-card"]:first-child')
    
    // Verify navigation
    await expect(page).toHaveURL(/\/movies\/\d+/)
    await expect(page.locator('h1')).toContainText('Inception')
  })
})
```

## Performance Testing

### Load Testing with Locust

```python
# backend/tests/load/locustfile.py
from locust import HttpUser, task, between

class CINEIQUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get token"""
        self.token = "test_token"
    
    @task(3)
    def get_trending(self):
        """Get trending movies"""
        self.client.get(
            "/api/v1/movies/trending",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def search_movies(self):
        """Search movies"""
        self.client.post(
            "/api/v1/search/semantic",
            json={"query": "action thriller", "limit": 20},
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def get_recommendations(self):
        """Get recommendations"""
        self.client.post(
            "/api/v1/recommend",
            json={"limit": 20},
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**Run Load Test:**
```bash
locust -f backend/tests/load/locustfile.py --host=http://localhost:8000
```

## ML Model Testing

### Model Accuracy Tests

```python
# backend/tests/test_ml/test_model_accuracy.py
import pytest
import pickle
import pandas as pd
from surprise import accuracy

def test_svd_accuracy():
    """Test SVD model accuracy on test set"""
    # Load model
    with open('backend/app/ml/models/svd_v1.pkl', 'rb') as f:
        model = pickle.load(f)
    
    # Load test data
    test_data = pd.read_csv('data/ml-25m/test_ratings.csv')
    
    # Make predictions
    predictions = []
    for _, row in test_data.iterrows():
        pred = model.predict(row['userId'], row['movieId'])
        predictions.append(pred)
    
    # Calculate RMSE
    rmse = accuracy.rmse(predictions, verbose=False)
    
    # Assert accuracy target
    assert rmse < 0.90, f"RMSE {rmse} exceeds target of 0.90"
```

## WebSocket Testing

```python
# backend/tests/test_websocket.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_connection():
    """Test WebSocket connection"""
    client = TestClient(app)
    
    with client.websocket_connect(
        "/api/v1/ws/room/test-room?user_id=test&display_name=Test"
    ) as websocket:
        # Receive room state
        data = websocket.receive_json()
        assert data["type"] == "room_state"
        
        # Send playback event
        websocket.send_json({
            "type": "playback",
            "action": "play",
            "time": 120
        })
        
        # Should receive broadcast
        data = websocket.receive_json()
        assert data["type"] == "playback_sync"
```

## CI/CD Testing

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
```

## Test Coverage Goals

- **Backend:** ≥ 85% code coverage
- **Frontend:** ≥ 80% code coverage
- **Critical paths:** 100% coverage
  - Authentication
  - Payment processing (if applicable)
  - Data persistence
  - ML model inference

## Manual Testing Checklist

### Functional Testing

- [ ] User can sign up and log in
- [ ] User can search for movies
- [ ] User can rate movies
- [ ] User can get personalized recommendations
- [ ] User can create watch-together room
- [ ] WebSocket sync works correctly
- [ ] Letterboxd import works
- [ ] All API endpoints return correct data

### UI/UX Testing

- [ ] All animations are smooth (60fps)
- [ ] Responsive design works on mobile
- [ ] Dark theme is consistent
- [ ] Loading states are clear
- [ ] Error messages are helpful
- [ ] Forms validate correctly

### Performance Testing

- [ ] Page load time < 3s
- [ ] API response time < 500ms
- [ ] Search results appear < 1s
- [ ] Recommendations load < 2s
- [ ] WebSocket latency < 100ms

### Security Testing

- [ ] Authentication required for protected routes
- [ ] JWT tokens expire correctly
- [ ] SQL injection prevented
- [ ] XSS attacks prevented
- [ ] CORS configured correctly
- [ ] Rate limiting works

## Debugging Tips

### Backend Debugging

```python
# Add to main.py for detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Frontend Debugging

```typescript
// Add to components for debugging
useEffect(() => {
  console.log('Component state:', state)
}, [state])
```

### Database Debugging

```bash
# Connect to PostgreSQL
psql -h localhost -U cineiq -d cineiq

# Check tables
\dt

# Query data
SELECT * FROM users LIMIT 10;
```

## Continuous Monitoring

### Sentry Integration

```python
# backend/app/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0,
)
```

### Performance Monitoring

```python
# Add to critical endpoints
from prometheus_client import Histogram

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

@request_duration.time()
async def get_recommendations():
    # ... endpoint logic
    pass
```

## Test Data

### Sample Test Users

```json
{
  "test_user_1": {
    "email": "user1@test.com",
    "ratings": 150,
    "favorite_genres": ["Sci-Fi", "Thriller"]
  },
  "test_user_2": {
    "email": "user2@test.com",
    "ratings": 50,
    "favorite_genres": ["Comedy", "Romance"]
  }
}
```

### Sample Test Movies

```json
[
  {"tmdb_id": 27205, "title": "Inception"},
  {"tmdb_id": 157336, "title": "Interstellar"},
  {"tmdb_id": 155, "title": "The Dark Knight"}
]
```
