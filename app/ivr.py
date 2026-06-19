from flask import Blueprint, request, current_app
from app.extensions import db, redis_client
from app.models import CallLog

ivr_bp = Blueprint("ivr", __name__, url_prefix="/ivr")

MENU_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <GetInput action="/ivr/handle-input" inputType="dtmf" digitEndTimeout="5" numDigits="1" retries="1" redirect="true">
    <Speak>Welcome. Press 1 for Sales. Press 2 for Support. Press 3 to hear your number read back.</Speak>
  </GetInput>
</Response>"""

GOODBYE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Speak>You have reached the maximum number of retries. Goodbye.</Speak>
  <Hangup/>
</Response>"""


def _log_call(call_uuid, from_number, to_number, selection, status):
    entry = CallLog(
        call_uuid=call_uuid,
        from_number=from_number,
        to_number=to_number,
        menu_selection=selection,
        call_status=status,
    )
    db.session.add(entry)
    db.session.commit()


def _speak_xml(text):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Speak>{text}</Speak>
</Response>"""


def _xml_response(xml_string):
    from flask import Response
    return Response(xml_string, content_type="text/xml")


@ivr_bp.route("/welcome", methods=["POST"])
def welcome():
    base = request.url_root.rstrip("/")
    menu_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <GetInput action="{base}/ivr/handle-input" inputType="dtmf" digitEndTimeout="5" numDigits="1" retries="1" redirect="true">
    <Speak>Welcome. Press 1 for Sales. Press 2 for Support. Press 3 to hear your number read back.</Speak>
  </GetInput>
</Response>"""
    return _xml_response(menu_xml)


@ivr_bp.route("/handle-input", methods=["POST"])
def handle_input():
    call_uuid = request.form.get("CallUUID", "unknown")
    from_number = request.form.get("From", "unknown")
    to_number = request.form.get("To", "unknown")
    digit = request.form.get("Digits", "")

    retry_key = f"ivr:retries:{call_uuid}"
    rc = current_app.extensions["redis_client"]

    if digit == "1":
        _log_call(call_uuid, from_number, to_number, "sales", "completed")
        rc.delete(retry_key)
        return _xml_response(_speak_xml("Connecting you to Sales. Please hold."))

    if digit == "2":
        _log_call(call_uuid, from_number, to_number, "support", "completed")
        rc.delete(retry_key)
        return _xml_response(_speak_xml("Connecting you to Support. Please hold."))

    if digit == "3":
        spoken = " ".join(from_number)
        _log_call(call_uuid, from_number, to_number, "readback", "completed")
        rc.delete(retry_key)
        return _xml_response(_speak_xml(f"Your number is {spoken}."))

    # Invalid input or no input — increment retry counter
    pipe = rc.pipeline()
    pipe.incr(retry_key)
    pipe.ttl(retry_key)
    count, ttl = pipe.execute()

    if ttl == -1:
        rc.expire(retry_key, 300)

    if count >= 3:
        _log_call(call_uuid, from_number, to_number, "timeout", "no-input")
        return _xml_response(GOODBYE_XML)

    selection = "invalid" if digit else "timeout"
    _log_call(call_uuid, from_number, to_number, selection, "no-input")
    retry_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Speak>{"We did not receive any input." if not digit else "Invalid option."} Please try again.</Speak>
  <Redirect method="POST">{request.url_root.rstrip("/")}/ivr/welcome</Redirect>
</Response>"""
    return _xml_response(retry_xml)
