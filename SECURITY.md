# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of CINEIQ seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Disclose Publicly

Please do not open a public GitHub issue for security vulnerabilities.

### 2. Report Privately

Send an email to: **security@cineiq.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-14 days
  - Medium: 14-30 days
  - Low: 30-90 days

### 4. Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide regular updates on our progress
- We will notify you when the vulnerability is fixed
- We will credit you in our security advisories (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

1. **Keep Dependencies Updated**
   ```bash
   npm audit fix
   pip install --upgrade -r requirements.txt
   ```

2. **Use Strong API Keys**
   - Never commit API keys to Git
   - Rotate keys regularly (quarterly)
   - Use environment variables

3. **Enable HTTPS**
   - Always use HTTPS in production
   - Enable HSTS headers
   - Use valid SSL certificates

4. **Database Security**
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access
   - Regular backups

5. **Rate Limiting**
   - Configure appropriate rate limits
   - Monitor for abuse
   - Use API keys for tracking

### For Developers

1. **Input Validation**
   - Validate all user inputs
   - Use Pydantic models
   - Sanitize data before rendering

2. **SQL Injection Prevention**
   - Use SQLAlchemy ORM
   - Never use raw SQL with user input
   - Use parameterized queries

3. **XSS Prevention**
   - React automatically escapes content
   - Be careful with `dangerouslySetInnerHTML`
   - Sanitize user-generated content

4. **Authentication**
   - Use Clerk for authentication
   - Validate JWT tokens
   - Implement proper session management

5. **Secrets Management**
   - Use environment variables
   - Never hardcode secrets
   - Use AWS Secrets Manager in production

## Known Security Considerations

### 1. API Keys in Frontend

The frontend uses `NEXT_PUBLIC_*` variables which are exposed to the client. These should only contain public keys (like Clerk publishable key).

### 2. Rate Limiting

Default rate limit is 100 requests/minute per user. Adjust based on your needs in `backend/app/core/config.py`.

### 3. CORS Configuration

CORS is configured to allow specific origins. Update `backend/app/main.py` for production domains.

### 4. Database Encryption

Sensitive data should be encrypted at rest. Consider using PostgreSQL's `pgcrypto` extension.

## Security Checklist for Deployment

- [ ] All API keys are in environment variables
- [ ] HTTPS is enabled
- [ ] Database uses strong passwords
- [ ] CORS is configured for production domains
- [ ] Rate limiting is enabled
- [ ] Logging is configured
- [ ] Monitoring is set up
- [ ] Backups are automated
- [ ] Security headers are configured
- [ ] Dependencies are up to date

## Security Headers

Add these headers in production (via nginx/ALB):

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;
```

## Vulnerability Disclosure

We will publish security advisories for all confirmed vulnerabilities at:
- GitHub Security Advisories
- Our security page: https://cineiq.com/security

## Bug Bounty Program

We currently do not have a bug bounty program, but we greatly appreciate responsible disclosure and will acknowledge contributors.

## Contact

- Security Email: security@cineiq.com
- General Contact: support@cineiq.com
- GitHub Issues: https://github.com/iitg-coding-club/cineiq/issues (for non-security bugs)

## Acknowledgments

We thank the following security researchers for their responsible disclosure:

- (None yet - be the first!)

---

Last Updated: 2026-05-09
