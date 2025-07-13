import sys
import os
import re
from shutil import rmtree, copytree
from datetime import datetime

# external packages
import chevron
import mistune
import yaml


# !! DO NOT TOUCH UNLESS YOU KNOW WHAT YOU'RE DOING !!
SRC = 'src'
DEST = 'dest'

# Chevron rendering function
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
    print(content)
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
    outfile = outfile.replace(SRC, DEST, 1)
    url = outfile.replace(DEST, config['baseUrl'])
    meta["url"] = url
    meta["outfile"] = outfile
    meta['outpath'] = os.path.dirname(outfile)

    # Also need the IN FILE to figure out which file to delete.
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

    # Fix collection links
    for prop in page:
        propVal = page[prop]
        print(f"Check page prop: {prop}")
        if prop in site['collections']:
            print(f"{prop} is in site collections")
            if isinstance(propVal, list):
                plist = propVal
                if 'valuePages' in site['collections'][prop]:
                    vpages = site['collections'][prop]['valuePages']

                    for v in vpages:
                        for idx, p in enumerate(plist):
                            if v['collectionName'] == p:
                                page[prop][idx] = v
            else:
                print(f"Property value: {page[prop]}")
                print(f"Collection value: {site['collections'][prop]}")



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
    """Works like genCollectionFromProperty, except that instead of gathering pages that have a given property, it gathers pages where PROPERTY = VALUE. This function DOES NOT generate a tree-like data structure, only a list of page dictionaries.

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


def genPropertyValuePages(collection, template, config):
    """Used by genCollectionFromProperty() to generate a list of page dictionaries for each key in a collection. For example, if the collection is 'tags', this function generates pages dictionaries for 'tags/tag1.html', 'tags/tag2.html', etc.

    Requires:
    collection - A nested key/value data structure returned by genCollectionFromProperty().
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
        outfile = f"{DEST}/{colNameCleaned}/{valNameCleaned}.html"
        url = outfile.replace(DEST, config['baseUrl'], 1)
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


def genCollectionFromProperty(config, pageList, prop, propValueTemplate, rootTitle, rootTemplate):
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

    # Generate a new collection
    newCollection = {
        'name': prop,
        'pages': propPages,
        'values': []
    }

    for pv in propValues:
        newValueDict = {
            'name': pv,
            'pages': []
        }
        for pg in propPages:

            # Once again, we have to distinguish between strings and arrays.
            if isinstance(pg[prop], list):
                for item in pg[prop]:
                    if item == pv:
                        newValueDict['pages'].append(pg)
            elif isinstance(pg[prop], str):
                if pg[prop] == pv:
                    newValueDict['pages'].append(pg)

        newCollection['values'].append(newValueDict)

    # Generate and add pages for each property.
    pvPages = genPropertyValuePages(newCollection, propValueTemplate, config)
    newCollection['valuePages'] = pvPages

    # Finally, generate the ROOT page for the collection
    outfile = f"{DEST}/all{prop}.html"
    url = outfile.replace(DEST, config['baseUrl'], 1)
    newCollection['rootPage'] = {
        'title': rootTitle,
        'date': datetime.now(),
        'template': rootTemplate,
        'content': "",
        'outfile': outfile,
        'outpath': os.path.dirname(outfile),
        'url': url
    }

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
    if os.path.isdir(DEST):
        try:
            rmtree(DEST)
        except Exception as e:
            print(f"ERROR: Unable to clean {DEST}!")
            print(f"ERROR: {e}")
            sys.exit(1)

    # Copy SRC to DEST to scoop up any page assets (images, sample files, etc.)
    copytree(SRC, DEST)

    # Collect and process the page files.
    # NOTE: Remember that we copy the pages to DEST and SCAN DEST! DO NOT SCAN SRC! If you do, then all generated page dictionaries will have an 'infile' value starting with SRC, which cause the pages to be deleted from SRC instead of DEST.
    pages = scanPageDir(DEST, config)

    # Sort the pages by date
    def getDate(page):
        return page['date']

    allPages = sorted(pages, key=getDate, reverse=True)


    # Convert dates to preferred format
    for p in allPages:
        dString = p['date'].strftime(config['dateFormat'])
        p['date'] = dString


    # Process collections
    # Use a list to store collection ROOT pages that should be added to the main site menu.
    rootMenuPages = []
    for c in config['collections']:
        col = config['collections'][c]

        if 'hasProperty' in col:
            # Ensure a sensible title.
            if 'rootTitle' in col:
                title = col['rootTitle']
            else:
                title = c

            addToMenu = False
            if 'addToMenu' in col:
                if col['addToMenu']:
                    addToMenu = True

            # Make sure we have templates!
            if 'propValueTemplate' not in col:
                print(f"ERROR: Collection {c} has no 'propValueTemplate'!")
                sys.exit(1)

            if 'rootTemplate' not in col:
                print(f"ERROR: Collection {c} has no 'rootTemplate'!")
                sys.exit(1)

            prop = col['hasProperty']

            # Generate a new collection.
            newCol = genCollectionFromProperty(config, allPages, c, col['propValueTemplate'], title, col['rootTemplate'])
            #print(col['pages'])

            # Attach the new collection.
            config['collections'][c] = newCol

            # Add the value pages to the main page list for rendering.
            for pvp in config['collections'][c]['valuePages']:
                allPages.append(pvp)

            # And the ROOT page of the collection.
            allPages.append(newCol['rootPage'])

            # Add to menu if requests.
            if addToMenu:
                rootMenuPages.append(newCol['rootPage'])

        elif 'propertyEquals' in col:
            prop = col['propertyEquals']['property']
            val = col['propertyEquals']['value']
            print(f"PROP: {prop} / VAL: {val}")
            col['pages'] = getPagesPropertyEquals(allPages, prop, val, config)


    if 'menu' in config['collections']:
        for m in rootMenuPages:
            config['collections']['menu']['pages'].append(m)

    print("Collections")
    for c in config['collections']:
        print(f"Col name: {c}")
        col = config['collections'][c]
        print("Properties:")
        for p in col:
            print(p)
            print(col[p])
        print("---")


    # Write all of the pages.
    for p in allPages:
        writePage(p, allPages, config)

        # NOTE: Since we're copying everything from SRC to DEST, remove the input files from dest.
        if 'infile' in p:
            os.remove(p['infile'])


    # Copy static assets
    if os.path.isdir('static'):
        try:
            copytree('static', DEST, dirs_exist_ok=True)
        except Exception as e:
            print(f"ERROR: Unable to copy STATIC ASSETS to {DEST}!")
            print(f"ERROR: {e}")
            sys.exit(1)

#    # Generate the stylesheet
#    css = renderTemplate('style', 'templates', {'site': config})
#    try:
#        with open(f"{DEST}/style.css", 'w') as f:
#            f.write(css)
#
#    except Exception as e:
#        print(f"ERROR: Unable to write file: '{DEST}/style.css'!")
#        print(f"ERROR: {e}")
#        sys.exit(1)


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


def printHelp():
    print("Supported options are:")
    print("publish - Builds the site with 'baseUrl' from config.yml.")
    print("build   - Builds the site with 'testUrl' from config.yml.")

if __name__ == "__main__":
    #main()
    print(sys.argv)

    if len(sys.argv) == 2:
        if sys.argv[1] == "publish":
            main(pub=True)
        elif sys.argv[1] == "build":
            main()
    else:
        printHelp()
