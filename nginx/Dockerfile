FROM nginx:alpine

# Install openssl to generate self-signed certificate on startup
RUN apk add --no-cache openssl

# Copy custom Nginx configuration
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script and ensure execute permissions
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80 443

ENTRYPOINT ["/entrypoint.sh"]
