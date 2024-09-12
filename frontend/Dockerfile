# Use a specific Node.js version for consistency
FROM node:22-alpine

# set working directory
WORKDIR /workspace

# install git 
RUN apk update && apk install --no-install-recommends  -y \
    # graphviz
    graphviz \
    # github
    git \
    # for installing packages
    curl \
    # for interacting with remote servers
    openssh-client\
    # clean up
    && apk clean\
    && rm -rf /var/lib/apt/lists/*

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI server will run on
EXPOSE 3000

# Start the Vite development server
CMD ["npm", "run", "dev"]
