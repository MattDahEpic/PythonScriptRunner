# Python Script Runner
This container runs a set of python scripts on a schedule. I use it to run a set of "every hour" Mastodon bots and cross-social post replicator scripts. Rather than setting up a bunch of crontabs and venvs manually, I made this script that does that all for me.

Each configured script will have its dependencies automatically installed if they exist (in a `requirements.txt`) and be run on the configured schedule with their stdout/err redirected to a file for monitoring.

## Usage
1. Create a base folder and place each python file and its dependencies in a folder inside the base folder.
2. Link the base folder into /pythonapps in the container.
3. Create a `.apprunnerdata.json` file in each app folder with data in the following format:
```json
{
    "schedule": "0 0 * * *", //a cron schedule to run this script at
    "script": "app.py" //which file to run
}
```
4. Run the container, making sure to set the `TZ` environment variable to your local timezone ([List of timezones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones))

Example directory layout:
```
* Folder (linked to /pythonapps) 
  * app1
    * .apprunnerdata.json
    * app.py
    * requirements.txt
  * app2
    * .apprunnerdata.json
    * app.py
    * requirements.txt
```

## Development
docker compose up --build