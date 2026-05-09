# CINEIQ API Documentation

Base URL: `http://localhost:8000` (development) | `https://api.cineiq.com` (production)

## Authentication

All endpoints require authentication via Clerk JWT token (except health check).

```bash
Authorization: Bearer <jwt_token>
```

## Endpoints

### Health Check

#### GET `/api/v1/health`

Check API health and dependencies status.

**Response:**
```json
{
  "status": "healthy",
  "service": "cineiq-backend",
  "dependencies": {
    "redis": "ok",
    "qdrant": "ok",
    "postgres": "ok"
  }
}
```

---

### Movies

#### GET `/api/v1/movies/trending`

Get trending movies from TMDB.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "movies": [
    {
      "id": 27205,
      "title": "Inception",
      "poster_url": "https://image.tmdb.org/...",
      "backdrop_url": "https://image.tmdb.org/...",
      "vote_average": 8.4,
      "release_date": "2010-07-16"
    }
  ],
  "total": 20
}
```

#### GET `/api/v1/movies/{tmdb_id}`

Get detailed movie information.

**Parameters:**
- `tmdb_id` (path): TMDB movie ID

**Response:**
```json
{
  "tmdb_id": 27205,
  "title": "Inception",
  "overview": "A thief who steals corporate secrets...",
  "release_date": "2010-07-16",
  "runtime": 148,
  "genres": ["Action", "Science Fiction", "Adventure"],
  "director": "Christopher Nolan",
  "cast": [
    {
      "name": "Leonardo DiCaprio",
      "character": "Cobb",
      "profile_path": "/..."
    }
  ],
  "vote_average": 8.4,
  "vote_count": 32000,
  "poster_url": "https://...",
  "backdrop_url": "https://...",
  "tagline": "Your mind is the scene of the crime"
}
```

#### GET `/api/v1/movies/search`

Search movies by title.

**Query Parameters:**
- `query` (required): Search query

**Response:**
```json
{
  "query": "inception",
  "results": [...],
  "total": 5
}
```

---

### Search

#### POST `/api/v1/search/semantic`

Semantic search using natural language queries.

**Request Body:**
```json
{
  "query": "dark psychological thriller with twist ending",
  "limit": 20,
  "genres": ["Thriller", "Mystery"],
  "min_year": 2000,
  "max_year": 2024
}
```

**Response:**
```json
{
  "query": "dark psychological thriller with twist ending",
  "results": [
    {
      "tmdb_id": 680,
      "title": "Pulp Fiction",
      "overview": "...",
      "genres": ["Thriller", "Crime"],
      "year": "1994",
      "rating": 8.5,
      "similarity_score": 0.92,
      "match_reason": "Semantic similarity: 92%"
    }
  ],
  "total": 15
}
```

#### GET `/api/v1/search/vibe`

Quick vibe-based search with presets.

**Query Parameters:**
- `vibe` (required): Vibe preset (mind-bending, feel-good, dark-atmospheric, etc.)
- `limit` (optional): Max results (default: 20)

**Response:** Same as semantic search

---

### Recommendations

#### POST `/api/v1/recommend`

Get personalized movie recommendations.

**Request Body:**
```json
{
  "limit": 20,
  "exclude_watched": true,
  "genres_filter": ["Action", "Sci-Fi"]
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "tmdb_id": 27205,
      "title": "Inception",
      "predicted_rating": 4.7,
      "confidence": 0.91,
      "explanation": {
        "top_factors": [
          "Similar to Interstellar (CF)",
          "High sci-fi affinity (0.87)",
          "Director Christopher Nolan match"
        ],
        "counterfactual": "If you had rated Tenet lower, this score would drop to 3.9",
        "contributing_models": {
          "svd": 0.45,
          "ncf": 0.35,
          "content": 0.20
        }
      },
      "poster_url": "https://...",
      "genres": ["Action", "Sci-Fi", "Thriller"]
    }
  ],
  "total": 20,
  "user_ratings_count": 150,
  "algorithm": "hybrid_svd"
}
```

#### GET `/api/v1/similar/{tmdb_id}`

Get movies similar to a given movie.

**Parameters:**
- `tmdb_id` (path): Movie ID
- `limit` (query, optional): Max results (default: 20)

**Response:**
```json
{
  "query_movie_id": 27205,
  "similar_movies": [
    {
      "tmdb_id": 157336,
      "title": "Interstellar",
      "overview": "...",
      "genres": ["Adventure", "Drama", "Science Fiction"],
      "similarity_score": 0.94,
      "match_reason": "Content similarity: 94%"
    }
  ],
  "total": 20
}
```

---

### Users

#### POST `/api/v1/users/ratings`

Submit or update a movie rating.

**Request Body:**
```json
{
  "tmdb_id": 27205,
  "rating": 4.5,
  "watched_at": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Rating submitted",
  "tmdb_id": 27205,
  "rating": 4.5
}
```

#### GET `/api/v1/users/ratings`

Get user's rating history.

**Query Parameters:**
- `limit` (optional): Max results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "ratings": [
    {
      "tmdb_id": 27205,
      "rating": 4.5,
      "watched_at": "2024-01-15T10:30:00Z",
      "title": "Inception",
      "poster_url": "https://...",
      "release_date": "2010-07-16",
      "genres": ["Action", "Sci-Fi"]
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 3
}
```

