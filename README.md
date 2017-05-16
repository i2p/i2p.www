# I2P website

To run locally (for testing purposes):

- Install proxychains, configure it for Tor

- Pull in the dependencies:

    ```
    $ proxychains ./setup_venv.sh
    ```

    (you can also pull them non-anon by leaving out proxychains)

- Compile translations (if you want to see them):

    ```
    $ ./compile-messages.sh
    ```

- Start the webserver:

    ```
    $ ./runserver.py
    ```

- Open the site at http://localhost:5000/

## Running a mirror

If you want to mirror the I2P website, thanks! Here is a checklist:

- Do not edit any of the files in `i2p2www/` 
  - In particular, do not change the `CANONICAL_DOMAIN` variable in
    `i2p2www/__init__.py`, it needs to point to the official site for SEO.
- If you need to edit variables in `etc/update.vars`, copy the file to
  `etc/update.vars.custom` and edit appropriately. The only variable you
  may need to edit is `MTNURL` in `etc/update.vars` (if your Monotone client
  tunnel is listening on a different port).
- If you want to enable caching, copy `i2p2www/settings.py.sample` to
  `i2p2www/settings.py` and edit appropriately.
- Add `./site-updater.sh` to your crontab. This will keep the site updated,
  recompile the translations when necessary, and touch a file in `/tmp/`
  (look in `etc/update.vars` for the filename, your webserver should restart
  WSGI when the timestamp of this file changes).

## Configuration

Configuration files for the various scripts are in `etc/`. Environment variables
in `etc/translation.vars` can be overridden by creating the file
`etc/translation.vars.custom` and re-defining the environment variables there.

## Updating translations

1. Pull new and updated translations from Transifex:

    ```
    $ tx pull -a
    ```

2. Correctly format the translations:

    ```
    $ ./update-existing-po.sh
    ```

3. Check in the updated translations:

    ```
    $ mtn ci i2p2www/translations/ -m "Updated translations"
    ```

4. Check in any new translations:

    ```
    $ mtn add -R i2p2www/translations/ && mtn ci i2p2www/translations/ -m "New translations"
    ```

5. Update the POT files with any changes to the website text:

    ```
    $ ./extract-messages.sh
    ```

6. Update the translations with any changes to the website text:

    ```
    $ ./update-existing-po.sh
    ```

7. Check in any changes to the website text:

    ```
    $ mtn ci pots/ i2p2www/translations/ -m "Updated translation strings"
    ```

8. Push website text changes to Transifex:

    ```
    $ tx push -s
    ```
