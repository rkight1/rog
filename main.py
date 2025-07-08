import sys
import os
import re
from shutil import rmtree, copytree
from datetime import datetime

# external packages
import chevron
import mistune
import yaml

# Test chevron
def renderTemplate(tName, tPath, pDict):
    # Die if template can't be slurped.
    tFile = f"{tPath}/{tName}.ms"
    try:
        with open(f"{tFile}", 'r') as f:
            template = f.read()
    except Exception as e:
        print(f"ERROR: Unable to read template file: '{tFile}'!")
        print(f"ERROR: {e}")
        sys.exit(1)

    # Build the argument dict.
    args = {
        'template': template,

        # defaults to .
        'partials_path': tPath,

        # defaults to mustache
        'partials_ext': 'ms',

        'data': pDict
    }

    # ./partials/thing.ms will be read and rendered
    return chevron.render(**args)


# Split pages into meta and content halfs
def splitPage(content):
    parts = content.split("\n+++\n")

    return [parts[0].strip(), parts[1].strip()]


# Slurp a page and build a dict of page data. Also
# validates the page to ensure required keys exist.
def scanPage(pgPath, config):
    # print(pgPath)
    try:
        with open(pgPath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Unable to read page at {pgPath}")
        print(f"ERROR: {e}")
        print(sys.exit(1))

    parts = splitPage(content)

    meta = yaml.safe_load(parts[0])
    content = parts[1]

    # At a bare minimum, all pages need a date and a title
    if "title" not in meta:
        print(f"ERROR: Page at '{pgPath}' has no TITLE!")
        sys.exit(1)

    if "date" not in meta:
        print(f"ERROR: Page at '{pgPath}' has no DATE!")
        sys.exit(1)

    # Other keys can have default values
#    if "tags" not in meta:
#        meta["tags"] = []
#
    if "template" not in meta:
        meta["template"] = "default"

    # Every page needs a url and an output path
    outfile = pgPath.replace('.md', '.html', 1)
    outfile = outfile.replace('src', 'dest', 1)
    url = outfile.replace('dest', config['baseUrl'])
    meta["url"] = url
    meta["outfile"] = outfile
    meta['outpath'] = os.path.dirname(outfile)

    # Also need the IN PATH to figure out which file to delete.
    meta['infile'] = pgPath

    meta["content"] = mistune.html(content)

    return meta


def getFiles(dirPath):
    fileList = []
    for (root,dirs,files) in os.walk(dirPath,topdown=True):
        for f in files:
            fileList.append(f"{root}/{f}")

    return fileList


def scanPageDir(dirPath, config):
    allFiles = getFiles(dirPath)
    pages = []

    for a in allFiles:
        if a.endswith(".md"):
            pDict = scanPage(a, config)
            pages.append(pDict)

    return pages


def writePage(page, pageList, site):
    #print(page)
    #print("---")
    # Build the page data dictionary
    templateData = {
        'site': site,
        'page': page,
        'allPages': pageList
    }

    # Generate the final output
    output = renderTemplate(page['template'], 'templates', templateData)

    # Create the output directory if it doesn't exist.
    if not os.path.isdir(page['outpath']):
        try:
            os.makedirs(page['outpath'])
        except Exception as e:
            print(f"ERROR: Unable to create output dirrctory: '{page['outpath']}'")
            print(f"ERROR: {e}")
            sys.exit(1)

    # Try to write the final output
    try:
        with open(page['outfile'], 'w') as f:
            f.write(output)

    except Exception as e:
        print(f"ERROR: Unable to write output file: '{page['outfile']}'!")
        print(f"ERROR: {e}")
        sys.exit(1)


def getPagesPropertyEquals(pageList, prop, value, config):
    """Works like getPagesWithProperty, except that instead of gathering pages that have a given property, it gathers pages where PROPERTY = VALUE. This function DOES NOT generate a tree-like data structure, only a list of page dictionaries.

    This can be used to generate a list of blog ppsts, project pages, etc."""

    # Get a list of pages that have the property.
    foundPages = []
    #print(f"Looking for {prop}, value {value}")
    for p in pageList:
        if prop in p:
            #print(f"Found {prop}, value {p[prop]}")
            if p[prop] == value:
                foundPages.append(p)

    return foundPages


def getPagesWithProperty(pageList, prop, config):
    """Takes a list of page dictionaries, a property (eg. tags, category), and a site dictionary. Generates a collection of tree-like structures representing a ROOT PAGE for each property (yoursite.com/<prop>) and a list of pages for each unique value (yoursite.com/<prop>/[pv1, pv2, etc]).

    This can be used to generate pages for each tag, category, etc.
    """

    # Get a list of pages that have the property.
    propPages = []
    for pg in pageList:
        if prop in pg:
            propPages.append(pg)


    # Collect the property values.
    propValues = []

    for pg in propPages:
        val = pg[prop]

        # If the value is a list, iterate over it.
        if isinstance(val, list):
            for item in val:
                propValues.append(item)
        # If it's a string, append it as is.
        elif isinstance(val, str):
            propValues.append(val)
        else:
            print("WARNING: Property '{prop}' of page with title: {pg['title']} is neither a string nor a list. Skipping.")

    # Remove duplicate values
    propValues = list(set(propValues))

    newCollection = {
        'name': prop,
        'pages': [propPages],
        'values': []
    }

    for pv in propValues:
        newValueDict = {
            'name': pv,
            'pages': []
        }
        for pg in propPages:

            # Once again, we have to distringuish between string and array
            if isinstance(pg[prop], list):
                for item in pg[prop]:
                    if item == pv:
                        newValueDict['pages'].append(pg)
            elif isinstance(pg[prop], str):
                if pg[prop] == pv:
                    newValueDict['pages'].append(pg)

        newCollection['values'].append(newValueDict)

    return newCollection


def genPropertyValuePages(collection, template, config):
    """Generate a list of page dictionaries for each key in a page collection. For example, if getPagesWithProperty() is used to get all pages with a 'tags' property, this function can take that collection and generate pages dictionaries for 'tags/tag1.html', 'tags/tag2.html', etc.

    Requires:
    collection - A nested key/value data structure returned by getPagesWithProperty().
    template   - The name of the template file to use. Will be resolved to 'templates/<template>.ms'.
    config     - Main site configuration dictionary. Required to set the URL of the new page.
    """

    colName = collection['name']

    # File names can't have special characters.
    colNameCleaned = cleanString(colName)

    # Make property pages.
    pageList = []
    for t in collection['values']:
        valName = t['name']
        valPages = t['pages']

        # File names can't have special characters.
        valNameCleaned = cleanString(valName)

        # Next, create the page
        outfile = f"dest/{colNameCleaned}/{valNameCleaned}.html"
        url = outfile.replace('src', config['baseUrl'])
        pDict = {
            'title': valName,
            'date': datetime.now(),
            'template': template,
            'content': "",
            'collectionPages': valPages,
            'collectionName': valName,
            'outfile': outfile,
            'outpath': os.path.dirname(outfile),
            'url': url
        }

        # Append the newly created page.
        pageList.append(pDict)

    return pageList



def cleanString(string):
    # Convert special characters to 'x'
    pattern = r'[^A-Za-z0-9 ]'
    newStr = re.sub(pattern, "x", string)

    # Convert spaces to underscores to make them more filename friendly.
    newStr = newStr.replace(" ", "_")

    return newStr


def main(pub=False):
    # First, load the config file
    try:
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print("ERROR: Unable to load 'config.yml'!")
        print("Please make sure the file exists and contains valid YAML.")
        sys.exit(1)

    # If we're not publishing, fix the URL
    if not pub:
        config['baseUrl'] = config['testUrl']

    # Remove dest if already exist
    if os.path.isdir('dest'):
        try:
            rmtree('dest')
        except Exception as e:
            print("ERROR: Unable to clean DEST!")
            print(f"ERROR: {e}")
            sys.exit(1)

    # Make the output directory
    os.makedirs('dest')

    # Copy static assets
    if os.path.isdir('static'):
        try:
            copytree('static', 'dest')
        except Exception as e:
            print("ERROR: Unable to copy STATIC ASSETS to DEST!")
            print(f"ERROR: {e}")
            sys.exit(1)

    # Collect and process the page files
    pages = scanPageDir('src', config)

    # Sort the pages by date
    def getDate(page):
        return page['date']

    allPages = sorted(pages, key=getDate, reverse=True)


    # Process collections
    for c in config['collections']:
        col = config['collections'][c]

        if 'hasProperty' in col:
            prop = col['hasProperty']
            col['pages'] = getPagesWithProperty(allPages, c, config)
            #print(col['pages'])

            # Generate pages for each property and add them to allPages.
            propertyValuePages = genPropertyValuePages(col['pages'], col['template'], config)
            #print(propertyValuePages)

            for pvp in propertyValuePages:
                allPages.append(pvp)

        elif 'propertyEquals' in col:
            prop = col['propertyEquals']['property']
            val = col['propertyEquals']['value']
            print(f"PROP: {prop} / VAL: {val}")
            col['pages'] = getPagesPropertyEquals(allPages, prop, val, config)


    print("Collections")
    for c in config['collections']:
        print(f"Col name: {c}")
        col = config['collections'][c]
        print("Properties:")
        for p in col:
            print(p)
            print(col[p])
        print("---")



#    # Attach the tag pages to config
#    config['collections'] = {}
#    config['collections']['tags'] = getPagesWithProperty(allPages, 'tags', config)
#
#    allTagPages = genPropertyValuePages(config['collections']['tags'], "tagPage", config)
#
#    for tp in allTagPages:
#        allPages.append(tp)

    #print(allTagPages['values'])

    # Write all of the pages.
    for p in allPages:
        writePage(p, allPages, config)


    # Generate the stylesheet
    css = renderTemplate('style', 'templates', {'site': config})
    try:
        with open('dest/style.css', 'w') as f:
            f.write(css)

    except Exception as e:
        print(f"ERROR: Unable to write file: 'dest/style.css'!")
        print(f"ERROR: {e}")
        sys.exit(1)


    # Test code
#    pDict = {
#        'site': config,
#        'page': {
#            'title': "Lots of stuff",
#            'content': "There's a lot of stuff here!"
#        }
#    }
#
#    print(renderTemplate('default', 'templates', pDict))
#
#    # scanPage test
#    print(scanPage('src/index.md'))
#
#    print(getFiles('src'))

main()
