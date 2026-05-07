import sys
sys.path.insert(0, '/opt/agents')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import structlog

log = structlog.get_logger()
app = FastAPI(title="communication_mcp", version="1.0.0")

class SendSlackRequest(BaseModel):
    channel: str
    message: str

class SendPagerDutyRequest(BaseModel):
    service: str
    message: str

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@app.get("/health")
def health():
    return {"status": "ok", "server": "communication_mcp", "port": 8007}

@app.post("/send_slack")
def send_slack(req: SendSlackRequest):
    # Placeholder for Slack webhook
    log.info("slack_sent", channel=req.channel, message=req.message[:50])
    return {"channel": req.channel, "sent": True}

@app.post("/send_pagerduty")
def send_pagerduty(req: SendPagerDutyRequest):
    # Placeholder for PagerDuty API
    log.info("pagerduty_sent", service=req.service, message=req.message[:50])
    return {"service": req.service, "sent": True}

@app.post("/send_email")
def send_email(req: SendEmailRequest):
    # Placeholder for email sending
    log.info("email_sent", to=req.to, subject=req.subject)
    return {"to": req.to, "sent": True}
