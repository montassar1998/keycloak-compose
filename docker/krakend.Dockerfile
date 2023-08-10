

# First stage: Set up the tools
FROM debian:bullseye-slim AS builder
RUN apt-get update && apt-get install -y gettext-base

# Copy krakend.json (this should be your template with placeholders)
COPY ./docker/krakend.json /etc/krakend/krakend.template.json

# Second stage: Set up the runtime environment
FROM devopsfaith/krakend:latest

# Copy tools and files from the builder stage
COPY --from=builder /usr/bin/envsubst /usr/bin/envsubst
COPY --from=builder /etc/krakend/krakend.template.json /etc/krakend/krakend.template.json

# Copy the entrypoint script and the .env file
COPY krakend-entrypoint.sh /krakend-entrypoint.sh
COPY .env /app/.env

# Make the script executable
RUN chmod +x /krakend-entrypoint.sh

# Expose KrakenD's default port
EXPOSE 8000

# Use our entrypoint script
ENTRYPOINT ["/krakend-entrypoint.sh"]
CMD [ "run", "-c", "/etc/krakend/krakend.json", "-p", "8000" ]

