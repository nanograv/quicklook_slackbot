import slack, os, json, time, glob, datetime, numpy as np
from pathlib import Path
#from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

import argparse

parser = argparse.ArgumentParser(description = "Setup slackbot to report number of samples in runs")

#Required arguments:
parser.add_argument("-channel", dest = 'channel', required = True, help = "Slack channel to send the message; App MUST BE ADDED TO CHANNEL")

parser.add_argument("--datadir", default = "./", help = "Directory holding all quicklook plots (assumed to be .png)")
parser.add_argument("--run_every", type = float, dest = 'run_every', default = 12, help = "Run this code once per given number of hours; Default = 12 hours")
parser.add_argument("--interval", type = float, dest = 'interval', default = 12, help = "Check for new plots in the last given number of hours. Recommend setting it equal to --run_every; Default = 12 hour")
parser.add_argument("--cronjob", dest = 'cronjob', action = 'store_true', default = False, help = 'Flag to set whether bot is run as a Slurm/PBS job or cron job. Default: False')

parser.add_argument("--test", dest = 'test', action = 'store_true', default = False, help = "Run code only once for testing.")

args = parser.parse_args()

def was_modified(fname, interval = 60 * 60):
    """
    Function to determine whether file was modified within the time given by "interval"
    
    Input
    -----
    fname: str; Path to file
    time: float (seconds); Time interval in the past in which file was modified
    
    Returns
    -----
    was_modified: Boolean; Whether file was modified
    """
    
    statbuf = os.stat(fname)
    mod_time = statbuf.st_mtime
    current_time = time.time()
    
    if np.abs(mod_time - current_time) <= interval:
        return True
    else:
        return False
    
env_path = Path('.') / '.env'
#load_dotenv(dotenv_path = env_path)

client = slack.WebClient(token = os.environ['SLACK_TOKEN'])

BOT_ID = client.api_call("auth.test")['user_id']

datadir = args.datadir

interval = args.interval * 3600
channel = args.channel
run_every = args.run_every * 3600

if not args.cronjob:
    while True:

        ql_plots = sorted(glob.glob(datadir + '/*.png'))

        new_plots = np.array(())

        for path in ql_plots:

            if was_modified(path, interval = interval):
                new_plots = np.append(new_plots, path)

        if len(new_plots) != 0:

            init_msg = r":robot_face: INCOMING! {} :robot_face:".format(datetime.datetime.now())
            client.chat_postMessage(channel = channel, text = init_msg)

            for ii, path in enumerate(new_plots):

                fname = path.split('/')[-1]

                client.files_upload(channels = channel, file = path, 
                                    title = fname, init_comment = fname)

        if args.test:
            break
        else:
            time.sleep(run_every)
            
else:
    
    ql_plots = sorted(glob.glob(datadir + '/*.png'))

    new_plots = np.array(())

    for path in ql_plots:

        if was_modified(path, interval = interval):
            new_plots = np.append(new_plots, path)

    if len(new_plots) != 0:

        init_msg = r":robot_face: INCOMING! {} :robot_face:".format(datetime.datetime.now())
        client.chat_postMessage(channel = channel, text = init_msg)

        for ii, path in enumerate(new_plots):

            fname = path.split('/')[-1]

            client.files_upload(channels = channel, file = path, 
                                title = fname, init_comment = fname)
