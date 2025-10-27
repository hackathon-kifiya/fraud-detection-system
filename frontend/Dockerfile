FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies including serve
RUN npm install && npm install -g serve

# Copy source code
COPY . .

# Set build-time environment variables
ARG REACT_APP_BACKEND_URL
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL

ARG REACT_APP_RULE_ENGINE_URL
ENV REACT_APP_RULE_ENGINE_URL=$REACT_APP_RULE_ENGINE_URL

ARG REACT_APP_DECISION_SERVICE_URL
ENV REACT_APP_DECISION_SERVICE_URL=$REACT_APP_DECISION_SERVICE_URL

ARG REACT_APP_DATA_MANAGEMENT_SERVICE_URL
ENV REACT_APP_DATA_MANAGEMENT_SERVICE_URL=$REACT_APP_DATA_MANAGEMENT_SERVICE_URL

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start the application using serve
CMD ["serve", "-s", "build", "-l", "3000"]

