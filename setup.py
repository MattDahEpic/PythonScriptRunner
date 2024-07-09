import os
import sys
import subprocess
import traceback
import logging
import json
from crontab import CronTab

from models.apprunnerdata import *

logger = logging.getLogger('AppRunner')
logger.setLevel(logging.DEBUG)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

cron = CronTab(user=True)

base_directory = '/pythonapps'
data_file_name = '.apprunnerdata.json'

for pathname in os.listdir(base_directory):
    fullpath = os.path.join(os.path.abspath(base_directory), pathname)
    if os.path.isdir(fullpath):
        app_datafile = os.path.join(fullpath, data_file_name)
        if not os.path.exists(app_datafile):
            logger.warning(f'App path {pathname} does not contain data file, skipping')
            continue
        logger.info(f'Found canidate app path {pathname}')
        try:
            #load runner data
            data: AppRunnerData = json.load(open(app_datafile))
            logger.debug(f'Lodaded app data: {data}')
            #create and activate venv
            logger.debug('Creating venv...')
            subprocess.call(args=['python', '-m', 'venv', '.apprunnervenv'], cwd=fullpath)
            venv_python_path = os.path.join('.apprunnervenv', 'bin/python')
            #install requirements if needed
            logger.debug('Installing requirements (if specified)...')
            if (os.path.exists(os.path.join(fullpath, 'requirements.txt'))):
                subprocess.call(args=[venv_python_path, '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=fullpath, start_new_session=True)
            #create crontab entry
            logger.debug('Adding crontab entry...')
            cron_entry = cron.new(f'cd {fullpath} && {venv_python_path} {data['script']} > "{os.path.join(fullpath, '.apprunner.log')}" 2>&1')
            cron_entry.setall(data['schedule'])

            logger.info(f'Finished setup for app path {pathname}')
        except Exception as e:
            logger.error(f'Failed to load app data in path {pathname}')
            traceback.print_exc()
            exit(1)

cron.write(user=cron.user)

# loaded, print debug data
logger.info('Loaded successfully!')
logger.debug('Started cron with following entries:')
for job in cron:
    logger.debug(job) 
