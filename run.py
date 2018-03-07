#!/usr/bin/env python

import json, os, getopt, sys, codecs

from jinja2 import Environment, FileSystemLoader
from subprocess import call
from shutil import copyfile, copytree, rmtree

# Define locations of fixed input files - all other files need to be referenced in these files
# to be picked up
# TODO: make this a parameter

# Default directories under the basedir
DEFAULTWORKDIRSUFFIX = 'build/'
DEFAULTOUTPUTDIRSUFFIX = 'output/'
DEFAULTCONFIGFILE = 'config/inputfiles.json'
DEFAULTTEMPLATEFILE = 'config/templates.json'

baseDirectory = '/documents/'
workingDirectory = ''
outputDirectory = ''
templateFile = '' # defines all available templates
configFile = '' # defines input files and which templates should be applied to them

def main(argv):
    # initialize paths vars
    initialize(argv)

    # read json from input files

    with open(templateFile) as templateJson , open(configFile) as configJson:
        try:
            # Set current file to be processed so we can use it in a potential error message
            # this is simply to avoid having two try blocks
            currentFile = 'template file(' + templateFile + ')'
            print 'Reading ' + currentFile

            templateData = json.load(templateJson)
            currentFile = 'config file(' + configFile + ')'
            print 'Reading ' + currentFile
            configData = json.load(configJson)
        except Exception, e:
            print "Invalid json in " +  currentFile + " - aborting!"
            return
    # TODO: add schema validation

    # Create dict with template data for easier retrieval later on
    templateDict = dict()
    for template in templateData:
        templateDict[template['name']] = template

    setupBuildEnv()

    # start processing input files
    for inputFile in configData:
        for template in inputFile['templates']:
            # Pass both loaded dicts to the routine that applies the input to the template
            processFile(inputFile, templateDict[template])



    return


def initialize(args):
    global baseDirectory, inputDirectory, templateDirectory, workingDirectory, outputDirectory, configFile, templateFile, scriptDirectory
    print 'Initializing paths:'

    if baseDirectory == '':
        baseDirectory = os.getcwd() + '/'

    print 'Base directory -> ' + baseDirectory

    # TODO: implement overriding these with command line arguments
    # Set directories
    workingDirectory = baseDirectory + DEFAULTWORKDIRSUFFIX
    print "Work directory -> " + workingDirectory

    outputDirectory = baseDirectory + DEFAULTOUTPUTDIRSUFFIX
    print 'Output directory -> ' + outputDirectory

    # Set config files from Defaults
    configFile = baseDirectory + DEFAULTCONFIGFILE

    templateFile = baseDirectory + DEFAULTTEMPLATEFILE
    return


