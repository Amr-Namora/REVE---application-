# notification_utils.py
import os
import requests
from exponent_server_sdk import PushClient, PushMessage
from .models import PushToken


def send_push_notification(user, title, body):
    try:
        # Retrieve the user's expo push token
        token_obj = PushToken.objects.get(user=user)
        token = token_obj.expo_push_token

        # Build the push message
        message = PushMessage(to=token, title=title, body=body)

        # Check if an Expo token is provided (i.e., push security is enabled)
        expo_token = os.getenv("EXPI want to ask O_TOKEN")
        if expo_token:
            # Create a requests session that includes the required headers
            session = requests.Session()
            session.headers.update({
                "Authorization": f"Bearer {expo_token}",
                "accept": "application/json",
                "accept-encoding": "gzip, deflate",
                "content-type": "application/json"
            })
            PushClient(session=session).publish(message)
        else:
            # If no Expo token is provided, try publishing without authentication header
            PushClient().publish(message)

        return {"status": "Success"}
    except PushToken.DoesNotExist:
        return {"error": "User has no push token"}
    except Exception as e:
        # Catch any other exceptions and return their messages.
        return {"error": str(e)}
