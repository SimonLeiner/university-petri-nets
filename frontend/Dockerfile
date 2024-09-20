# Use a specific Node.js version for consistency: mathing with backend
FROM --platform=linux/amd64 node:22-alpine

# Set working directory
WORKDIR /app

# Install packages
RUN apk update && apk add \
    # github
    git \
    # for installing packages
    curl \
    # for interacting with remote servers
    openssh-client \
    # clean up
    && rm -rf /var/cache/apk/*

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the server will run on
EXPOSE 3000

# Start the Vite development server
CMD ["npm", "run", "dev"]

