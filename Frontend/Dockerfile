# Use a lightweight Node.js image
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install frontend dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose Vite's default port
EXPOSE 5173

# Run the dev server and expose it to the network
CMD ["npm", "run", "dev", "--", "--host"]