# Step 1: Use an official Nginx image as a base
FROM nginx:alpine

# Step 2: Copy your frontend files into the Nginx container
COPY . /usr/share/nginx/html/

# Step 3: Expose port 80 to access the frontend
EXPOSE 80

# Step 4: Nginx will automatically serve files from /usr/share/nginx/html
