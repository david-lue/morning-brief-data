import urllib.request, re, json, sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = [
    ('The Headlines', 'https://feeds.simplecast.com/ydACIPHO'),
    ('The Daily',     'https://feeds.simplecast.com/54nAGcIl'),
    ('AI Daily Brief','https://anchor.fm/s/f7cac464/podcast/rss'),
    ('AI + a16z',     'https://feeds.simplecast.com/Hb_IuXOo'),
    ('Hugging Face',  'https://rss.art19.com/hugging-face'),
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
}

today = datetime.now(timezone.utc).date()
results = []

for name, url in FEEDS:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode('utf-8', errors='replace')
        items = re.findall(r'<item[^>]*>(.*?)</item>', content, re.DOTALL)
        if not items:
            results.append({'name': name, 'error': 'no items'}); continue
        item = items[0]
        t   = re.search(r'<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item, re.DOTALL)
        d   = re.search(r'<pubDate>(.*?)</pubDate>', item)
        dur = re.search(r'<itunes:duration[^>]*>(.*?)</itunes:duration>', item, re.DOTALL)
        title = t.group(1).strip() if t else 'N/A'
        pub_date = None; is_today = False; date_str = 'N/A'
        if d:
            try:
                pub_date = parsedate_to_datetime(d.group(1).strip()).date()
                is_today = (pub_date == today)
                date_str = 'Today' if is_today else pub_date.strftime('%b %-d')
            except Exception: pass
        mins = 'N/A'
        if dur:
            raw = dur.group(1).strip(); parts = raw.split(':')
            try:
                if len(parts)==3: m=int(parts[0])*60+int(parts[1])+round(int(parts[2])/60)
                elif len(parts)==2: m=int(parts[0])+round(int(parts[1])/60)
                else: m=round(int(raw)/60)
                mins=f'{m} min'
            except Exception: pass
        results.append({'name': name, 'title': title, 'date': date_str, 'duration': mins, 'is_today': is_today})
    except Exception as e:
        results.append({'name': name, 'error': str(e)})

output = {'fetched_at': datetime.now(timezone.utc).isoformat(), 'date': str(today), 'episodes': results}
print(json.dumps(output, indent=2))
