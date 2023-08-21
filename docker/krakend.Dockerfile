
# Second stage: Set up the runtime environment
FROM devopsfaith/krakend:latest

COPY ./docker/krakend.json /etc/krakend/krakend.json

# Expose KrakenD's default port
EXPOSE 8000

# Use our entrypoint script
CMD [ "run", "-c", "/etc/krakend/krakend.json", "-p", "8000" ]

