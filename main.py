#!/usr/bin/env python

import json, os, getopt, sys, codecs

from jinja2 import Environment, FileSystemLoader


def main(argv):
    inputfile = ''
    outputfile = ''
    templatefile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:t:",["ifile=","ofile=","template="])
    except getopt.GetoptError:
        print 'main.py -i <inputfile> -o <outputfile> -t <templatefile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'main.py -i <inputfile> -o <outputfile> -t <templatefile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-t", "--template"):
            templatefile = arg

    if templatefile == '' or outputfile == '' or inputfile == '':
        print 'main.py -i <inputfile> -o <outputfile> -t <templatefile>'
        sys.exit(2)

    print 'Input file is ', inputfile
    print 'Output file is ', outputfile
    print 'Template file is ', templatefile

    with open(inputfile) as json_file:
        data = json.load(json_file)

    filename = u'_'.join((data["personal_data"]["first_name"],data["personal_data"]["last_name"])).encode("ascii","ignore")

    outputfile = outputfile + "OpenCore_" + filename + "_" + os.path.splitext(templatefile)[0] + ".tex"

    PATH = os.path.dirname('/documents/templates/')
    TEMPLATE_ENVIRONMENT = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(PATH, '')),
        trim_blocks=False,
        block_start_string = '((*',
        block_end_string = '*))',
        variable_start_string = '(((',
        variable_end_string = ')))',
        comment_start_string = '((=',
        comment_end_string = '=))')

    context = {
        'data': data
    }

    print outputfile
    with codecs.open(outputfile, 'w', 'utf-8') as f:
        html = TEMPLATE_ENVIRONMENT.get_template(templatefile).render(context)
        f.write(html)

if __name__ == "__main__":
    main(sys.argv[1:])






