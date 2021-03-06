# Using pixyz batch image
FROM pixyzinc/batch:2020.1.2.16

# Copy Pixyz License file to PiXYZStudio/licenses folder
COPY pixyz.lic /usr/share/PiXYZStudio/licenses/pixyz.lic

# Install python and related packages
RUN apt-get update -y && \
  apt-get install python3-pip wget unzip -y && \
  pip3 install --no-cache-dir --upgrade pip && \
  \
  # delete cache and tmp files
  apt-get clean && \
  apt-get autoclean && \
  rm -rf /var/cache/* && \
  rm -rf /tmp/* && \
  rm -rf /var/tmp/* && \
  rm -rf /var/lib/apt/lists/* && \
  \
  # make some useful symlinks that are expected to exist
  cd /usr/bin && \
  ln -s pydoc3 pydoc && \
  ln -s python3 python && \
  ln -s python3-config python-config && \
  cd /

# Set the application directory
WORKDIR /app

# Copy our requirements.txt
COPY requirements.txt .

# Install requirements.txt to PixyzBatch target
RUN pip install -r requirements.txt -t /opt/PiXYZBatch-2020.1.2.16-amd64/pythonDlls/lib-dynload

# Copy src code to workdir inside the container
COPY src/ .

# Execute from PixyzBatchLauncher
ENTRYPOINT "/usr/bin/PiXYZBatchLaucher" "/app/main.py"