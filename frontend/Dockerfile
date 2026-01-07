FROM node:18-alpine

WORKDIR /app

# Copy package.json and lockfile
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 5173

# Run dev server with --host to expose to network
CMD ["npm", "run", "dev", "--", "--host"]
