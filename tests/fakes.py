class FakeTelegramClient:
    def __init__(
        self,
        admin_status="administrator",
        chat_member_error=None,
        sent_message_id=202,
    ):
        self.admin_status = admin_status
        self.chat_member_error = chat_member_error
        self.sent_message_id = sent_message_id
        self.sent_polls = []
        self.sent_messages = []
        self.chat_member_requests = []

    def get_chat_member(self, chat_id, user_id):
        self.chat_member_requests.append((chat_id, user_id))
        if self.chat_member_error:
            raise self.chat_member_error
        return {"status": self.admin_status}

    def send_poll(self, chat_id, poll):
        self.sent_polls.append((chat_id, poll))
        return {"message_id": 101}

    def send_message(self, chat_id, text):
        self.sent_messages.append((chat_id, text))
        return {"message_id": self.sent_message_id}


def group_update(text, user=None):
    return {
        "update_id": 1,
        "message": {
            "message_id": 11,
            "text": text,
            "chat": {"id": -1001, "type": "supergroup"},
            "from": user or {"id": 55, "username": "adminuser", "first_name": "Admin"},
        },
    }
