import os
import sys
import subprocess
import traceback
import logging
import json
import time
import threading
import pycron
from dotenv import dotenv_values

from models.loadedapp import *

def venv_python_path() -> str: 
    return os.path.join('.apprunnervenv', 'Scripts' if os.name == 'nt' else 'bin', 'python')

def run(app: LoadedApp):
    env = dotenv_values(os.path.join(app.fullPath, '.env'))
    output_file = open(os.path.join(app.fullPath, '.apprunner.log'), 'w')
    app_call = subprocess.run(args=[venv_python_path(), app.entrypoint],
                          cwd=app.fullPath,
                          env=env,
                          stdout=output_file,
                          stderr=output_file,
                          shell=True)
    output_file.close()
    if (app_call.returncode != 0):
        logger.warning(f'App {app.directoryName} exited with error code {app_call.returncode}')

logger = logging.getLogger('AppRunner')
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

base_directory = os.environ.get('APP_DIRECTORY') if os.environ.get('APP_DIRECTORY') else '.testing-directory'
data_file_name = '.apprunnerdata.json'

loadedApps: "list[LoadedApp]" = []

if (os.name != 'nt' and not os.access(base_directory, os.W_OK | os.X_OK)):
    logger.warning(f'App directory is not writable!')

# Load data
for pathname in os.listdir(base_directory):
    fullpath = os.path.join(os.path.abspath(base_directory), pathname)
    if os.path.isdir(fullpath):
        app_datafile = os.path.join(fullpath, data_file_name)
        if not os.path.exists(app_datafile):
            logger.warning(f'App path {pathname} does not contain data file, skipping')
            continue
        logger.info(f'Found canidate app path {pathname}')
        try:
            app = LoadedApp()
            app.directoryName = pathname
            app.fullPath = fullpath
            data = json.load(open(app_datafile))
            app.schedule = data['schedule']
            app.entrypoint = data['script']
            app.hasRequirements = os.path.exists(os.path.join(fullpath, 'requirements.txt'))
            app.hasEnv = os.path.exists(os.path.join(fullpath, '.env'))
            loadedApps.append(app)

            logger.debug(f'Lodaded app data')
        except Exception as e:
            logger.error(f'Failed to load app data in path {pathname}')
            traceback.print_exc()
            exit(1)

# Do setup
for app in loadedApps:
    try:
        logger.info(f'Preparing app {app.directoryName}')

        #Check for writability
        if (os.name != 'nt' and not os.access(app.directoryName, os.W_OK | os.X_OK)):
            logger.warning(f'App path {app.directoryName} is not writable!')

        #create and activate venv
        logger.debug('Creating venv...')
        subprocess.call(args=['python', '-m', 'venv', '.apprunnervenv'], cwd=app.fullPath)
        #mark script as executable
        if (os.name != 'nt'):
            logger.debug('Marking script as executable to ensure it runs...')
            subprocess.call(args=['chmod', '+x', app.entrypoint], cwd=app.fullPath)
            if (not os.access(os.path.join(app.fullPath, app.entrypoint), os.X_OK)):
                logger.error(f'App excutable for app {app.directoryName} is not executable! Skipping app setup, app will not run')
                loadedApps.remove(app)
                continue
        #install requirements if needed
        if (app.hasRequirements):
            logger.debug('Installing requirements...')
            subprocess.call(args=[venv_python_path(), '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=app.fullPath, start_new_session=True)
        
        logger.info(f'Finished preperation for app {app.directoryName}')
    except Exception as e:
        logger.error(f'Failed to prepare app {pathname}')
        traceback.print_exc()
        exit(1)

# Loaded, print debug data
logger.info('Loaded successfully!')
logger.info('The following apps have been loaded:')
for app in loadedApps:
    logger.info(f'* {app.directoryName} with schedule {app.schedule}')

# Run the apps
while 1:
    for app in loadedApps:
        if (pycron.is_now(app.schedule)):
            thread = threading.Thread(target=run, args=(app, ))
            thread.start()
    time.sleep(60)