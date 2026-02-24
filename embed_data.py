import json
import re

# Read the HTML file
with open(r'C:\Users\Mario\work\invest-sns\signal-review-v3.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Read Opus data
with open(r'C:\Users\Mario\work\invest-sns\_opus_review_results.json', 'r', encoding='utf-8') as f:
    opus_data = json.load(f)

# Try to read backup data with UTF-16
backup_data = {}
try:
    # Try without BOM first
    with open(r'C:\Users\Mario\work\invest-sns\smtr_data\corinpapa1106\_review_results_backup.json', 'r', encoding='utf-16') as f:
        backup_data = json.load(f)
    print(f"Backup data loaded with utf-16: {len(backup_data)} items")
except:
    print("Could not read backup data, using empty dict")

# Create embedded data
embedded_reviews = {}

# Add backup data to embedded reviews
for key, value in backup_data.items():
    embedded_reviews[key] = {
        'review_status': 'approved' if value.get('status') == 'approve' else 'rejected' if value.get('status') == 'reject' else 'pending',
        'review_reason': value.get('reason', ''),
        'review_timestamp': value.get('timestamp', '')
    }

# Add opus data to embedded reviews  
for key, value in opus_data.items():
    signal_id = f"{value['signal_data']['video_id']}_{value['signal_data']['asset']}"
    if signal_id not in embedded_reviews:
        embedded_reviews[signal_id] = {}
    
    embedded_reviews[signal_id]['opus_review_status'] = 'approved' if value.get('verdict') == 'approve' else 'rejected' if value.get('verdict') == 'reject' else 'pending'
    embedded_reviews[signal_id]['opus_confidence'] = value.get('confidence', 'MEDIUM')
    embedded_reviews[signal_id]['opus_reasoning'] = value.get('reasoning', '')

print(f"Total embedded review items: {len(embedded_reviews)}")

# Convert to JavaScript object
js_embedded_reviews = json.dumps(embedded_reviews, ensure_ascii=False, indent=2)

# Find the script tag and add embedded data
script_pattern = r'(<script[^>]*>)(.*?)(</script>)'
match = re.search(script_pattern, html_content, re.DOTALL)

if match:
    script_start = match.group(1)
    script_content = match.group(2)
    script_end = match.group(3)
    
    # Add embedded data at the beginning of script
    embedded_script = f"""
        // Embedded review data for GitHub Pages
        const EMBEDDED_REVIEWS = {js_embedded_reviews};
        
        // Use embedded data instead of API calls
        function getReviewData() {{
            return Promise.resolve(EMBEDDED_REVIEWS);
        }}
        
        function getOpusData() {{
            return Promise.resolve(EMBEDDED_REVIEWS);
        }}
        
        // localStorage functions for new reviews
        function saveToLocalStorage(key, data) {{
            const existing = JSON.parse(localStorage.getItem('signal_reviews') || '{{}}');
            existing[key] = data;
            localStorage.setItem('signal_reviews', JSON.stringify(existing));
        }}
        
        function getFromLocalStorage() {{
            return JSON.parse(localStorage.getItem('signal_reviews') || '{{}}');
        }}
        
        // Merge embedded data with localStorage data
        function getAllReviewData() {{
            const embedded = EMBEDDED_REVIEWS;
            const localStorage = getFromLocalStorage();
            return {{...embedded, ...localStorage}};
        }}
    """
    
    # Replace fetch calls with local data access
    script_content = re.sub(
        r'fetch\([^)]+\)',
        'getAllReviewData().then ? getAllReviewData() : Promise.resolve(getAllReviewData())',
        script_content
    )
    
    # Remove localhost API URLs and replace with local data
    script_content = re.sub(
        r'const\s+API_URL\s*=\s*[^;]+;',
        '// API_URL removed for GitHub Pages',
        script_content
    )
    
    script_content = re.sub(
        r'const\s+OPUS_API_URL\s*=\s*[^;]+;',
        '// OPUS_API_URL removed for GitHub Pages',
        script_content
    )
    
    new_html = html_content.replace(
        script_start + script_content + script_end,
        script_start + embedded_script + script_content + script_end
    )
    
    # Save the modified HTML
    with open(r'C:\Users\Mario\work\smtr-web\signal-review-v4.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print("Modified HTML saved as signal-review-v4.html")
    print("Embedded data includes:")
    print(f"  - Review data: {len([k for k, v in embedded_reviews.items() if 'review_status' in v])} items")
    print(f"  - Opus data: {len([k for k, v in embedded_reviews.items() if 'opus_review_status' in v])} items")
else:
    print("Could not find script tag to modify")