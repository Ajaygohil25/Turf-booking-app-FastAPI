from fastapi_mail import FastMail, MessageSchema, MessageType
from .mail_config import conf

async def send_mail(email: str, subject: str, content: str):
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email from Turf Booking Application</title>
        <style>
            /* Fallback fonts and basic reset */
            body, h2, p {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
            }}
        </style>
    </head>
    <body style="background-color: #000; color: #fff; padding: 20px; font-family: Arial, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; margin: 0 auto;">
            <tr>
                <td style="padding: 20px 0; text-align: center;">
                    <h2 style="font-size: 24px; color: #fff; margin-bottom: 10px;">It's from Turf Booking Application</h2>
                </td>
            </tr>
            <tr>
                <td style="padding: 10px 20px; background-color: #1a1a1a; border-radius: 8px;">
                    <p style="font-size: 16px; color: #fff; margin-bottom: 15px;">Sending mail for: <strong style="color: #ffcc00;">{subject}</strong></p>
                    <p style="font-size: 16px; color: #fff; margin-bottom: 15px;">{content}</p>
                    <p style="font-size: 16px; color: #fff; margin-bottom: 0;">Thanks for using Turf booking app. We hope you enjoy it!</p>
                </td>
            </tr>
            <tr>
                <td style="padding: 20px 0; text-align: center;">
                    <p style="font-size: 14px; color: #ccc;">&copy; 2025 Turf Booking Application. All rights reserved.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=template,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)
