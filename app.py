# app.py
#
# Use this sample code to handle webhook events in your integration.
#
# 1) Paste this code into a new file (app.py)
#
# 2) Install dependencies
#   pip3 install flask
#   pip3 install stripe
#
# 3) Run the server on http://localhost:4242
#   python3 -m flask run --port=4242

import json
import os
import stripe
import firebase_admin
from firebase_admin import auth
from firebase_admin import db
from flask import Flask, jsonify, request

import firebase_admin
from firebase_admin import credentials


cred = credentials.Certificate("supllynvest-firebase-adminsdk-rtfc7-8f8535a9db.json")
firebase_admin.initialize_app(cred,{'databaseURL':'https://supllynvest-default-rtdb.firebaseio.com/'})
ref = db.reference('users') 


#user = auth.get_user(uid)

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = 'whsec_a39a283ec4df25eabc698c6207eb158c73bb04d629d2d68e97c499883b95fa87'

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    if event['type'] == 'checkout.session.completed':
      session = event['data']['object']
      email= event['data']['object']['customer_details']['email']
      price = event['data']['object']['amount_total']
      price_usd = price/100
      quantity = price_usd/3 #$
      print(email)
      print(payload)
      user = auth.get_user_by_email(email)
      print(user.uid)
    # ... handle other event types
    
      uid = user.uid
      users = ref.child(str(uid)+'/supply')
      supplies= int(users.get())
      supplies += quantity
      ref.child(str(uid)).set({
        'supply': supplies
      })
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)