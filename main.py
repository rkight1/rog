import sys

# external packages
import chevron


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

pDict = {
    'site': {
        'name': "My site!"
    },
    'page': {
        'title': "Lots of stuff",
        'content': "There's a lot of stuff here!"
    }
}

print(renderTemplate('default', 'templates', pDict))
