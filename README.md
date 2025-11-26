# QR Code Generator API

A secure, stateless REST API for generating QR codes on-demand with support for multiple formats and authentication.

## Features

- 🔐 **JWT Authentication** - Secure API access with Bearer tokens
- 📱 **Multiple Formats** - PNG, SVG, JPEG, PDF output support
- 📏 **Configurable Sizes** - Small (150px), Medium (300px), Large (600px)
- 🛡️ **Error Correction** - L, M, Q, H levels for different use cases
- ⚡ **High Performance** - <500ms generation, 100+ concurrent requests
- 🧪 **Comprehensive Testing** - Unit, integration, and contract tests
- 📊 **Performance Logging** - Built-in performance monitoring

## Quick Start

### Prerequisites

- Python 3.11+
- pip

### 🔐 Authentication

The API requires JWT authentication for all endpoints except `/v1/health`.

### Getting a Token

Generate a JWT token using your credentials:

```bash
curl -X POST "http://localhost/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the Token

Include the token in your API requests:

```bash
curl -X POST "http://localhost:8000/v1/qr-code" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"data": "Hello World!", "size": "medium", "format": "png"}'
```

### Validating a Token

Check if a token is still valid:

```bash
curl -X POST "http://localhost/v1/auth/validate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Default Credentials (Development)

- Username: `admin` / Password: `secure_password_123`
- Username: `testuser` / Password: `test_password_456`

### Configuration

Set up users via environment variable:

```bash
AUTH_USERS='{"admin": "your_password", "api_user": "another_password"}'
```

For Coolify deployment, use escaped format:
```bash
AUTH_USERS={\"admin\": \"your_password\", \"api_user\": \"another_password\"}
```

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd qr-code-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the API:
```bash
python src/main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc
- **OpenAPI Schema**: http://localhost/openapi.json

## 🚀 API Endpoints

### Authentication Endpoints

#### Generate Token
```bash
POST /v1/auth/token
Content-Type: application/json

{
  "username": "admin",
  "password": "your_password"
}
```

#### Validate Token
```bash
POST /v1/auth/validate
Authorization: Bearer <your-token>
```

### QR Code Endpoints

#### Generate QR Code
```bash
POST /v1/qr-code
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "data": "Hello World!",
  "size": "medium",
  "format": "png",
  "error_correction": "M"
}
```

**Supported Sizes**: `small`, `medium`, `large`  
**Supported Formats**: `png`, `svg`, `jpeg`, `pdf`  
**Error Correction**: `L`, `M`, `Q`, `H`

#### Health Check (No Auth Required)
```bash
GET /v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T15:00:00Z",
  "version": "1.0.0"
}
```

## Usage

### Authentication

All endpoints (except `/health`) require JWT authentication:

```bash
# Include Bearer token in Authorization header
Authorization: Bearer <your-jwt-token>
```

### Generate QR Code

```bash
curl -X POST "http://localhost/v1/qr-code" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "data": "Hello, World!",
    "size": "medium",
    "format": "png",
    "error_correction": "M"
  }' \
  --output qr-code.png
```

### Health Check

```bash
curl "http://localhost/v1/health"
```

## 📝 Examples

### Complete Workflow

```bash
# 1. Get authentication token
TOKEN=$(curl -s -X POST "http://localhost/v1/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secure_password_123"}' | \
  jq -r '.access_token')

# 2. Generate QR code with the token
curl -X POST "http://localhost/v1/qr-code" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"data": "https://example.com", "size": "medium", "format": "png"}' \
  --output website-qrcode.png
```

### Different Formats

```bash
# SVG format (vector)
curl -X POST "http://localhost/v1/qr-code" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"data": "Contact: John Doe", "format": "svg"}' \
  --output contact.svg

# PDF format (print)
curl -X POST "http://localhost/v1/qr-code" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"data": "Invoice #12345", "format": "pdf", "size": "large"}' \
  --output invoice.pdf

# High error correction for damaged codes
curl -X POST "http://localhost/v1/qr-code" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"data": "Critical data", "error_correction": "H", "format": "png"}' \
  --output robust.png
```

### Python Example

```python
import requests
import json

# Get token
auth_response = requests.post("http://localhost/v1/auth/token", 
  json={"username": "admin", "password": "secure_password_123"})
token = auth_response.json()["access_token"]

# Generate QR code
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
qr_response = requests.post("http://localhost/v1/qr-code",
  headers=headers,
  json={"data": "https://github.com", "format": "png", "size": "medium"})

# Save QR code
with open("github-qr.png", "wb") as f:
    f.write(qr_response.content)
```

### JavaScript Example

```javascript
// Get token
const authResponse = await fetch('http://localhost/v1/auth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'secure_password_123'
  })
});
const { access_token } = await authResponse.json();

// Generate QR code
const qrResponse = await fetch('http://localhost/v1/qr-code', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    data: 'Hello from JavaScript!',
    format: 'svg'
  })
});

