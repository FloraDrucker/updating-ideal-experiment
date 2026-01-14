FROM python:3.11-alpine

RUN apk add --no-cache --update \
    python3 python3-dev g++ \
    gfortran musl-dev linux-headers \
    postgresql-dev

RUN pip3 install --upgrade pip setuptools

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

# Environment variables (must be set at runtime)
# OTREE_SECRET_KEY - Required for session security
# OTREE_ADMIN_PASSWORD - Required for admin panel access
# DATABASE_URL - Optional, defaults to SQLite

CMD ["otree", "prodserver", "3001"]
