FROM blang/latex
MAINTAINER Sönke Liebau <soenke.liebau@opencore.com>

RUN apt-get update -q
RUN apt-get -qy install python python-pip
RUN pip install jinja2
ADD generate_profiles.sh /usr/local/bin/generate_profiles.sh
ADD main.py /usr/local/bin/main.py

# Install necessary fonts
RUN mkdir /usr/share/fonts/truetype/helvetica
COPY font/* /usr/share/fonts/truetype/helvetica/

WORKDIR /documents
VOLUME ["/documents"]
ENTRYPOINT /usr/local/bin/generate_profiles.sh
#ENTRYPOINT /bin/bash