#### GET `/api/v1/users/profile`

Get user taste profile with genre affinities.

**Response:**
```json
{
  "user_id": "user_123",
  "email": "user@example.com",
  "display_name": "John Doe",
  "total_ratings": 150,
  "average_rating": 3.8,
  "top_genres": [
    {
      "genre": "Science Fiction",
      "average_rating": 4.2,
      "count": 45,
      "affinity": 0.84
    }
  ],
  "rating_distribution": {
    "5.0": 30,
    "4.5": 25,
    "4.0": 40,
    "3.5": 20,
    "3.0": 15,
    "2.5": 10,
    "2.0": 5,
    "1.5": 3,
    "1.0": 2,
    "0.5": 0
  },
  "taste_vector": [0.84, 0.72, 0.65, ...]
}
```

#### DELETE `/api/v1/users/ratings/{tmdb_id}`

Delete a rating.

**Parameters:**
- `tmdb_id` (path): Movie ID

**Response:**
```json
{
  "success": true,
  "message": "Rating deleted",
  "tmdb_id": 27205
}
```

---

### Watch Together

#### POST `/api/v1/rooms/create`

Create a watch-together room.

**Request Body:**
```json
{
  "tmdb_id": 27205,
  "max_participants": 10
}
```

**Response:**
```json
{
  "room_id": "550e8400-e29b-41d4-a716-446655440000",
  "join_url": "/watch/550e8400-e29b-41d4-a716-446655440000",
  "ws_url": "ws://localhost:8000/api/v1/ws/room/550e8400-e29b-41d4-a716-446655440000",
  "movie": {
    "tmdb_id": 27205,
    "title": "Inception",
    "poster_url": "https://..."
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET `/api/v1/rooms/{room_id}`

Get room information and participants.

**Response:**
```json
{
  "room_id": "550e8400-e29b-41d4-a716-446655440000",
  "movie": {
    "tmdb_id": 27205,
    "title": "Inception",
    "poster_url": "https://...",
    "backdrop_url": "https://..."
  },
  "host_user_id": "user_123",
  "participants": [
    {
      "user_id": "user_123",
      "display_name": "John Doe",
      "joined_at": "2024-01-15T10:30:00Z"
    }
  ],
  "live_participants": [
    {
      "user_id": "user_123",
      "display_name": "John Doe"
    }
  ],
  "max_participants": 10,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### WS `/api/v1/ws/room/{room_id}`

WebSocket endpoint for real-time room communication.

**Query Parameters:**
- `user_id`: User identifier
- `display_name`: Display name

**Message Types:**

**Playback Control:**
```json
{
  "type": "playback",
  "action": "play",  // or "pause", "seek"
  "time": 120
}
```

**Chat Message:**
```json
{
  "type": "chat",
  "text": "Great movie!"
}
```

**Reaction:**
```json
{
  "type": "reaction",
  "emoji": "❤️"
}
```

**Received Events:**
```json
{
  "type": "playback_sync",
  "action": "play",
  "time": 120,
  "state": "playing",
  "user_id": "user_123",
  "display_name": "John Doe",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Imports

#### POST `/api/v1/import/letterboxd`

Import ratings from Letterboxd CSV export.

**Request:** `multipart/form-data`
- `file`: CSV file

**Response:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_items": 500,
  "imported": 485,
  "failed": 15,
  "message": "Successfully imported 485 out of 500 ratings"
}
```

#### GET `/api/v1/import/jobs`

Get import job history.

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "source": "letterboxd",
      "status": "completed",
      "total_items": 500,
      "processed_items": 485,
      "error_message": null,
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:35:00Z"
    }
  ]
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable

---

## Rate Limiting

- **Default**: 100 requests/minute per user
- **Headers**:
  - `X-RateLimit-Limit`: Rate limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

---

## Pagination

Endpoints that return lists support pagination:

**Query Parameters:**
- `limit`: Max items per page (default: 20, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response includes:**
```json
{
  "results": [...],
  "total": 500,
  "page": 1,
  "pages": 25
}
```

---

## Interactive API Docs

Visit `/docs` for interactive Swagger UI documentation.

---

## SDKs & Examples

### Python
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/search/semantic",
        json={"query": "dark thriller", "limit": 10},
        headers={"Authorization": f"Bearer {token}"}
    )
    results = response.json()
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/v1/recommend', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ limit: 20, exclude_watched: true })
});
const data = await response.json();
```

---

## Support

- API Issues: https://github.com/RamK2006/issues

