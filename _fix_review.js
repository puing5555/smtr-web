const fs = require('fs');

// Read signals
const signals = JSON.parse(fs.readFileSync('invest-sns/smtr_data/corinpapa1106/_all_signals_194.json', 'utf8'));

// Read HTML
let html = fs.readFileSync('invest-sns/signal-review.html', 'utf8');

// Replace fetch-based loading with embedded data
// Find and replace the async loadData function
html = html.replace(
  /async function loadData\(\)[\s\S]*?try \{[\s\S]*?signalsData = await signalsResponse\.json\(\);[\s\S]*?console\.warn\('Claude 검증.*?\n\s*\}/,
  `async function loadData() {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('error').style.display = 'none';
            
            try {
                // 내장 데이터 사용 (194개 시그널)
                signalsData = window.EMBEDDED_SIGNALS || [];`
);

// Inject embedded data script before the main script
const embedTag = '<script>\nwindow.EMBEDDED_SIGNALS = ' + JSON.stringify(signals) + ';\n</script>\n';
html = html.replace('    <script>\n        // 전역 변수들', embedTag + '    <script>\n        // 전역 변수들');

fs.writeFileSync('invest-sns/signal-review.html', html);
console.log('Done! Embedded', signals.length, 'signals');
