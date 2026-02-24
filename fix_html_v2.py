import json
import re

# Read the current v4 HTML file
with open(r'C:\Users\Mario\work\smtr-web\signal-review-v4.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Read Opus data again
with open(r'C:\Users\Mario\work\invest-sns\_opus_review_results.json', 'r', encoding='utf-8') as f:
    opus_data = json.load(f)

print(f"Processing {len(opus_data)} opus items...")

# Create better embedded data structure
embedded_reviews = {}
signal_data = []

for key, value in opus_data.items():
    signal_info = value['signal_data']
    
    # Create signal entry for the main grid
    signal_entry = {
        'id': key,
        'asset': signal_info['asset'],
        'signal_type': signal_info['signal_type'], 
        'content': signal_info['content'],
        'confidence': signal_info['confidence'],
        'timeframe': signal_info['timeframe'],
        'conditional': signal_info['conditional'],
        'skin_in_game': signal_info['skin_in_game'],
        'hedged': signal_info['hedged'],
        'context': signal_info['context'],
        'timestamp': signal_info['timestamp'],
        'video_id': signal_info['video_id'],
        'channel': signal_info['channel'],
        'title': signal_info['title'],
        'video_summary': signal_info['video_summary'],
        'upload_date': signal_info['upload_date'],
        # Review status
        'review_status': 'approved' if value.get('verdict') == 'approve' else 'rejected' if value.get('verdict') == 'reject' else 'pending',
        'review_reason': value.get('reasoning', ''),
        # Opus review
        'opus_review_status': 'approved' if value.get('verdict') == 'approve' else 'rejected' if value.get('verdict') == 'reject' else 'pending',
        'opus_confidence': value.get('confidence', 'MEDIUM'),
        'opus_reasoning': value.get('reasoning', '')
    }
    
    signal_data.append(signal_entry)
    
    # Also add to reviews dict for API replacement
    embedded_reviews[key] = {
        'review_status': signal_entry['review_status'],
        'review_reason': signal_entry['review_reason'],
        'opus_review_status': signal_entry['opus_review_status'],
        'opus_confidence': signal_entry['opus_confidence'],
        'opus_reasoning': signal_entry['opus_reasoning']
    }

print(f"Created {len(signal_data)} signal entries and {len(embedded_reviews)} review entries")

# Convert to JavaScript
js_signal_data = json.dumps(signal_data, ensure_ascii=False, indent=2)
js_embedded_reviews = json.dumps(embedded_reviews, ensure_ascii=False, indent=2)

# Create the complete embedded JavaScript
embedded_js = f"""
// ========== EMBEDDED DATA FOR GITHUB PAGES ==========
const EMBEDDED_SIGNAL_DATA = {js_signal_data};
const EMBEDDED_REVIEWS = {js_embedded_reviews};

// Replace API calls with embedded data
function loadSignals() {{
    console.log('Loading embedded signal data:', EMBEDDED_SIGNAL_DATA.length, 'signals');
    return Promise.resolve(EMBEDDED_SIGNAL_DATA);
}}

function loadReviews() {{
    console.log('Loading embedded review data:', Object.keys(EMBEDDED_REVIEWS).length, 'reviews');
    return Promise.resolve(EMBEDDED_REVIEWS);
}}

// localStorage functions for new reviews
function saveReview(signalId, reviewData) {{
    const existing = JSON.parse(localStorage.getItem('signal_reviews') || '{{}}');
    existing[signalId] = reviewData;
    localStorage.setItem('signal_reviews', JSON.stringify(existing));
    console.log('Saved review to localStorage:', signalId, reviewData);
}}

function getLocalReviews() {{
    return JSON.parse(localStorage.getItem('signal_reviews') || '{{}}');
}}

// Merge embedded data with localStorage data
function getAllReviews() {{
    const embedded = EMBEDDED_REVIEWS;
    const local = getLocalReviews();
    return {{...embedded, ...local}};
}}

// Mock API endpoints
const API_ENDPOINTS = {{
    signals: () => loadSignals(),
    reviews: () => Promise.resolve(getAllReviews()),
    submit: (data) => {{
        saveReview(data.id, data);
        return Promise.resolve({{'success': true}});
    }}
}};

console.log('GitHub Pages mode: Embedded data loaded');
console.log('Signals:', EMBEDDED_SIGNAL_DATA.length);
console.log('Reviews:', Object.keys(EMBEDDED_REVIEWS).length);
// ================================================
"""

# Insert the embedded JavaScript at the beginning of the script section
script_pattern = r'(<script[^>]*>)(.*?)(</script>)'
match = re.search(script_pattern, html_content, re.DOTALL)

if match:
    script_start = match.group(1)
    script_content = match.group(2)
    script_end = match.group(3)
    
    # Clean existing embedded code if any
    script_content = re.sub(r'// Embedded review data.*?// ================================================\n', '', script_content, flags=re.DOTALL)
    
    # Insert new embedded JavaScript
    new_script_content = embedded_js + '\n' + script_content
    
    # Replace API calls in the existing script
    # Replace fetch calls to load signals
    new_script_content = re.sub(
        r"fetch\(['\"]?[^'\"]*api/signals[^'\"]*['\"]?\)",
        "API_ENDPOINTS.signals()",
        new_script_content
    )
    
    # Replace fetch calls to load reviews  
    new_script_content = re.sub(
        r"fetch\(['\"]?[^'\"]*api/reviews[^'\"]*['\"]?\)",
        "API_ENDPOINTS.reviews()",
        new_script_content
    )
    
    # Replace submit calls
    new_script_content = re.sub(
        r"fetch\(['\"]?[^'\"]*api/submit[^'\"]*['\"]?,\s*\{[^}]+\}\)",
        "API_ENDPOINTS.submit",
        new_script_content
    )
    
    # Remove API_URL definitions
    new_script_content = re.sub(r"const\s+API_URL\s*=\s*[^;]+;", "// API_URL removed for GitHub Pages", new_script_content)
    new_script_content = re.sub(r"const\s+OPUS_API_URL\s*=\s*[^;]+;", "// OPUS_API_URL removed for GitHub Pages", new_script_content)
    
    # Create the final HTML
    final_html = html_content.replace(
        match.group(0),
        script_start + new_script_content + script_end
    )
    
    # Save the corrected version
    with open(r'C:\Users\Mario\work\smtr-web\signal-review-v3.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("SUCCESS: Final HTML saved as signal-review-v3.html")
    print(f"Embedded {len(signal_data)} signals with review data")
    print("Replaced API calls with local data access")
    print("Added localStorage support for new reviews")
    
else:
    print("ERROR: Could not find script section to modify")