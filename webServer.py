from flask import Flask, request
from talkWithMQTT import MqttWork
import json
import time
import settings as config

class WebServer:
    app = Flask(__name__)

    @app.route("/webhook", methods=['GET'])
    def verify():
        """webhook api"""
        return request.args.get('hub.challenge')

    # get json from request and send it to broker
    @app.route('/webhook', methods=['POST'])
    def post_json():
        message = {}
        if request.is_json:
            content = request.get_json()
            #print the request that came from facebook
            print('content:\n', content)

            # if the changes was the like
            if content['entry'][0]['changes'][0]['value']['item'] == 'like':
                # get the time from the request
                #converting epoch time to datetime
                epoch_time = int(content['entry'][0]['time'])
                human_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_time))
                # also get the sender id
                message = {'time': human_time,
                           'type': 'LIKE',
                           'sender_id': content['entry'][0]['changes'][0]['value']['sender_id']
                           }

                # print the message that will be send to broker
                print('message:\n', json.dumps(message))

                # send message to mqtt broker
                with MqttWork() as mqtt:
                    mqtt.publish(topic=config.MQTT_FB_WEBHOOK_TOPIC_NAME, message=(json.dumps(message)))

        resp = ('got from request\n %s') % content + ('\n\nsend to broker:\n%s' % message)
        print(resp)
        return resp

    @app.route('/')
    def api_root():
        return 'welcome'
