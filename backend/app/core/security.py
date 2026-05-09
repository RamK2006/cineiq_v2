from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import httpx
from typing import Dict, Any
from .config import settings

security = HTTPBearer()

# Cache for Clerk JWKS
_jwks_cache: Dict[str, Any] = {}


async def get_clerk_jwks() -> Dict[str, Any]:
    """Fetch Clerk JWKS for JWT verification"""
    if _jwks_cache:
        return _jwks_cache
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.clerk.dev/v1/jwks",
            headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
        )
        response.raise_for_status()
        jwks = response.json()
        _jwks_cache.update(jwks)
        return jwks


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """Verify Clerk JWT token"""
    token = credentials.credentials
    
    try:
        # Decode without verification first to get the header
        unverified_header = jwt.get_unverified_header(token)
        
        # Get JWKS
        jwks = await get_clerk_jwks()
        
        # Find the right key
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        
        return payload
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")


async def get_current_user(token_payload: Dict[str, Any] = Security(verify_token)) -> str:
    """Extract user ID from verified token"""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    return user_id
