# EvoAgentX Medical AI — Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x | Yes |
| 0.1.x | No |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** open a public GitHub issue
2. Email: mokangmedical@users.noreply.github.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Measures

### API Key Protection
- API keys are stored in `.env` (gitignored)
- Keys are masked in logs (`sk-1234...5678`)
- No keys are transmitted to third parties

### Input Validation
- All user inputs are sanitized before API calls
- SQL injection prevention (parameterized queries)
- XSS prevention (HTML escaping)
- Path traversal prevention

### Rate Limiting
- Per-API rate limits enforced
- NCBI: 3-10 req/s
- ClinicalTrials.gov: 10 req/s
- OpenFDA: 4 req/s
- RxNorm: 5 req/s

### Medical Safety
- All medical outputs include disclaimers
- Safety keyword blacklist prevents harmful advice
- Evidence traceability (PMID/NCT ID citations)
- No clinical diagnoses or treatment recommendations

### Data Privacy
- No user data is collected
- No telemetry or analytics
- All data stays local
- Cache is stored locally (~/.evoagentx/cache)

## Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive configuration
3. **Enable 2FA** on your GitHub account
4. **Regularly rotate** API keys
5. **Review** third-party dependencies

## Dependencies

We regularly update dependencies to patch security vulnerabilities:
- `pip audit` checks for known vulnerabilities
- Dependabot alerts for critical updates
- Security patches applied within 7 days

## Compliance

This project is designed for research purposes. For clinical use:
- Consult your institution's IRB/Ethics Committee
- Ensure HIPAA compliance for patient data
- Follow local regulations for medical AI
- Validate all outputs with healthcare professionals
