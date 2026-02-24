#!/usr/bin/env python3
"""Send an email via Google Workspace SMTP relay.

Assumes Google Admin SMTP relay is configured to allow this VPS IP and does NOT require SMTP AUTH.

Usage:
  python3 scripts/send_mail_via_gmail_relay.py \
    --from albert@boomer64.com \
    --to steven@boomer64.com \
    --subject "Test" \
    --body "Hello"
"""

import argparse
import smtplib
from email.message import EmailMessage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--from', dest='from_addr', required=True)
    ap.add_argument('--to', dest='to_addrs', action='append', required=True,
                    help='Repeatable. Example: --to person@domain.com')
    ap.add_argument('--subject', required=True)
    ap.add_argument('--body', required=True)
    ap.add_argument('--host', default='smtp-relay.gmail.com')
    ap.add_argument('--port', type=int, default=587)

    args = ap.parse_args()

    msg = EmailMessage()
    msg['From'] = args.from_addr
    msg['To'] = ', '.join(args.to_addrs)
    msg['Subject'] = args.subject
    msg.set_content(args.body)

    # NOTE: Google SMTP relay may reject EHLO if local hostname is "localhost".
    # Use a domain-like local hostname to ensure STARTTLS is offered.
    with smtplib.SMTP(args.host, args.port, timeout=30, local_hostname='boomer64.com') as s:
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.send_message(msg)


if __name__ == '__main__':
    main()
