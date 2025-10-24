FROM golang:1.23-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

FROM alpine:latest

RUN apk --no-cache add ca-certificates

RUN adduser -D -s /bin/sh frauduser

WORKDIR /app

COPY --from=builder /app/main .

COPY .env .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

CMD env && ./main \
    --port $PORT \
    --db $DB_URL \
    --migration_file_dir /app/migration \
    --env $ENV \
    --base_url $BASE_URL \
    --frontend_base_url $FRONTEND_URL \
EXPOSE $PORT
