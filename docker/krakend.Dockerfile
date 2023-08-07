# Use official KrakenD image as a base
FROM devopsfaith/krakend:latest

# Copy our custom krakend.json configuration into the container
COPY krakend.json /etc/krakend/krakend.json

# Expose KrakenD's default port
EXPOSE 8000

# Entry point is KrakenD's binary
ENTRYPOINT [ "/usr/bin/krakend" ]
CMD [ "run", "-c", "/etc/krakend/krakend.json", "-p", "8000" ]
