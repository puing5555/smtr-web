const fs = require('fs');
const reviews = JSON.parse(fs.readFileSync('C:/Users/Mario/work/smtr-web/preloaded-reviews.json', 'utf8'));
const json = JSON.stringify(reviews);

let html = fs.readFileSync('C:/Users/Mario/work/smtr-web/signal-review-v3.html', 'utf8');

// Use regex to find and replace
const regex = /function loadReviews\(\) \{\s*try \{ return JSON\.parse\(localStorage\.getItem\('signal-reviews-v2'\) \|\| '\{\}'\); \}\s*catch\(e\) \{ return \{\}; \}\s*\}/;

const match = html.match(regex);
if (match) {
    const replacement = `var PRELOADED_REVIEWS = ${json};
        function loadReviews() {
            try {
                var stored = JSON.parse(localStorage.getItem('signal-reviews-v2') || '{}');
                var merged = {};
                for (var k in PRELOADED_REVIEWS) merged[k] = PRELOADED_REVIEWS[k];
                for (var k in stored) merged[k] = stored[k];
                return merged;
            }
            catch(e) { return PRELOADED_REVIEWS || {}; }
        }`;
    html = html.replace(regex, replacement);
    fs.writeFileSync('C:/Users/Mario/work/smtr-web/signal-review-v3.html', html);
    console.log('DONE');
} else {
    console.log('NO MATCH');
}
