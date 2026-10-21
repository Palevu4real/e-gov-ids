FROM node:20-alpine

WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app
COPY . .

EXPOSE 5173

# Start Vite in dev mode (host 0.0.0.0 so Docker exposes it)
CMD ["npm", "run", "dev", "--", "--host"]