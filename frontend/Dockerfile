FROM node:22

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]


# # Remove existing React/Tailwind (if any)
# npm uninstall react react-dom @types/react @types/react-dom
# npm uninstall tailwindcss @tailwindcss/forms @tailwindcss/typography
# npm uninstall lucide-react

# # Install matching versions
# npm install react@^18.0.0 react-dom@^18.0.0
# npm install tailwindcss@^3.0.0
# npm install lucide-react@0.263.1

# # Optional: Install additional libraries available in Claude's environment
# npm install recharts mathjs lodash d3 three@0.128.0

# # Initialize Tailwind
# npx tailwindcss init -p