def processFile(inputFile, template):
    global workingDirectory, outputDirectory

    templateFile = template['template_file']

    print '==================================================================='
    print ' Input file: ' + inputFile['inputfile']
    print ' Template: ' + template['name'] +  '   ->   ' + baseDirectory + templateFile
    print ' Output file: ' + getOutputFile(inputFile, template)
    print '==================================================================='
    PATH = os.path.dirname(baseDirectory)
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

    print 'Loading input data..'
    with open(baseDirectory + inputFile['inputfile']) as inputJson:
        try:
            inputData = json.load(inputJson)
        except Exception, e:
            print 'Error loading input file ' + inputFile + ' skipping ..'
            print 'Failed!! \n\n\n'
            return

    context = {
        'data': inputData
    }

    currentWorkingDirectory = workingDirectory + template['name'] + '/'
    print 'Creating working directory: ' + currentWorkingDirectory
    createDir(currentWorkingDirectory)

    # Check whether a resources folder was defined and if so copy this to the build dir for that template
    if 'resources' in template:
        resourceDirectory = baseDirectory + template['resources']
        buildResourceDirectory = workingDirectory + template['name'] + '/' + template['resources']

        # Check if target already exists from a previous run for this template
        if not os.path.isdir(buildResourceDirectory):
            print 'Copying resources folder into working directory'
            copytree(resourceDirectory, buildResourceDirectory)
            print resourceDirectory + ' -> ' + buildResourceDirectory
        else:
            print 'Resource directory already exists from prior input file, skip copying.'

    intermediateFile = getIntermediateFile(inputFile, template)

    print 'Applying input to template -> ' + intermediateFile
    try:
        with codecs.open(intermediateFile, 'w', 'utf-8') as f:
            html = TEMPLATE_ENVIRONMENT.get_template(templateFile).render(context)
            f.write(html)
    except Exception, e:
        print 'Error applying input data to template:' + str(e)
        print 'Failed!! \n\n\n'
        return

    # At this point we have generated the intermediate file for this combination of inputfile & template
    # next run the post processing script (if any) and move resulting files to output directory

    if 'post_processing' in template:
        # Post processing script was defined, so run it
        # scripts have to accept two parameters: inputfile and outputfile in that order
        postScript = getPostScript(template)
        outputFile = getOutputFile(inputFile, template)
        finalFile = getFinalFile(inputFile, template)
        stdoutFile = open(outputFile + '.' + 'stdout','w+')
        stderrFile = open(outputFile + '.' + 'stderr','w+')

        print 'Running post processing script ' + postScript + '  ->  ' + finalFile + ' in working dir: ' + currentWorkingDirectory
        returnCode = call([postScript, intermediateFile, outputFile], stdin=None, stdout=stdoutFile, stderr=stderrFile, cwd=currentWorkingDirectory)
        if returnCode != 0:
            print 'Script failed - not moving any artifacts!'
            print 'STDERR of post processing script was: '
            # TODO: add output of stderr
            print 'Failed!! \n\n\n'
            return
    else:
        # no post processing defined, intermediate file is final file, move it to output directory
        print 'No post processing script defined.'
        outputFile = intermediateFile
        finalFile = getFinalFile(inputFile, template)

    print 'Copying to final file -> ' + finalFile
    createDir(outputDirectory + template['name'] + '/')
    print 'copying ' + outputFile + ' to ' + finalFile
    copyfile(outputFile, finalFile)
    print 'Success!! \n\n\n'
    return


# Preparation method that copies all necessary files into the working directory
def setupBuildEnv():
    deleteThenCreateDir(workingDirectory)
    deleteThenCreateDir(outputDirectory)


def getIntermediateFile(input, template):
    return workingDirectory + template['name'] + '/' + input['outputfile'] + '_' + template['name'] + '.' + template['intermediate_extension']

def getPostScript(template):
    global workingDirectory
    return baseDirectory + template['post_processing']['script']

def getOutputFile(input, template):
    global workingDirectory
    if 'post_processing' in template:
        return workingDirectory + template['name'] + '/' + input['outputfile'] + '_' + template['name'] + '.' + template['post_processing']['final_extension']
    else:
        return workingDirectory + template['name'] + '/' + input['outputfile'] + '_' + template['name'] + '.' + template['intermediate_extension']

def getFinalFile(input, template):
    if 'prefix' in template:
        prefix = template['prefix']
    else:
        prefix = ''
    global outputDirectory
    if 'post_processing' in template:
        return outputDirectory + template['name'] + '/' + prefix + input['outputfile'] + '_' + template['name'] + '.' + template['post_processing']['final_extension']
    else:
        return outputDirectory + template['name'] + '/' + prefix + input['outputfile'] + '_' + template['name'] + '.' + template['intermediate_extension']


def createDir(directoryName):
    # TODO: add check for trailing /
    print 'Checking for ' + directoryName
    directory = os.path.dirname(directoryName)
    if not os.path.exists(directory):
        print 'Creating ' + directoryName
        os.makedirs(directory)


def deleteThenCreateDir(directoryName):
    # TODO: add check for trailing /
    print 'Checking for ' + directoryName
    directory = os.path.dirname(directoryName)
    if os.path.exists(directory):
        rmtree(directory)

    print 'Creating ' + directoryName
    os.makedirs(directory)

if __name__ == "__main__":
    main(sys.argv[1:])