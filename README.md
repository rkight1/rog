# ROG: Robert's Own Generator

## Dependencies

- Mistune
- Chevron

*(see `requirements.txt` for versions)*


## Why?

Mainly to show off what I know to potential employers/clients. Also, the vast majority of the SSG's out there right now are kind of complicated and have *way* to may features. My program only has *two* dependencies.


## Setup

1. Clone this repo.
2. Install the dependencies with `pip install -r requirements.txt`.
3. Edit the `config.yml` file to taste.
4. Edit the theme CSS (`static/style.css`) and the templates to make the site your own.
5. Replace the demo pages with your own content.
6. Run `python main.py publish`.
7. Sync the contents of the `dest` directory to your web server.


## CLI options

- `publish`: Build the site with the `baseURL` specified in `config.yml`
- `build`: Build the site with the `testURL` specified in `config.yml`
