# Use an official Node.js runtime as a parent image
FROM node:14-alpine

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in package.json
COPY package*.json ./
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port that the application listens on
EXPOSE 8080

# Run the application
CMD ["npm", "start"]