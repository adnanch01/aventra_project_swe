from flask import Flask, render_template, request, redirect, jsonify
import mysql.connector
import sqlite3
import os
import requests

app = Flask(__name__)

# RDS Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="your-rds-endpoint",
        user="admin",
        password="your_password",
        database="aventra_db"
    )

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Display Users (example of fetching data)
@app.route('/users')
def users():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, email FROM Users;")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('users.html', users=users)

# Add a new user (example of inserting data)
@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    email = request.form['email']
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Users (username, email) VALUES (%s, %s)", (username, email))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/users')


# Proxy/search endpoint for Eventbrite (demo)
@app.route('/api/search')
def api_search():
    """Proxy search to Eventbrite for demo purposes.

    Query params supported (all optional):
      - q: free-text query
      - lat, lng: location coordinates
      - start: ISO8601 range start (e.g. 2025-11-10T00:00:00Z)
      - end: ISO8601 range end

    Requires environment variable EVENTBRITE_TOKEN to be set on the server.
    """
    EVENTBRITE_TOKEN = os.getenv('EVENTBRITE_TOKEN')
    if not EVENTBRITE_TOKEN:
        return jsonify({'error': 'EVENTBRITE_TOKEN not configured on server'}), 500

    q = request.args.get('q', '')
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    start = request.args.get('start')
    end = request.args.get('end')

    # First, try to return results from a local Events table (SQLite preferred for dev).
    db_results = []
    use_sqlite = os.getenv('DB_USE_SQLITE', '1') == '1' or os.getenv('DB_HOST', 'your-rds-endpoint') in ('', 'your-rds-endpoint')
    try:
        if use_sqlite:
            conn = sqlite3.connect('dev_events.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            sql = "SELECT id, title, description, start_time, end_time, venue, lat, lng, url, source FROM Events"
            filters = []
            params = []
            if q:
                filters.append("(title LIKE ? OR description LIKE ?)")
                params.extend([f"%{q}%", f"%{q}%"])
            if start and end:
                filters.append("(start_time BETWEEN ? AND ?)")
                params.extend([start, end])
            if filters:
                sql += " WHERE " + " AND ".join(filters)
            sql += " ORDER BY start_time LIMIT 50"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            for r in rows:
                item = {
                    'id': f"db-{r['id']}",
                    'title': r['title'],
                    'description': r['description'],
                    'start_time': r['start_time'],
                    'end_time': r['end_time'],
                    'url': r['url'],
                    'source': r['source'] or 'db',
                }
                if r['venue']:
                    item['venue_name'] = r['venue']
                if r['lat'] and r['lng']:
                    try:
                        item['lat'] = float(r['lat'])
                        item['lng'] = float(r['lng'])
                    except Exception:
                        pass
                db_results.append(item)
            cursor.close()
            conn.close()
        else:
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            sql = "SELECT id, title, description, start_time, end_time, venue, lat, lng, url, source FROM Events"
            filters = []
            params = []
            if q:
                filters.append("(title LIKE %s OR description LIKE %s)")
                params.extend([f"%{q}%", f"%{q}%"])
            if start and end:
                filters.append("(start_time BETWEEN %s AND %s)")
                params.extend([start, end])
            if filters:
                sql += " WHERE " + " AND ".join(filters)
            sql += " ORDER BY start_time LIMIT 50"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            for r in rows:
                item = {
                    'id': f"db-{r.get('id')}",
                    'title': r.get('title'),
                    'description': r.get('description'),
                    'start_time': r.get('start_time').isoformat() if r.get('start_time') else None,
                    'end_time': r.get('end_time').isoformat() if r.get('end_time') else None,
                    'url': r.get('url'),
                    'source': r.get('source') or 'db',
                }
                if r.get('venue'):
                    item['venue_name'] = r.get('venue')
                if r.get('lat') and r.get('lng'):
                    try:
                        item['lat'] = float(r.get('lat'))
                        item['lng'] = float(r.get('lng'))
                    except Exception:
                        pass
                db_results.append(item)
            cursor.close()
            db.close()
    except Exception:
        # If DB not configured or table doesn't exist, ignore and fall back to Eventbrite
        db_results = []

    if db_results:
        return jsonify({'total': len(db_results), 'results': db_results})

    params = {}
    if q:
        params['q'] = q
    if lat and lng:
        params['location.latitude'] = lat
        params['location.longitude'] = lng
    if start:
        params['start_date.range_start'] = start
    if end:
        params['start_date.range_end'] = end
    # ask eventbrite to expand venue information so we can return lat/lng if available
    params['expand'] = 'venue'

    headers = {
        'Authorization': f'Bearer {EVENTBRITE_TOKEN}'
    }

    try:
        resp = requests.get('https://www.eventbriteapi.com/v3/events/search/', params=params, headers=headers, timeout=10)
        # If Eventbrite returns 404 for search, treat as empty results and fall back gracefully
        if resp.status_code == 404:
            return jsonify({'total': 0, 'results': [], 'note': 'Eventbrite returned NOT_FOUND for search'}), 200
        resp.raise_for_status()
    except requests.RequestException as e:
        # On other request errors, return a friendly error
        details = str(e)
        if hasattr(e, 'response') and e.response is not None:
            details = f"status={e.response.status_code} body={e.response.text}"
        return jsonify({'error': 'Eventbrite API request failed', 'details': details}), 502

    data = resp.json()

    # Normalize response to a simple shape
    results = []
    for ev in data.get('events', []):
        item = {
            'id': ev.get('id'),
            'title': ev.get('name', {}).get('text'),
            'description': ev.get('description', {}).get('text'),
            'start_time': ev.get('start', {}).get('utc'),
            'end_time': ev.get('end', {}).get('utc'),
            'url': ev.get('url'),
            'source': 'eventbrite'
        }
        venue = ev.get('venue')
        if venue:
            item['venue_name'] = venue.get('name')
            address = venue.get('address', {})
            item['venue_address'] = address.get('localized_address_display')
            lat_v = address.get('latitude')
            lng_v = address.get('longitude')
            try:
                if lat_v and lng_v:
                    item['lat'] = float(lat_v)
                    item['lng'] = float(lng_v)
            except Exception:
                pass
        results.append(item)

    return jsonify({
        'total': data.get('pagination', {}).get('object_count', len(results)),
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True)
