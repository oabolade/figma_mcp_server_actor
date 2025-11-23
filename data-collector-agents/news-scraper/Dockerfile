FROM node:20-slim

WORKDIR /app

# Install Playwright dependencies and curl for healthchecks
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm install --production

# Install Playwright browsers
RUN npx playwright install --with-deps chromium

COPY . .

EXPOSE 3001

CMD ["node", "src/index.js"]

