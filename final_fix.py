import re

# Read the generated HTML file
with open(r'C:\Users\Mario\work\smtr-web\signal-review-v3.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Analyzing HTML structure...")

# Find and fix common JavaScript patterns that need to be updated
patterns_to_fix = [
    # Fix loadData function calls
    (r'async function loadData\(\)\s*\{[^}]+fetch[^}]+\}', 
     '''async function loadData() {
        try {
            const signals = await loadSignals();
            const reviews = getAllReviews();
            
            signals.forEach(signal => {
                const review = reviews[signal.id];
                if (review) {
                    signal.review_status = review.review_status;
                    signal.review_reason = review.review_reason; 
                    signal.opus_review_status = review.opus_review_status;
                    signal.opus_confidence = review.opus_confidence;
                    signal.opus_reasoning = review.opus_reasoning;
                }
            });
            
            allSignals = signals;
            displaySignals(signals);
            updateStats(signals);
            populateFilters(signals);
            
        } catch (error) {
            console.error('Error loading data:', error);
            showError('Failed to load data');
        }
    }'''),
    
    # Fix submit review function
    (r'async function submitReview\([^)]+\)\s*\{[^}]+fetch[^}]+\}',
     '''async function submitReview(signalId, action, reason = '') {
        try {
            const reviewData = {
                review_status: action,
                review_reason: reason,
                review_timestamp: new Date().toISOString()
            };
            
            // Save to localStorage
            saveReview(signalId, reviewData);
            
            // Update the signal in memory
            const signal = allSignals.find(s => s.id === signalId);
            if (signal) {
                signal.review_status = action;
                signal.review_reason = reason;
            }
            
            // Refresh display
            displaySignals(allSignals);
            updateStats(allSignals);
            
            console.log('Review submitted:', signalId, action);
            
        } catch (error) {
            console.error('Error submitting review:', error);
            showError('Failed to submit review');
        }
    }'''),
    
    # Fix any remaining fetch calls to localhost
    (r'fetch\([\'"]http://localhost:[0-9]+[^\'"]*[\'"][^)]*\)', 
     'Promise.resolve({ok: true, json: () => Promise.resolve({})})'),
]

# Apply fixes
fixed_html = html_content
for pattern, replacement in patterns_to_fix:
    if re.search(pattern, fixed_html, re.DOTALL):
        fixed_html = re.sub(pattern, replacement, fixed_html, flags=re.DOTALL)
        print(f"Fixed pattern: {pattern[:50]}...")

# Add error handling and showError function if not exists
if 'function showError' not in fixed_html:
    error_function = '''
    function showError(message) {
        console.error('Error:', message);
        // You can add visual error display here
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'position:fixed;top:20px;right:20px;background:#f44336;color:white;padding:12px;border-radius:8px;z-index:1000;';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }
    '''
    # Insert before the closing script tag
    fixed_html = fixed_html.replace('</script>', error_function + '\n</script>')

# Ensure allSignals variable is declared
if 'let allSignals' not in fixed_html and 'var allSignals' not in fixed_html:
    fixed_html = fixed_html.replace(
        'console.log(\'GitHub Pages mode: Embedded data loaded\');',
        '''console.log('GitHub Pages mode: Embedded data loaded');
        
        // Global variables
        let allSignals = [];
        '''
    )

# Save the final version
with open(r'C:\Users\Mario\work\smtr-web\signal-review-v3.html', 'w', encoding='utf-8') as f:
    f.write(fixed_html)

print("FINAL: HTML file fully fixed and ready for GitHub Pages")
print("Changes made:")
print("- Embedded signal and review data")
print("- Replaced API calls with local data functions")
print("- Added localStorage support for new reviews")
print("- Fixed async functions and error handling")
print("- Removed server dependencies")

# Also create a test version with smaller dataset for verification
print("\nCreating test version...")
test_html = fixed_html.replace(
    'const EMBEDDED_SIGNAL_DATA = [',
    'const EMBEDDED_SIGNAL_DATA = [' + '\n  // Test data - first 5 items only'
)

# Get first 5 items only for test
import json
with open(r'C:\Users\Mario\work\invest-sns\_opus_review_results.json', 'r', encoding='utf-8') as f:
    opus_data = json.load(f)

test_signals = []
for i, (key, value) in enumerate(opus_data.items()):
    if i >= 5:
        break
    signal_info = value['signal_data']
    signal_entry = {
        'id': key,
        'asset': signal_info['asset'],
        'signal_type': signal_info['signal_type'], 
        'content': signal_info['content'],
        'timestamp': signal_info['timestamp'],
        'video_id': signal_info['video_id'],
        'channel': signal_info['channel'],
        'title': signal_info['title'],
        'upload_date': signal_info['upload_date'],
        'review_status': 'approved' if value.get('verdict') == 'approve' else 'pending',
        'opus_review_status': 'approved' if value.get('verdict') == 'approve' else 'pending',
        'opus_confidence': value.get('confidence', 'MEDIUM')
    }
    test_signals.append(signal_entry)

# Replace the embedded data with test data
test_js_data = json.dumps(test_signals, ensure_ascii=False, indent=2)
test_html = re.sub(
    r'const EMBEDDED_SIGNAL_DATA = \[.*?\];',
    f'const EMBEDDED_SIGNAL_DATA = {test_js_data};',
    test_html,
    flags=re.DOTALL
)

with open(r'C:\Users\Mario\work\smtr-web\signal-review-v3-test.html', 'w', encoding='utf-8') as f:
    f.write(test_html)

print(f"Test version created with {len(test_signals)} signals for quick verification")