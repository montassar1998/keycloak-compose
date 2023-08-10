FROM alpine:3.14 as alpine
RUN apk add --no-cache gettext
COPY ./docker/krakend.json /app/krakend.template.json
COPY ./.env /app/.env
RUN export $(grep -v '^#' /app/.env | xargs) && envsubst < /app/krakend.template.json > /app/krakend.json

# First stage: Replace values in the krakend.json
FROM busybox AS builder
COPY --from=alpine /usr/bin/envsubst /usr/local/bin/
COPY --from=alpine /app/krakend.json /app/krakend.json



# Second stage: Set up the runtime environment
FROM devopsfaith/krakend:latest

# Copy tools and files from the builder stage
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

