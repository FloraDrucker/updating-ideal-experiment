# Study on Work - oTree Experiment

A behavioral economics experiment built with oTree that studies participant behavior, beliefs, and decision-making under different financial incentive structures.

## Prerequisites

- Python 3.11 (see `.python-version`)
- pip
- Git

## Local Development Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd updating-ideal-experiment
```

### 2. Create and activate a virtual environment

**macOS/Linux:**
```bash
python3.11 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set environment variables (optional for development)

For local development, the app will run with warnings if these are not set:

```bash
export OTREE_SECRET_KEY="your-secret-key-here"
export OTREE_ADMIN_PASSWORD="your-admin-password"
```

### 5. Initialize the database

```bash
otree resetdb
```

### 6. Run the development server

```bash
otree devserver
```

The experiment will be available at `http://localhost:8000`

- **Demo page:** `http://localhost:8000/demo`
- **Admin panel:** `http://localhost:8000/admin`

## Running Bot Tests

oTree includes a bot testing framework that simulates participants:

```bash
otree test study_on_work
```

## Docker Deployment

### Build the image

```bash
docker build -t study-on-work .
```

### Run the container

**Required environment variables for production:**

```bash
docker run -d \
  -p 3001:3001 \
  -e OTREE_SECRET_KEY="your-secure-secret-key" \
  -e OTREE_ADMIN_PASSWORD="your-secure-admin-password" \
  -e DATABASE_URL="postgres://user:pass@host:5432/dbname" \
  study-on-work
```

The experiment will be available at `http://localhost:3001`

### Using docker-compose (optional)

Create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  otree:
    build: .
    ports:
      - "3001:3001"
    environment:
      - OTREE_SECRET_KEY=${OTREE_SECRET_KEY}
      - OTREE_ADMIN_PASSWORD=${OTREE_ADMIN_PASSWORD}
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OTREE_SECRET_KEY` | Production | Secret key for session/cookie signing |
| `OTREE_ADMIN_PASSWORD` | Production | Password for admin panel access |
| `DATABASE_URL` | Optional | PostgreSQL connection string (defaults to SQLite) |

## Project Structure

```
├── instructions_consent/    # Consent and comprehension screening app
├── study/                   # Main experiment app (6 rounds)
│   ├── __init__.py         # Player model, pages, payment logic
│   ├── Task.html           # Encryption task UI
│   └── tests.py            # Bot tests
├── _static/                 # Static assets
├── settings.py              # oTree configuration
├── requirements.txt         # Python dependencies
└── Dockerfile              # Container configuration
```

## Experiment Flow

1. **instructions_consent app:** Welcome, task instructions, comprehension check, consent
2. **study app (6 rounds):**
   - Round 1: Trial round
   - Rounds 2-6: Main experiment with beliefs, ideals, predictions, and surveys
   - Final round includes payment calculation

## License

[Add your license here]
