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
    if "tags" not in meta:
        meta["tags"] = []

    if "template" not in meta:
        meta["template"] = "default"

    # Every page needs a url and an output path
    outpath = pgPath.replace('.md', '.html', 1)
    url = outpath.replace('dest', config['baseUrl'])
    meta["url"] = url
    meta["outpath"] = outpath

    # Also need the IN PATH to figure out which file to delete.
    meta['inpath'] = pgPath

    meta["content"] = mistune.html(content)

    return meta


def getFiles(dir):
    fileList = []
    for (root,dirs,files) in os.walk(dir,topdown=True):
        for f in files:
            fileList.append(f"{root}/{f}")

    return fileList


def scanPageDir(dir, config):
    allFiles = getFiles(dir)
    pages = []

    for a in allFiles:
        if a.endswith(".md"):
            pDict = scanPage(a, config)
            pages.append(pDict)

    return pages


def writePage(page, pageList, site):
    # Build the page data dictionary
    templateData = {
        'site': site,
        'page': page,
        'allPages': pageList
    }

    # Generate the final output
    output = renderTemplate(page['template'], 'templates', templateData)

    # Try to write the final output
    try:
        with open(page['outpath'], 'w') as f:
            f.write(output)

    except Exception as e:
        print(f"ERROR: Unable to write output file: '{p['outpath']}'!")
        print(f"ERROR: {e}")
        sys.exit(1)


def getPagesByProperty(pageList, prop, config):
    """Takes a list of page dictionaries, a property (eg. tags, category), and a site dictionary. Generates a collection of tree-like structures representing ROOT PAGE for property (yoursite.com/<prop>) and a list of pages for each unique value (yoursite.com/<prop>/[pv1, pv2, etc]).

    This can be used to generate pages for each tag, category, <insert property here>.
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

    # Copy src to dest
    try:
        copytree('src', 'dest')
    except Exception as e:
        print("ERROR: Unable to copy SRC to DEST!")
        print(f"ERROR: {e}")
        sys.exit(1)

    # Copy static assets
    if os.path.isdir('static'):
        try:
            copytree('static', 'dest')
        except Exception as e:
            print("ERROR: Unable to copy STATIC ASSETS to DEST!")
            print(f"ERROR: {e}")
            sys.exit(1)

    # Collect and process the page files
    pages = scanPageDir('dest', config)

    # Sort the pages by date
    def getDate(page):
        return page['date']

    allPages = sorted(pages, key=getDate, reverse=True)
    allTagPages = getPagesByProperty(allPages, 'tags', config)

    # Attach the tag pages to config
    config['collections'] = {}
    config['collections']['tags'] = allTagPages

    # Create the tag page directory
    try:
        os.mkdir(f"dest/tag")

    except Exception as e:
        print("ERROR: Unable to create 'dest/tag'!")
        print(f"ERROR: {e}")
        sys.exit(1)

    # Write the tag pages
    for t in allTagPages['values']:
        tagName = t['name']
        colPages = t['pages']

        # File names can't have special characters.
        tCleaned = cleanString(tagName)

        # Next, create the page
        outpath = f"dest/tag/{tCleaned}.html"
        url = outpath.replace('dest', config['baseUrl'])
        pDict = {
            'title': f"Pages tagged '{tagName}'",
            'date': datetime.now(),
            'template': "tagPage",
            'content': "",
            'collection': colPages,
            'outpath': outpath,
            'url': url
        }

        # Append it the main page list
        allPages.append(pDict)

    print(allTagPages['values'])

    # Write all of the pages.
    for p in allPages:
        writePage(p, allPages, config)

        # Not all pages will have an inpath
        if 'inpath' in p:
            # Try to remove the source MD file.
            try:
                os.remove(p['inpath'])

            except Exception as e:
                print(f"ERROR: Unable to delete input file: '{p['inpath']}'!")
                print(f"ERROR: {e}")
                sys.exit(1)

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
