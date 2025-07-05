import sys
import os
from shutil import rmtree, copytree

# external packages
import chevron
import mistune
import yaml

# Test chevron
def renderTemplate(tName, tPath, pDict):
    # Die if template can't be slurped.
    tFile = f"{tPath}/{tName}.html"
    try:
        with open(f"{tFile}", 'r') as f:
            template = f.read()
    except Exception as e:
        print(f"Unable to read template file: '{tFile}'!")
        print(f"ERROR: {e}")
        sys.exit(1)

    # Build the argument dict.
    args = {
        'template': template,

        # defaults to .
        'partials_path': tPath,

        # defaults to mustache
        'partials_ext': 'html',

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
    print(pgPath)
    try:
        with open(pgPath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"ERROR: Unable to read page at {pgPath}")
        print(f"ERROR: {e}")

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

    meta["content"] = content

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



def main(pub=False):
    # First, load the config file
    try:
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print("ERROR: Unable to load 'config.yml'!")
        print("Please make sure the file exists and contains valid YAML")

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

    # Collect and process the page files
    pages = scanPageDir('dest', config)

    # Sort the pages by date
    def getDate(page):
        return page['date']

    pages = sorted(pages, key=getDate, reverse=True)
    print(pages)

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
