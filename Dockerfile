FROM node

# 1. static instructions
EXPOSE 80
WORKDIR /opt/sickbeetz/web
ENTRYPOINT ["npm"]
CMD ["start"]

# 2. system dependency instructions
ENV PATH="/root/miniconda2/bin:${PATH}"
RUN apt-get update && \
    apt-get install -y libopenblas-dev && \
    wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh && \
    bash Miniconda2-latest-Linux-x86_64.sh -b && \
    npm install -g bower

# 3. app dependency instructions
COPY ./web/package.json /opt/sickbeetz/web/package.json
COPY ./web/bower.json /opt/sickbeetz/web/bower.json
RUN apt-get update && \
    conda install -y numpy scipy matplotlib scikit-learn=0.16.1 && \
    pip install librosa==0.3.1 && \
    npm install && \
    bower install -F --allow-root

# 4. app copy instructions
COPY . /opt/sickbeetz
