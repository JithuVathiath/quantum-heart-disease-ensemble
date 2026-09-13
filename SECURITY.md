# Security Policy

## Supported Version

The latest release on the default branch receives security fixes.

## Reporting a Vulnerability

Please use GitHub's private vulnerability-reporting feature when available. Do not include patient data, credentials, private repository content, or exploit details in a public issue.

Include the affected revision, reproduction steps using synthetic or public-safe inputs, likely impact, and any suggested mitigation.

## Data and Secret Boundaries

- Raw UCI records are downloaded locally and excluded from Git.
- Public result artefacts contain aggregate statistics only.
- The project requires no API key for the reference statevector benchmark.
- Do not commit IBM Quantum credentials or other tokens.
- ZIP extraction validates destination paths before writing files.

