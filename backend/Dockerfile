FROM golang:1.23-alpine AS builder

WORKDIR /app

RUN apk add --no-cache git

COPY go.mod go.sum ./

RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd

FROM alpine:latest

RUN apk --no-cache add ca-certificates

RUN adduser -D -s /bin/sh frauduser

WORKDIR /app

COPY --from=builder /app/main .

# Copy seed files for data type initialization
COPY --from=builder /app/data ./data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

USER frauduser

EXPOSE 8080

CMD ["sh", "-c", "export ENGINE_URL=$ENGINE_URL && export DATA_MANAGEMENT_SERVICE_URL=$DATA_MANAGEMENT_SERVICE_URL && ./main -db=\"$DATABASE_URL\" -rule_engine_url=\"$ENGINE_URL\" -decision_service_url=\"$DECISION_SERVICE_URL\" -data_management_service_url=\"$DATA_MANAGEMENT_SERVICE_URL\" -anomaly_detection_engine_url=\"$ANOMALY_DETECTION_ENGINE_URL\" -predictive_engine_url=\"$PREDICTIVE_ENGINE_URL\" -cors_origins=\"$CORS_ALLOWED_ORIGINS\" -swagger=\"$ENABLE_SWAGGER\""]
