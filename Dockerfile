
FROM amazon/aws-lambda-python:3.12

# Set the working directory in the container
WORKDIR /var/task

# Install chrome dependencies
RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm jq unzip

# Copy and run the chrome installer script
COPY ./build/chrome-installer.sh ./chrome-installer.sh
RUN sed -i 's/\r$//' ./chrome-installer.sh
RUN chmod +x ./chrome-installer.sh
RUN ./chrome-installer.sh
RUN rm ./chrome-installer.sh

# Use pyproject.toml for dependency management
COPY pyproject.toml ./

# Install pip and build if not present, then install project and dependencies
RUN pip install --upgrade pip build && pip install .

ENV RUNNING_IN_DOCKER=true

# Copy the src directory from the build context into the container at /var/task/src
COPY src/ ./src/
COPY static/combined_fixtures.json ./tmp/

# Command to run the application
CMD ["src.main"]