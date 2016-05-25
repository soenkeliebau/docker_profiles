#!/usr/bin/env bash

# TODO: Create build environment
rm -rf /documents/build
mkdir -p /documents/build/pdf
cp -r /documents/resources /documents/build/

for template in /documents/templates/*.j2; do
    template=$(basename "$template")
    for profile in /documents/input/*.json; do
        filename=$(basename "$profile")
        filename="${filename%.*}"
        python /usr/local/bin/main.py -t $template -i $profile -o /documents/build/
    done
done
for adocfile in /documents/build/*.adoc; do
    filename=$(basename "$adocfile")
    filename="${filename%.*}"
    pdffile="/documents/build/pdf/${filename}.pdf"
    asciidoctor -r asciidoctor-pdf -b pdf $adocfile -o $pdffile
done