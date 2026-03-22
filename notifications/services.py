from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from .models import Notification


def create_notification(user, title, message, type):

    # جلوگیری از تکرار
    if Notification.objects.filter(
        user=user, title=title, message=message
    ).exists():
        return

    # Save notification
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type
    )

    # 📩 Send only important emails
    if type not in ["badge", "career", "course"] or not user.email:
        return

    # 🎯 Dynamic UI based on type
    type_config = {
        "badge": {
        "icon": "✦",
            "color": "#7c3aed",
            "bg": "#ede9fe",
            "label": "New Achievement"
        },
        "course": {
            "icon": "˚⟡˖ ࣪",
            "color": "#2563eb",
            "bg": "#dbeafe",
            "label": "Course Update"
        },
        "career": {
            "icon": ".☘︎ ݁˖",
            "color": "#d97706",
            "bg": "#fef3c7",
            "label": "Career Opportunity"
        },
    }

    config = type_config.get(type, {
        "icon": "🛎",
        "color": "#64748b",
        "bg": "#f1f5f9",
        "label": "Notification"
    })

    subject = f"{config['label']}: {title} | SkillAI"

    dashboard_url = "http://127.0.0.1:8000/notifications/all/"
    html_content = f"""
<div style="margin:0;padding:0;background:#fdf2f8;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
    <tr>
      <td align="center">

        <table width="420" cellpadding="0" cellspacing="0"
          style="background:#ffffff;border-radius:16px;
                 box-shadow:0 12px 30px rgba(167,139,250,0.15);
                 overflow:hidden;">

          <!-- HEADER -->
          <tr>
            <td style="
              padding:20px;
              background:linear-gradient(135deg,#a78bfa,#f472b6);
              text-align:center;
              font-size:20px;
              font-weight:700;
              color:white;">
              SkillAI ✦
            </td>
          </tr>

          <!-- BODY -->
          <tr>
            <td style="padding:28px;">

              <p style="margin:0 0 18px 0;font-size:14px;color:#475569;">
                Hi <strong>{user.username}</strong>,
              </p>

              <!-- TYPE LABEL -->
              <div style="
                font-size:12px;
                color:{config['color']};
                font-weight:700;
                margin-bottom:14px;">
                {config['label']}
              </div>

              <!-- CARD -->
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="background:#f8fafc;border-radius:12px;padding:14px;">
                <tr>

                  <!-- ICON -->
                  <td width="50" valign="top">
                    <div style="
                      width:44px;height:44px;
                      background:{config['bg']};
                      border-radius:10px;
                      display:flex;
                      align-items:center;
                      justify-content:center;
                      font-size:22px;
                      color:{config['color']};">
                      {config['icon']}
                    </div>
                  </td>

                  <!-- TEXT -->
                  <td style="padding-left:12px;">
                    <div style="font-size:15px;font-weight:700;color:#1e1b4b;">
                      {title}
                    </div>

                    <div style="font-size:13px;color:#64748b;margin-top:6px;line-height:1.5;">
                      {message}
                    </div>
                  </td>

                </tr>
              </table>

              <!-- BUTTON -->
              <div style="text-align:center;margin:26px 0;">
                <a href="{dashboard_url}" style="
                  background:linear-gradient(135deg,#a78bfa,#f472b6);
                  color:white;
                  padding:12px 26px;
                  border-radius:10px;
                  text-decoration:none;
                  font-size:13px;
                  font-weight:600;
                  display:inline-block;">
                  View Notification
                </a>
              </div>

              <!-- FOOTER -->
              <div style="
                text-align:center;
                font-size:12px;
                color:#94a3b8;
                line-height:1.6;">
                You're receiving this because of activity on your SkillAI account.<br>
                © 2026 SkillAI · Built for learning and career growth
              </div>

            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</div>
"""

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()