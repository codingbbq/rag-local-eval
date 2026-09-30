# documents.py
documents_content = {
    "unica_overview.txt": """UNICA CAMPAIGN OVERVIEW

Unica Campaign is a marketing automation platform with these key features:

1. Visual Campaign Designer
   - Drag-and-drop workflow builder
   - Pre-built components for email, SMS, push
   - Version control and campaign history

2. Audience Segmentation
   - Dynamic segments based on behavior and data
   - Real-time segment updates
   - Nested segments for advanced targeting

3. Multi-Channel Orchestration
   - Email marketing with personalization
   - SMS and push notifications
   - Web and social media integration

4. Real-Time Analytics
   - Campaign performance dashboard
   - Conversion tracking
   - ROI calculation per campaign

CAMPAIGN ARCHITECTURE
A campaign consists of:
- Entry: How contacts enter (batch, trigger, manual)
- Actions: What to do (send message, update profile)
- Decisions: Business logic (did they open? Are they premium?)
- Wait: Pause for time (wait 3 days, wait until Monday)
- Exit: When to remove from campaign
""",

    "unica_best_practices.txt": """UNICA CAMPAIGN BEST PRACTICES

CAMPAIGN DESIGN BEST PRACTICES

1. Define Clear KPIs
   - Choose primary KPI: Conversion, CTR, Engagement?
   - Set target metrics
   - Measure for full campaign duration

2. A/B Testing
   - Test one variable at a time
   - Minimum 10,000 contacts per test
   - Reach 95% statistical significance
   - Run full campaign before scaling

3. Test Small Before Scaling
   - Start with 5-10% of audience
   - Monitor for 24-48 hours
   - Check delivery, opt-outs, behavior
   - Scale to remaining contacts only if successful

4. Monitor Real-Time Performance
   - Set up live dashboards
   - Define alert thresholds
   - Daily reviews during campaigns
   - Be ready to pause if issues arise

PERFORMANCE OPTIMIZATION

1. Use Event-Based Triggers
   - Real-time triggers (purchase, website visit)
   - Time-based triggers (birthday, anniversary)
   - Behavioral triggers (abandoned cart)
   - Event-based is 3-5x more effective

2. Segment to Avoid Fatigue
   - Track contact frequency across all campaigns
   - Set maximum email caps (e.g., 5 per week)
   - Create do-not-mail lists
   - Use preference centers

3. Respect Preferences
   - Honor unsubscribes within 10 days
   - Maintain suppression lists
   - Provide preference centers
   - Monitor bounce rates (> 5% is concerning)

4. Clean Data Regularly
   - Validate emails before import
   - Remove duplicates
   - Update records as they change
   - Run data quality checks quarterly

COMMON ISSUES

Issue: Message Duplication
Solutions:
- Add wait periods between similar campaigns
- Deduplicate segment logic
- Monitor campaign overlap
- Check batch reprocessing

Issue: Low Engagement
Solutions:
- A/B test messaging
- Test different send times
- Simplify design
- Segment by engagement level

Issue: High Bounce Rates
Solutions:
- Validate email lists
- Only send to active subscribers
- Configure SPF/DKIM
- Implement gradual ramp-up

Issue: Unsubscribe Spikes
Solutions:
- Review message relevance
- Check send frequency
- Verify targeting
- Analyze unsubscribe feedback
"""
}

def create_documents():
    """Create sample documents"""
    for filename, content in documents_content.items():
        with open(filename, 'w') as f:
            f.write(content)
        print(f"✓ Created {filename}")

if __name__ == "__main__":
    create_documents()
    print("\n✓ All documents created!")