import requests
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ✅ Gmail details fill cheyyi
YOUR_EMAIL = "officialallinone77@gmail.com"
APP_PASSWORD = "yjgd irac utbp qlqy"

memory = []

def analyze_csv(file):
    try:
        df = pd.read_csv(file)
        return df.describe().to_string()
    except Exception as e:
        return str(e)

def plot_csv(file):
    try:
        df = pd.read_csv(file)
        plt.figure()
        plt.bar(df["Name"], df["Sales"])
        plt.title("Sales Graph")
        plt.xlabel("Name")
        plt.ylabel("Sales")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        return "Graph shown successfully"
    except Exception as e:
        return str(e)

def insights_csv(file):
    try:
        df = pd.read_csv(file)
        result = ""
        result += "📊 INSIGHTS\n"
        result += f"Rows: {len(df)}\n"
        result += f"Columns: {list(df.columns)}\n\n"
        if "Sales" in df.columns:
            result += f"Average Sales: {df['Sales'].mean()}\n"
            result += f"Max Sales: {df['Sales'].max()}\n"
            result += f"Min Sales: {df['Sales'].min()}\n"
            top = df.loc[df["Sales"].idxmax()]
            result += f"\n🏆 Top Performer:\n"
            result += f"Name: {top['Name']}\n"
            result += f"Sales: {top['Sales']}\n"
        return result
    except Exception as e:
        return str(e)

def send_email(to, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = YOUR_EMAIL
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(YOUR_EMAIL, APP_PASSWORD)
            server.sendmail(YOUR_EMAIL, to, msg.as_string())
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

print("🤖 AI Agent Ready!")
print("Commands: csv: | graph: | insight: | send email | exit")

while True:
    user = input("\nYou: ")

    if user.lower() == "exit":
        break

    elif user.startswith("csv:"):
        file = user.replace("csv:", "").strip()
        print(analyze_csv(file))

    elif user.startswith("graph:"):
        file = user.replace("graph:", "").strip()
        print(plot_csv(file))

    elif user.startswith("insight:"):
        file = user.replace("insight:", "").strip()
        print(insights_csv(file))

    elif user.lower() == "send email":
        to = input("To: ")
        subject = input("Subject: ")
        body = input("Body: ")
        print(send_email(to, subject, body))

    else:
        memory.append(user)
        prompt = "\n".join(memory[-10:]) + "\nAI:"
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2", "prompt": prompt, "stream": False}
        )
        reply = response.json()["response"]
        print("Agent:", reply)
        memory.append(reply)