# Security Guidelines for ChainSync Platform

## Overview
This document outlines security best practices and requirements for deploying and maintaining the ChainSync Environmental Services Platform.

## Critical Security Requirements

### 1. API Key Management

**NEVER commit API keys to version control!**

#### For Local Development:
1. Create a `config-local.properties` file (add to `.gitignore`)
2. Add your actual API keys to this file:
   ```properties
   openweathermap.api.key=your_actual_api_key_here
   ```

#### For Production (CloudHub/Runtime Manager):
1. Use CloudHub secure properties or Runtime Manager properties
2. Set the following secure properties:
   - `secure::openweathermap.api.key` - Your OpenWeatherMap API key
   - `secure::db.username` - Database username
   - `secure::db.password` - Database password

#### Example Configuration:
```properties
# Development (config-local.properties)
openweathermap.api.key=your_dev_key_here

# Production (CloudHub Properties)
openweathermap.api.key=${secure::openweathermap.api.key}
db.username=${secure::db.username}
db.password=${secure::db.password}
```

### 2. HTTPS Enforcement

**All external API calls must use HTTPS protocol.**

- ✅ Correct: `https://api.openweathermap.org/...`
- ❌ Incorrect: `http://api.openweathermap.org/...`

All HTTP request configurations in `external-api-config.xml` enforce HTTPS.

### 3. Authentication & Authorization

#### API Security Configuration

For production environments, ensure these settings in `config.properties`:

```properties
# Enable API authentication
security.api.key.required=true

# Enable rate limiting to prevent abuse
security.rate.limiting=true

# Enable audit logging for compliance
security.audit.logging=true

# Enable data encryption
security.data.encryption=true
```

#### Development vs Production

Development/Testing:
```properties
security.api.key.required=false  # Only for local dev!
```

Production:
```properties
security.api.key.required=true   # ALWAYS required!
```

### 4. Request Timeouts

All HTTP request configurations include timeouts to prevent hanging connections:

- **Connection Timeout**: 30 seconds (configurable via `timeout.default`)
- **Read Timeout**: 30 seconds
- **Emergency Operations**: 5 seconds (via `timeout.emergency`)

Configure in `config.properties`:
```properties
timeout.default=30000      # 30 seconds
timeout.emergency=5000     # 5 seconds for critical operations
```

### 5. Input Validation

Always use proper query parameters instead of string concatenation to prevent injection attacks:

**Correct Approach:**
```xml
<http:request method="GET" url="https://api.example.com/endpoint">
    <http:query-params><![CDATA[#[{
        'param1': vars.userInput,
        'param2': vars.facilityId
    }]]]></http:query-params>
</http:request>
```

**Incorrect Approach (Vulnerable to injection):**
```xml
<!-- DO NOT USE -->
<http:request url="#['https://api.example.com/endpoint?param=' ++ vars.userInput]"/>
```

### 6. Error Handling

**Do not expose internal error details to external clients.**

Use standardized error responses from `global-functions.dwl`:

```dataweave
import * from global-functions
---
generateErrorResponse("ERROR_CODE", "User-friendly message")
```

This generates:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly message",
    "timestamp": "2025-11-07T10:30:00Z"
  }
}
```

## Security Checklist for Deployment

Before deploying to production:

- [ ] All API keys moved to secure properties
- [ ] `security.api.key.required=true` in config.properties
- [ ] `security.data.encryption=true` in config.properties
- [ ] All HTTP calls use HTTPS protocol
- [ ] Request timeouts configured for all external API calls
- [ ] Database credentials use secure properties
- [ ] No sensitive data in logs (use `maskSensitiveData()` function)
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] CORS policies configured (if needed)
- [ ] TLS 1.2+ enforced for all connections

## Secure Configuration Template

Use this template for production deployments:

```properties
# API Configuration
openweathermap.api.key=${secure::openweathermap.api.key}

# Database Configuration
db.username=${secure::db.username}
db.password=${secure::db.password}

# Security Configuration
security.api.key.required=true
security.rate.limiting=true
security.audit.logging=true
security.data.encryption=true

# Timeouts
timeout.default=30000
timeout.emergency=5000
```

## Incident Response

If an API key or credential is compromised:

1. **Immediately** revoke the compromised key
2. Generate new keys/credentials
3. Update secure properties in CloudHub/Runtime Manager
4. Rotate all related secrets
5. Review audit logs for suspicious activity
6. Document the incident

## Security Testing

Regular security testing should include:

1. **API Key Exposure**: Scan repository for hardcoded secrets
2. **HTTPS Enforcement**: Verify all external calls use HTTPS
3. **Authentication**: Test that protected endpoints require auth
4. **Input Validation**: Test for SQL injection, XSS, etc.
5. **Timeout Handling**: Verify timeouts prevent hanging connections
6. **Error Messages**: Ensure no sensitive data in error responses

## Compliance

This platform handles environmental data subject to:

- EPA reporting requirements
- State DEQ regulations
- OSHA monitoring standards
- ISO 14001 & ISO 45001 standards

Ensure all security measures support regulatory compliance requirements.

## Contact

For security concerns or to report vulnerabilities, contact:
- Security Team: security@company.com
- Emergency Response: emergency-team@company.com

## References

- [MuleSoft Security Best Practices](https://docs.mulesoft.com/mule-runtime/latest/secure-configuration-properties)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [EPA Cybersecurity Guidelines](https://www.epa.gov/cybersecurity)
