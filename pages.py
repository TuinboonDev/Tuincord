from flask import Blueprint, redirect
import json

pages = Blueprint('pages', __name__)

MAP_FILENAME = "map.json"

@pages.route('/<key>')
def redirect_url(key):
    with open(MAP_FILENAME, "r") as f:
        shortened_urls = json.load(f)
    
    for item in shortened_urls:
        if item["shortcode"] == key:
            original_url = item["url"]

            if not original_url.startswith(('http://', 'https://')):
                original_url = 'https://' + original_url
            return redirect(original_url)
    
    return f"<h1>404 - URL not found</h1><p>The key '{key}' doesn't exist.</p>", 404