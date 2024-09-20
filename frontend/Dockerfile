# Use a specific Node.js version for consistency: matching with backend
FROM --platform=linux/amd64 node:22-bullseye

# Set working directory
WORKDIR /app

# Install packages
RUN apt-get update && apt-get install -y \
    # github
    git \
    # for installing packages
    curl \
    # for interacting with remote servers
    openssh-client \
    # clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json and package-lock.json
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY frontend .

# Expose the port the server will run on
EXPOSE 3000

# Start the Vite development server
CMD ["npm", "run", "dev"]

