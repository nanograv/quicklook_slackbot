import slack, os, json, time
from pathlib import Path
#from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

env_path = Path('.') / '.env'
load_dotenv(dotenv_path = env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

bad_ql_db = "bad_quicklook_db.txt"

client = slack.WebClient(token = os.environ['SLACK_TOKEN'])

BOT_ID = client.api_call("auth.test")['user_id']

admins = ['Michael Lam', 'Joe Swiggum']

admin_uid = []

for member in client.users_list().data['members']:
    
    if member.get('real_name') in admins:
        admin_uid.append(member.get('id'))

@slack_event_adapter.on('reaction_added')
def react_to_reaction(payload):
    
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    reaction = event.get('reaction')
    
    #Get the "item" from payload which contains metadata of message on which emoji is placed
    item = event.get('item', {})
    
    if len(item) == 0:
        return None

    og_msg_ts = item.get('ts')
    og_msg_channel_id = item.get('channel')
    
    reaction_data = client.reactions_get(channel = og_msg_channel_id, timestamp = og_msg_ts)
    
    react_info = reaction_data.data.get('message').get('reactions')
    
    for ii, reacts in enumerate(react_info):
        
        react_name = reacts.get('name')
        react_count = reacts.get('count')
        
        if react_name == 'white_check_mark' and react_count >= 3:
            
            #time.sleep(3)
            
            for ff in client.conversations_history(channel = 'C022WHE4ECC').data['messages']:
                
                if ff['ts'] == og_msg_ts and ff.get('files') is not None:
                    print("YAYAY")
                    client.files_delete(file = ff.get('files')[0].get('id'))
                    
            client.chat_delete(channel = og_msg_channel_id, ts = str(og_msg_ts))
            
            break
            
        #client.chat_postMessage(channel = og_msg_channel_id, thread_ts = str(og_msg_ts), 
        #                        text = f":{reacts.get('name')}:" * reacts.get("count"))
    

@app.route('/help', methods=['POST'])
def helpp():
    
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    
    help_text = r"""Hello! Here's what you're supposed to do:
    1) If the quicklook plot looks fine, add a green check mark (no bot response)
    2) If the quicklook plot looks iffy, consult with others, or if you're an expert and confident of your opinion, do the following:
    /flag psr_name MJD reason
    3) Move on to the next plot.
    4) If you have second thoughts about that plot you flagged and want to revoke the flag, do:
    /unflag psr_name MJD
    
    Happy quicklooking! Beep-boop :robot_face:"""

    client.chat_postMessage(
        channel = user_id, text = help_text)
    
    return Response(), 200

@app.route('/flag', methods=['POST'])
def flag():
    
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    
    ip_text = data.get('text')
    
    with open(bad_ql_db, 'a') as ff:
        ff.write(ip_text + '\n')
        
    op_text = r"""Success! :robot_face:
    Here's what <@{}> flagged:
    {}
    To unflag, use /unflag psr_name mjd
    Tagging admins for review:
    """.format(user_id, ip_text)
    
    for uid in admin_uid:
        op_text += '<@{}> '.format(uid)
    
    client.chat_postMessage(
        channel=channel_id, text = op_text)
    
    return Response(), 200

@app.route('/unflag', methods=['POST'])
def unflag():
    
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    
    ip_text = data.get('text')
    
    ip_psr, ip_mjd = ip_text.split(' ')
    
    with open(bad_ql_db, 'r') as ff:
        current_lines = ff.readlines()
    
    new_lines = []
    for ii, ll in enumerate(current_lines):
        sp_ll = ll.split(' ')
        psr = sp_ll[0]
        mjd = sp_ll[1]
        
        if (ip_psr == psr) and (ip_mjd == mjd):
            continue
        else:
            new_lines.append(ll)
    
    with open("temp.txt", 'w') as ff:
        for ll in new_lines:
            ff.write(ll)
        
    os.replace("temp.txt", bad_ql_db)
        
    op_text = r"""Success! :robot_face:
    Here's what <@{}> unflagged:
    {}
    To flag, use /flag psr_name mjd comment
    """.format(user_id, ip_text)
    
    client.chat_postMessage(
        channel=channel_id, text = op_text)
    
    return Response(), 200


app.run(debug = True)
