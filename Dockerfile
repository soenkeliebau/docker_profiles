FROM asciidoctor/docker-asciidoctor
MAINTAINER Sönke Liebau <soenke.liebau@opencore.com>
RUN pip install jinja2
ADD generate_profiles.sh /usr/local/bin/generate_profiles.sh
ADD main.py /usr/local/bin/main.py
ENTRYPOINT /usr/local/bin/generate_profiles.sh