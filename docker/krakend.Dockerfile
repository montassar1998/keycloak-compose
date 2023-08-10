FROM alpine:3.14 as alpine
RUN apk update

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
COPY --from=builder /app/krakend.json /app/krakend.json


# Expose KrakenD's default port
EXPOSE 8000

# Use our entrypoint script
CMD [ "run", "-c", "/etc/krakend/krakend.json", "-p", "8000" ]

