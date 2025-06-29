import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageColor, ImageDraw
import io

st.set_page_config(page_title="QR Generator", page_icon="🔗")

st.title("QR Code Generator")

st.write("""
✨ Generate stylish QR Codes for text, links, WiFi, vCards, social profiles, payments, events and more!  
Upload a background image or use none — your QR appears **bottom center** keeping your face clear.
""")

# --- Select QR type ---
qr_type = st.selectbox(
    "What do you want to encode?",
    ["Plain Text", "URL", "WiFi Network", "vCard (Business Card)", "WhatsApp",
     "Instagram", "LinkedIn", "Snapchat", "SMS", "Event"]
)

# --- Get data input ---
data = ""

if qr_type == "Plain Text":
    data = st.text_area("Enter your text")

elif qr_type == "URL":
    data = st.text_input("Enter the URL")

elif qr_type == "WiFi Network":
    ssid = st.text_input("WiFi SSID (name)")
    password = st.text_input("WiFi Password")
    security = st.selectbox("Security", ["WPA", "WEP", "nopass"])
    hidden = st.checkbox("Hidden network?", value=False)
    data = f"WIFI:T:{security};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"

elif qr_type == "vCard (Business Card)":
    name = st.text_input("Full Name")
    phone = st.text_input("Phone Number")
    email = st.text_input("Email")
    org = st.text_input("Organization")
    url = st.text_input("Website")
    data = f"BEGIN:VCARD\nVERSION:3.0\nN:{name}\nTEL:{phone}\nEMAIL:{email}\nORG:{org}\nURL:{url}\nEND:VCARD"

elif qr_type == "WhatsApp":
    phone = st.text_input("Recipient Phone Number (with country code)")
    message = st.text_area("Message")
    data = f"https://wa.me/{phone}?text={message}"

elif qr_type == "Instagram":
    username = st.text_input("Instagram Username")
    data = f"https://instagram.com/{username}"

elif qr_type == "LinkedIn":
    profile_url = st.text_input("LinkedIn Profile URL")
    data = profile_url

elif qr_type == "Snapchat":
    username = st.text_input("Snapchat Username")
    data = f"https://www.snapchat.com/add/{username}"

elif qr_type == "SMS":
    phone = st.text_input("Phone Number")
    message = st.text_area("SMS Message")
    data = f"SMSTO:{phone}:{message}"

elif qr_type == "Event":
    event_name = st.text_input("Event Name")
    date = st.date_input("Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")
    details = st.text_area("Details")
    venue = st.text_input("Venue")

    # Format for Google Calendar
    start_dt = f"{date.strftime('%Y%m%d')}T{start_time.strftime('%H%M%S')}Z"
    end_dt = f"{date.strftime('%Y%m%d')}T{end_time.strftime('%H%M%S')}Z"
    data = (
        f"https://www.google.com/calendar/render"
        f"?action=TEMPLATE"
        f"&text={event_name.replace(' ', '+')}"
        f"&dates={start_dt}/{end_dt}"
        f"&details={details.replace(' ', '+')}"
        f"&location={venue.replace(' ', '+')}"
    )

# --- Style ---
st.subheader("🎨 Customize Style")
fill_color = st.color_picker("QR Color", "#000000")
back_color = st.color_picker("Background Color", "#ffffff")
fill_color_rgb = ImageColor.getrgb(fill_color)
back_color_rgb = ImageColor.getrgb(back_color)

# --- Background image option ---
st.subheader("📸 Optional: Upload background image")
bg_image_file = st.file_uploader("Upload background (PNG/JPG)", type=["png", "jpg", "jpeg"])

# --- Generate QR ---
if st.button("Generate QR Code"):
    if data:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        qr_img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=SolidFillColorMask(back_color=back_color_rgb, front_color=fill_color_rgb)
        ).get_image()

        qr_img = qr_img.resize((150, 150))

        if bg_image_file:
            bg = Image.open(bg_image_file).convert("RGB")
            bg = bg.resize((300, 300))

            # Calculate bottom-center position
            pos = ((bg.width - qr_img.width) // 2, bg.height - qr_img.height - 10)

            bg.paste(qr_img, pos)

            final_img = bg

        else:
            final_img = qr_img

        st.image(final_img, caption="✅ Your scannable QR", use_container_width=False)

        buf = io.BytesIO()
        final_img.save(buf, format="PNG")
        buf.seek(0)

        st.download_button(
            label="📥 Download",
            data=buf,
            file_name="qr_code.png",
            mime="image/png"
        )

        if 'qr_history' not in st.session_state:
            st.session_state.qr_history = []
        st.session_state.qr_history.append(final_img)

    else:
        st.warning("⚠️ Please enter valid data!")

# --- Show QR History ---
if 'qr_history' in st.session_state and len(st.session_state.qr_history) > 0:
    st.subheader("📜 Your QR Code History (this session)")
    cols = st.columns(4)
    for idx, hist_img in enumerate(st.session_state.qr_history):
        with cols[idx % 4]:
            st.image(hist_img, width=150)

st.markdown("---")
st.caption("""
✨ Made by Mukul Sapra
[LinkdIn](https://www.linkedin.com/in/mukul-sapra-ba31b3372/) | [GitHub](https://github.com/DevGyaniMukul) | mukulsapra123@gmail.com
""")
st.markdown("""
<!-- Plausible Analytics -->
<script defer data-domain="globalqr.onrender.com" src="https://plausible.io/js/script.js"></script>
""", unsafe_allow_html=True)
