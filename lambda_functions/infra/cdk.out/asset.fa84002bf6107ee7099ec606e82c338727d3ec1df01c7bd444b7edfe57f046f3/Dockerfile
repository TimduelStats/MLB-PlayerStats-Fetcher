FROM amazon/aws-lambda-python:3.12

# Install Chrome dependencies
RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm jq unzip

# Copy and run the Chrome installer script
COPY chrome-installer.sh /chrome-installer.sh
RUN chmod +x /chrome-installer.sh && /chrome-installer.sh && rm /chrome-installer.sh

# Install Python dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy function and utility code
COPY functions/ /var/task/functions/
COPY utils/ /var/task/utils/

CMD [ "functions.fetch_stats.lambda_handler" ]