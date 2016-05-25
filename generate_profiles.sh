#!/usr/bin/env bash

# TODO: Create build environment
rm -rf /documents/build
mkdir -p /documents/build/pdf
cp -r /documents/resources /documents/build/

for template in /documents/templates/*.j2; do
    template=$(basename "$template")
    echo "Beginning processing for template $template.."
    for profile in /documents/input/*.json; do
        filename=$(basename "$profile")
        filename="${filename%.*}"
        adocfile="/documents/build/${filename}.adoc"
        pdffile="/documents/build/pdf/${filename}.pdf"
        echo "Generating intermediate file from $filename into $adocfile"
        python /usr/local/bin/main.py -t $template -i $profile -o $adocfile
        echo "Writing $pdffile"
        asciidoctor -r asciidoctor-pdf -b pdf $adocfile -o $pdffile
    done
done