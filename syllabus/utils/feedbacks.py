class Feedback(object):
    def __init__(self, feedback_type, message):
        self.type = feedback_type
        self.message = message
        self.alert_color = "success" if self.type == "success" else "danger"
        self.icon = "fa-check" if self.type == "success" else "fa-times"
        self.title = "Success !" if self.type == "success" else "Error."

    def __dict__(self):
        return {"type": self.type, "message": self.message}

    @staticmethod
    def from_dict(feedback_dict):
        if feedback_dict is not None:
            return Feedback(feedback_type=feedback_dict["type"], message=feedback_dict["message"])
        return None


def set_feedback(session, feedback):
    """ adds the feedback to the session """
    session["feedback"] = feedback.__dict__()


def has_feedback(session):
    """ returns True if there is a feedback in the session, False otherwise """
    return "feedback" in session


def get_feedback(session):
    """ returns the current feedback in the specified session if there is one, None otherwise """
    try:
        return Feedback.from_dict(session.get("feedback", None))
    except:
        return None


def pop_feeback(session):
    """ returns and removes the current feedback from the specified session if there is one, None otherwise """
    return Feedback.from_dict(session.pop("feedback", None))
