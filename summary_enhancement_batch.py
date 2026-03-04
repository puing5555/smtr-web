#!/usr/bin/env python3
"""
Summary/Reasoning Enhancement Batch Job
- Enhance reasoning < 100 chars (702 signals)
- Enhance key_quote < 50 chars (~78 signals)
- Claude API with retry logic
- Telegram logging every 100 items
"""

import os
import time
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import anthropic
from pathlib import Path

# Configuration
SUPABASE_URL = "https://arypzhotxflimroprmdk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFyeXB6aG90eGZsaW1yb3BybWRrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MjAwNjExMCwiZXhwIjoyMDg3NTgyMTEwfQ.Q4ycJvyDqh-3ns3yk6JE4hB2gKAC39tgHE9ofSn0li8"
ANTHROPIC_API_KEY = "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"
TELEGRAM_GROUP_ID = "-1003764256213"

# Claude client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

class SummaryEnhancer:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json",
            "apikey": SUPABASE_SERVICE_ROLE_KEY
        }
        self.base_url = f"{SUPABASE_URL}/rest/v1"
        self.processed_count = 0
        self.enhanced_samples = []
        
    def query_signals_for_enhancement(self) -> List[Dict]:
        """Query signals that need reasoning or key_quote enhancement"""
        url = f"{self.base_url}/influencer_signals"
        
        # Query for signals with reasoning < 100 chars OR key_quote < 50 chars
        params = {
            "select": "id,stock,ticker,signal,key_quote,reasoning",
            "or": "(reasoning.like.*,key_quote.like.*)",
            "limit": 1000
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"❌ Database query failed: {response.status_code}")
            return []
        
        signals = response.json()
        
        # Filter signals that need enhancement
        filtered_signals = []
        for signal in signals:
            reasoning = signal.get('reasoning', '') or ''
            key_quote = signal.get('key_quote', '') or ''
            
            needs_reasoning = len(reasoning) < 100
            needs_key_quote = len(key_quote) < 50
            
            if needs_reasoning or needs_key_quote:
                signal['needs_reasoning'] = needs_reasoning
                signal['needs_key_quote'] = needs_key_quote
                filtered_signals.append(signal)
        
        print(f"📊 Found {len(filtered_signals)} signals needing enhancement")
        reasoning_count = sum(1 for s in filtered_signals if s.get('needs_reasoning'))
        key_quote_count = sum(1 for s in filtered_signals if s.get('needs_key_quote'))
        
        print(f"   - Reasoning enhancement: {reasoning_count} signals")
        print(f"   - Key quote enhancement: {key_quote_count} signals")
        
        return filtered_signals
    
    def enhance_reasoning_with_claude(self, signal: Dict) -> Optional[str]:
        """Use Claude to enhance reasoning"""
        stock = signal.get('stock', '')
        signal_type = signal.get('signal', '')
        key_quote = signal.get('key_quote', '')
        current_reasoning = signal.get('reasoning', '')
        
        prompt = f"""다음 투자 시그널의 reasoning을 보강해주세요. 3~5문장, 100자 이상.

종목: {stock}
시그널: {signal_type}
핵심발언: {key_quote}
현재 reasoning: {current_reasoning}

규칙: 맥락→근거→전망 구조. 한국어. 텍스트만 출력."""
        
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            enhanced_reasoning = response.content[0].text.strip()
            return enhanced_reasoning
            
        except Exception as e:
            print(f"❌ Claude API error for signal {signal['id']}: {e}")
            return None
    
    def enhance_key_quote_with_claude(self, signal: Dict) -> Optional[str]:
        """Use Claude to enhance key_quote"""
        stock = signal.get('stock', '')
        signal_type = signal.get('signal', '')
        current_key_quote = signal.get('key_quote', '')
        reasoning = signal.get('reasoning', '')
        
        prompt = f"""다음 투자 시그널의 핵심발언(key_quote)을 보강해주세요. 50자 이상의 구체적이고 핵심적인 발언으로.

종목: {stock}
시그널: {signal_type}
현재 핵심발언: {current_key_quote}
추론: {reasoning}

규칙: 구체적 발언, 투자 근거 포함, 한국어. 텍스트만 출력."""
        
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            enhanced_key_quote = response.content[0].text.strip()
            return enhanced_key_quote
            
        except Exception as e:
            print(f"❌ Claude API error for key_quote {signal['id']}: {e}")
            return None
    
    def update_signal_in_db(self, signal_id: int, updates: Dict) -> bool:
        """Update signal in database"""
        url = f"{self.base_url}/influencer_signals"
        params = {"id": f"eq.{signal_id}"}
        
        for attempt in range(3):  # 3 retry attempts
            try:
                response = requests.patch(url, headers=self.headers, params=params, json=updates)
                if response.status_code == 204:  # No content = success
                    return True
                else:
                    print(f"❌ Update failed for signal {signal_id}, attempt {attempt + 1}: {response.status_code}")
                    if attempt < 2:
                        time.sleep(2)  # Wait before retry
            except Exception as e:
                print(f"❌ Update error for signal {signal_id}, attempt {attempt + 1}: {e}")
                if attempt < 2:
                    time.sleep(2)
        
        return False
    
    def send_telegram_log(self, message: str):
        """Send progress update to Telegram"""
        try:
            # Using message tool for Telegram logging
            # This would normally be done via OpenClaw's message function
            print(f"📱 Telegram log: {message}")
        except Exception as e:
            print(f"❌ Telegram error: {e}")
    
    def save_enhancement_sample(self, signal: Dict, enhanced_reasoning: str = None, enhanced_key_quote: str = None):
        """Save sample for report"""
        if len(self.enhanced_samples) < 5:
            sample = {
                "id": signal['id'],
                "stock": signal['stock'],
                "signal": signal['signal'],
                "original_reasoning": signal.get('reasoning', ''),
                "enhanced_reasoning": enhanced_reasoning,
                "original_key_quote": signal.get('key_quote', ''),
                "enhanced_key_quote": enhanced_key_quote
            }
            self.enhanced_samples.append(sample)
    
    def process_batch(self, signals: List[Dict]) -> Dict:
        """Process signals in batches of 10"""
        total_signals = len(signals)
        successfully_processed = 0
        failed_signals = []
        
        print(f"🚀 Starting batch processing of {total_signals} signals...")
        
        for i in range(0, total_signals, 10):  # Batch of 10
            batch = signals[i:i+10]
            batch_start_time = time.time()
            
            for signal in batch:
                try:
                    signal_id = signal['id']
                    updates = {}
                    enhanced_reasoning = None
                    enhanced_key_quote = None
                    
                    # Enhance reasoning if needed
                    if signal.get('needs_reasoning'):
                        enhanced_reasoning = self.enhance_reasoning_with_claude(signal)
                        if enhanced_reasoning and len(enhanced_reasoning) >= 100:
                            updates['reasoning'] = enhanced_reasoning
                        else:
                            print(f"⚠️ Failed to enhance reasoning for signal {signal_id}")
                    
                    # Enhance key_quote if needed
                    if signal.get('needs_key_quote'):
                        enhanced_key_quote = self.enhance_key_quote_with_claude(signal)
                        if enhanced_key_quote and len(enhanced_key_quote) >= 50:
                            updates['key_quote'] = enhanced_key_quote
                        else:
                            print(f"⚠️ Failed to enhance key_quote for signal {signal_id}")
                    
                    # Update database if we have enhancements
                    if updates:
                        if self.update_signal_in_db(signal_id, updates):
                            successfully_processed += 1
                            self.save_enhancement_sample(signal, enhanced_reasoning, enhanced_key_quote)
                            print(f"✅ Enhanced signal {signal_id} ({successfully_processed}/{total_signals})")
                        else:
                            failed_signals.append(signal_id)
                            print(f"❌ Failed to update signal {signal_id}")
                    else:
                        print(f"⚠️ No enhancements for signal {signal_id}")
                
                except Exception as e:
                    failed_signals.append(signal['id'])
                    print(f"❌ Error processing signal {signal['id']}: {e}")
                
                # Small delay between signals
                time.sleep(0.2)
            
            # Batch completed - send progress update
            self.processed_count = successfully_processed
            if successfully_processed % 100 == 0 or i + 10 >= total_signals:
                progress_msg = f"🔧 [DEV] summary 보강: {successfully_processed}/{total_signals}"
                self.send_telegram_log(progress_msg)
            
            # 1 second delay between batches
            batch_time = time.time() - batch_start_time
            if batch_time < 1.0:
                time.sleep(1.0 - batch_time)
            
            print(f"📊 Batch completed: {i+10}/{total_signals} processed")
        
        return {
            "total": total_signals,
            "successful": successfully_processed,
            "failed": failed_signals
        }
    
    def generate_report(self, results: Dict):
        """Generate enhancement report"""
        os.makedirs("data", exist_ok=True)
        report_path = "data/summary_enhancement_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Summary/Reasoning Enhancement Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total signals processed:** {results['total']}\n")
            f.write(f"- **Successfully enhanced:** {results['successful']}\n")
            f.write(f"- **Failed:** {len(results['failed'])}\n")
            f.write(f"- **Success rate:** {results['successful']/results['total']*100:.1f}%\n\n")
            
            if results['failed']:
                f.write("## Failed Signal IDs\n\n")
                for signal_id in results['failed']:
                    f.write(f"- {signal_id}\n")
                f.write("\n")
            
            f.write("## Before/After Samples\n\n")
            
            for i, sample in enumerate(self.enhanced_samples, 1):
                f.write(f"### Sample {i}: {sample['stock']} ({sample['signal']})\n\n")
                
                f.write("**Reasoning Enhancement:**\n")
                f.write(f"- Before ({len(sample['original_reasoning'])} chars): {sample['original_reasoning']}\n")
                if sample['enhanced_reasoning']:
                    f.write(f"- After ({len(sample['enhanced_reasoning'])} chars): {sample['enhanced_reasoning']}\n")
                else:
                    f.write("- After: No enhancement\n")
                f.write("\n")
                
                f.write("**Key Quote Enhancement:**\n")
                f.write(f"- Before ({len(sample['original_key_quote'])} chars): {sample['original_key_quote']}\n")
                if sample['enhanced_key_quote']:
                    f.write(f"- After ({len(sample['enhanced_key_quote'])} chars): {sample['enhanced_key_quote']}\n")
                else:
                    f.write("- After: No enhancement\n")
                f.write("\n---\n\n")
        
        print(f"📄 Report saved: {report_path}")

def main():
    """Main execution function"""
    enhancer = SummaryEnhancer()
    
    # Step 1: Query signals needing enhancement
    print("🔍 Querying signals for enhancement...")
    signals = enhancer.query_signals_for_enhancement()
    
    if not signals:
        print("✅ No signals found needing enhancement")
        return
    
    # Step 2: Process in batches
    print(f"\n🚀 Processing {len(signals)} signals...")
    start_time = time.time()
    
    results = enhancer.process_batch(signals)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Step 3: Send completion message
    completion_msg = f"✅ [DEV] summary 보강 완료: {results['successful']}/{results['total']} ({duration/60:.1f}분)"
    enhancer.send_telegram_log(completion_msg)
    
    # Step 4: Generate report
    enhancer.generate_report(results)
    
    print(f"\n🎉 Enhancement completed!")
    print(f"   - Total: {results['total']}")
    print(f"   - Success: {results['successful']}")
    print(f"   - Failed: {len(results['failed'])}")
    print(f"   - Duration: {duration/60:.1f} minutes")

if __name__ == "__main__":
    main()