# Contributing to CINEIQ

Thank you for your interest in contributing to CINEIQ! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### Setup Development Environment

1. **Fork and clone:**
```bash
git clone https://github.com/YOUR_USERNAME/cineiq.git
cd cineiq
```

2. **Install dependencies:**
```bash
# Backend
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Testing tools

# Frontend
cd ../frontend
npm install
```

3. **Set up environment:**
```bash
cp .env.example .env
# Fill in your API keys
```

4. **Run setup:**
```bash
make setup
```

## Development Workflow

### Branch Naming
- Feature: `feature/your-feature-name`
- Bug fix: `fix/bug-description`
- Documentation: `docs/what-you-changed`
- Refactor: `refactor/what-you-refactored`

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add semantic search filtering by year
fix: resolve WebSocket connection timeout
docs: update deployment guide
refactor: optimize recommendation algorithm
test: add unit tests for rating submission
```

### Pull Request Process

1. **Create a branch:**
```bash
git checkout -b feature/your-feature
```

2. **Make your changes:**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Test your changes:**
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Linting
make lint
```

4. **Commit and push:**
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature
```

5. **Create Pull Request:**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Include screenshots for UI changes

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use `ruff` for linting
- Use `mypy` for type checking

```python
async def get_recommendations(
    user_id: str,
    limit: int = 20,
    exclude_watched: bool = True
) -> List[Recommendation]:
    """
    Get personalized movie recommendations.
    
    Args:
        user_id: User identifier
        limit: Maximum number of recommendations
        exclude_watched: Filter out already watched movies
        
    Returns:
        List of movie recommendations with explanations
    """
    # Implementation
```

### TypeScript (Frontend)
- Use TypeScript strict mode
- Follow Airbnb style guide
- Use functional components with hooks
- Maximum line length: 100 characters

```typescript
interface MovieCardProps {
  movie: Movie
  onRate: (rating: number) => void
}

export const MovieCard: React.FC<MovieCardProps> = ({ movie, onRate }) => {
  // Implementation
}
```

### CSS/Styling
- Use Tailwind CSS utility classes
- Follow the design system in `globals.css`
- Use CSS variables for colors
- Mobile-first responsive design

## Testing Guidelines

### Backend Tests
```python
# tests/test_recommendations.py
import pytest
from app.services.recommendation import RecommendationService

@pytest.mark.asyncio
async def test_get_recommendations():
    service = RecommendationService()
    recommendations = await service.get_recommendations(
        user_id="test_user",
        limit=10
    )
    assert len(recommendations) <= 10
    assert all(r.predicted_rating > 0 for r in recommendations)
```

### Frontend Tests
```typescript
// __tests__/MovieCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { MovieCard } from '@/components/MovieCard'

describe('MovieCard', () => {
  it('renders movie title', () => {
    render(<MovieCard movie={mockMovie} onRate={jest.fn()} />)
    expect(screen.getByText('Inception')).toBeInTheDocument()
  })
})
```

## Documentation

### Code Documentation
- Add docstrings to all functions/classes
- Include type hints
- Explain complex algorithms
- Document API endpoints

### README Updates
- Update README.md for new features
- Add examples for new functionality
- Update installation instructions if needed

## Feature Requests

1. Check existing issues first
2. Create a new issue with:
   - Clear description
   - Use case
   - Expected behavior
   - Mockups (if UI change)

## Bug Reports

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots/logs
- Environment (OS, browser, versions)

## Performance Considerations

- Optimize database queries (use indexes)
- Cache expensive operations
- Use async/await for I/O operations
- Minimize bundle size (code splitting)
- Lazy load components

## Security

- Never commit secrets or API keys
- Validate all user inputs
- Use parameterized queries
- Sanitize data before rendering
- Report security issues privately

## ML Model Contributions

### Training New Models
1. Document the model architecture
2. Include training scripts
3. Provide evaluation metrics
4. Compare with existing models
5. Include model card (dataset, performance, limitations)

### Model Evaluation
- RMSE < 0.86 for collaborative filtering
- Precision@10 > 0.75
- Test on hold-out set
- Document any biases

## Questions?

- Open a GitHub Discussion
- Join our Slack channel
- Email: dev@cineiq.com

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in the about page

Thank you for contributing to CINEIQ! 🎬✨
