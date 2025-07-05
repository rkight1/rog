import sys

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


def main():
    # First, load the config file
    try:
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print("ERROR: Unable to load 'config.yml'!")
        print("Please make sure the file exists and contains valid YAML")



    pDict = {
        'site': config,
        'page': {
            'title': "Lots of stuff",
            'content': "There's a lot of stuff here!"
        }
    }

    print(renderTemplate('default', 'templates', pDict))

main()
