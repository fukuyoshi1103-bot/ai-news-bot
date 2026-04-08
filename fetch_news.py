import os
import requests
import anthropic

def get_ai_news():
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "artificial intelligence OR AI",
        "domains": "techcrunch.com,theverge.com,wired.com,venturebeat.com,thenextweb.com",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": os.environ["NEWS_API_KEY"]
    }
    res = requests.get(url, params=params)
    articles = res.json().get("articles", [])
    
    news_text = "\n".join([
        f"- {a['title']}: {a['description'] or ''}"
        for a in articles[:10]
    ])
    return news_text

def summarize_with_claude(news_text):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""以下の英語ニュースをもとに、今日のAI最新情報を日本語で簡潔にまとめてください。
箇条書き5件、各1〜2文で。絵文字を適度に使ってLINE向けに読みやすく。

{news_text}"""
        }]
    )
    return message.content[0].text

def send_line_message(message):
    headers = {
        "Authorization": f"Bearer {os.environ['LINE_CHANNEL_ACCESS_TOKEN']}",
        "Content-Type": "application/json"
    }
    data = {
        "to": os.environ["LINE_USER_ID"],
        "messages": [{"type": "text", "text": f"🤖 今日のAIニュース\n\n{message}"}]
    }
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)

if __name__ == "__main__":
    news = get_ai_news()
    summary = summarize_with_claude(news)
    send_line_message(summary)
    print("送信完了！")