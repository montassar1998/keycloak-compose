
# Second stage: Set up the runtime environment
FROM devopsfaith/krakend:latest

COPY ./docker/krakend.json /etc/krakend/krakend.json

# Expose KrakenD's default port
EXPOSE 8000

# The default command to run Krakend with the provided configuration
CMD ["/usr/bin/krakend", "run", "-c", "/etc/krakend/krakend.json", "-d"]