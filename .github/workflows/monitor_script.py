import imaplib
import email
import json
import os
import re
from datetime import datetime, timedelta
import pytz

# Define Michigan Timezone
MI_TZ = pytz.timezone('America/Detroit')

def get_mi_now():
    """Returns the current time specifically in Michigan."""
    return datetime.now(MI_TZ)

def parse_bridge_time(time_str):
    """Converts '03/14/26 @ 9:10' to a localized Michigan datetime."""
    try:
        if not time_str or time_str == "N/A": return None
        
        # Standardize: remove @, collapse spaces
        clean = re.sub(r'\s+', ' ', time_str.replace('@', '')).strip().upper()
        
        # Split into date and time to handle single-digit hours (9:10 -> 09:10)
        parts = clean.split(' ')
        date_part = parts[0]
        time_part = parts[1]
        
        if len(time_part.split(':')[0]) == 1:
            time_part = "0" + time_part
            
        final_str = f"{date_part} {time_part}"
        dt = datetime.strptime(final_str, "%m/%d/%y %H:%M")
        
        return MI_TZ.localize(dt)
    except Exception as e:
        print(f"Time Parse Error: {e} on string: {time_str}")
        return None

def update_metrics(data):
    """Calculates uptime percentage based on closure history."""
    history = data.get("history", [])
    if not history:
        return data

    now = get_mi_now()
    total_closed = timedelta()
    
    # We start monitoring from the very first closure record
    first_event_time = parse_bridge_time(history[0]['closed_at'])
    if not first_event_time:
        return data

    for closure in history:
        start_dt = parse_bridge_time(closure['closed_at'])
        if not start_dt: continue
        
        # If it's still closed, calculate duration until 'now'
        if closure['opened_at']:
            end_dt = parse_bridge_time(closure['opened_at'])
        else:
            end_dt = now
            
        if end_dt and start_dt:
            total_closed += (end_dt - start_dt)

    total_time_elapsed = now - first_event_time
    
    if total_time_elapsed.total_seconds() > 0:
        closed_pct = (total_closed / total_time_elapsed) * 100
        data["metrics"] = {
            "pct_closed": round(closed_pct, 1),
            "pct_open": round(100 - closed_pct, 1)
        }
    return data

def get_bridge_status():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(os.environ['GMAIL_USER'], os.environ['GMAIL_PASS'])
        mail.select("inbox")
        
        # Broad search for Mackinac to ensure we catch the email
        search_query = '(SUBJECT "Mackinac" TO "xxfortnitedubzxx+bridge@gmail.com")'
        status, messages = mail.search(None, search_query)
        if not messages[0]: return None
            
        latest_msg_id = messages[0].split()[-1]
        _, data = mail.fetch(latest_msg_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')
            
        full_text = (str(msg.get('Subject')) + " " + body).upper()

        if "NOW OPEN" in full_text or "IS OPEN" in full_text:
            bridge_status = "OPEN"
        elif "CLOSED" in full_text:
            bridge_status = "CLOSED"
        else:
            return None

        # Flexible regex for 9:10 or 09:10
        time_match = re.search(r'\d{2}/\d{2}/\d{2}\s*@\s*\d{1,2}:\d{2}', full_text)
        update_time = time_match.group(0) if time_match else get_mi_now().strftime("%m/%d/%y @ %H:%M")
        
        return {"status": bridge_status, "time": update_time}
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    result = get_bridge_status()
    file_path = 'static/bridge_status.json'
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except:
        data = {"current_status": "UNKNOWN", "drink_count": 0, "history": [], "metrics": {"pct_open": 100, "pct_closed": 0}}
    
    if result:
        # Check if status flipped
        if result["status"] != data.get("current_status"):
            
            if result["status"] == "CLOSED":
                # Increment drink count
                data["drink_count"] = data.get("drink_count", 0) + 1
                
                # Create a new history entry
                data["history"].append({
                    "closed_at": result["time"],
                    "opened_at": None,
                    "duration": "IN PROGRESS"
                })
            
            elif result["status"] == "OPEN":
                # Finalize the last closure duration
                if data["history"] and data["history"][-1]["opened_at"] is None:
                    start = parse_bridge_time(data["history"][-1]["closed_at"])
                    end = parse_bridge_time(result["time"])
                    if start and end:
                        diff = end - start
                        duration_str = f"{int(diff.total_seconds()//3600)}h {int((diff.total_seconds()%3600)//60)}m"
                        data["history"][-1]["opened_at"] = result["time"]
                        data["history"][-1]["duration"] = duration_str

            data["current_status"] = result["status"]
            data["last_update"] = result["time"]

    # Refresh analytics (uptime pct)
    data = update_metrics(data)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)