const qrBlob = await qrResponse.blob();
download(qrBlob, 'qr-code.svg');
```

## API Parameters

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `data` | string | Required | - | Text or URL to encode (max 2000 chars) |
| `size` | string | `"medium"` | `"small"`, `"medium"`, `"large"` | QR code size in pixels |
| `format` | string | `"png"` | `"png"`, `"svg"`, `"jpeg"`, `"pdf"` | Output image format |
| `error_correction` | string | `"M"` | `"L"`, `"M"`, `"Q"`, `"H"` | Error correction level |

## Size Specifications

| Size | Dimensions | Use Case |
|------|------------|----------|
| `small` | 150×150px | Mobile displays, small icons |
| `medium` | 300×300px | General purpose, web use |
| `large` | 600×600px | Print, high-density displays |

## Error Correction Levels

| Level | Correction Capacity | Use Case |
|-------|---------------------|----------|
| `L` | ~7% | Clean environments, maximum data |
| `M` | ~15% | General purpose (default) |
| `Q` | ~25% | Industrial, some damage expected |
| `H` | ~30% | Print, labels, harsh environments |

## 🚨 Error Handling

### HTTP Status Codes

| Status | Description | Example |
|--------|-------------|---------|
| `200` | Success | QR code generated successfully |
| `400` | Bad Request | Invalid parameters or data |
| `401` | Unauthorized | Invalid or missing authentication |
| `403` | Forbidden | Insufficient permissions |
| `413` | Payload Too Large | Data exceeds QR code capacity |
| `415` | Unsupported Media Type | Invalid format requested |
| `422` | Unprocessable Entity | Cannot generate QR code |
| `500` | Internal Server Error | Server error occurred |

### Error Response Format

```json
{
  "error": "validation_error",
  "message": "Data cannot be empty",
  "details": {
    "field": "data",
    "constraint": "min_length"
  }
}
```

## 🔒 Security

### Authentication

- **JWT Bearer Tokens** required for all endpoints except `/v1/health`
- **Token Expiration**: 30 minutes (configurable)
- **Secure Credentials**: Environment variable configuration
- **No Password Storage**: Stateless authentication

### Best Practices

1. **Change Default Credentials**
   ```bash
   # Never use default passwords in production
   SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
   AUTH_USERS='{"admin": "strong_unique_password"}'
   ```

2. **Use HTTPS in Production**
   ```bash
   # Configure SSL/TLS in your reverse proxy
   # Never expose JWT tokens over unencrypted connections
   ```

3. **Token Management**
   ```bash
   # Store tokens securely on client side
   # Implement token refresh if needed
   # Validate tokens before each request
   ```

4. **Rate Limiting**
   ```bash
   # Consider implementing rate limiting
   # Monitor API usage patterns
   # Set reasonable request limits
   ```

## Deployment

### 🚀 Coolify Deployment (Recommended)

The easiest way to deploy to production is using Coolify:

1. **Push to Git Repository**
```bash
git add .
git commit -m "Ready for production"
git push origin main
```

2. **Create Application in Coolify**
- New Application → Docker → Git Repository
- Configure environment variables (see `.env.production`)
- Set health check to `/v1/health`
- Deploy!

📖 **Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Docker Deployment

```bash
# Build image
docker build -t qr-code-api .

# Run container
docker run -p 8000:8000 --env-file .env qr-code-api
```

### Docker Compose

```bash
docker-compose up -d
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Edit .env with your settings

# Run API
python src/main.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `true` | Enable debug mode |
| `SECRET_KEY` | - | JWT secret key (required) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `LOG_LEVEL` | `INFO` | Logging level |

## Architecture

```
src/
├── api/
│   └── endpoints/
│       └── qr.py         # QR generation endpoint
├── models/
│   ├── requests.py       # Request/response models
│   └── auth.py          # Authentication models
├── services/
│   ├── qr_generator.py  # QR code generation logic
│   └── auth.py          # Authentication service
├── utils/
│   ├── validators.py    # Input validation
│   └── logging.py       # Logging utilities
├── middleware/
│   └── auth.py          # Bearer token middleware
├── config.py            # Application configuration
└── main.py              # FastAPI application entry

tests/
├── unit/
│   ├── test_qr_generator.py
│   ├── test_validators.py
│   └── test_auth.py
├── integration/
│   ├── test_api.py
│   └── test_auth.py
└── contract/
    └── test_qr_api.py    # API contract tests
```

## Performance

- **Target Generation Time**: <500ms per QR code
- **Concurrent Requests**: 100+ simultaneous
- **Memory Usage**: ~10-160MB per request (depending on size)
- **Supported Formats**: PNG, SVG, JPEG, PDF

## Security

- JWT-based authentication
- Input validation and sanitization
- Error handling without information leakage
- CORS configuration
- Rate limiting (configurable)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples
