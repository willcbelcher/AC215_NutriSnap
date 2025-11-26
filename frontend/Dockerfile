# 1. Use Node.js 18 (Alpine)
FROM node:lts-alpine

# 2. Set the working directory
WORKDIR /app

# 3. Copy package.json AND yarn.lock
# This allows Docker to cache the dependencies step if these files haven't changed
COPY package.json yarn.lock ./

# 4. Install dependencies using Yarn
# --frozen-lockfile ensures it fails if yarn.lock needs updates (good for CI/Prod)
RUN yarn install --frozen-lockfile

# 5. Copy the rest of the application code
COPY . .

# 6. Build the Nuxt application
RUN yarn build

# 7. Expose the port
EXPOSE 3000

# 8. Set environment variables for the standalone server
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# 9. Start the application
CMD ["node", ".output/server/index.mjs"]