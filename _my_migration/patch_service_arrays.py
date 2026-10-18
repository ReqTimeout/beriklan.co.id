#!/usr/bin/env python3
"""F1-7 pass 3b: regenerate features (7 pages) + steps (9 pages) in English."""
import json, re, sys

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"
SVC = {s['slug']: s for s in json.load(open("/Users/maabook/Desktop/beriklan.my/web/src/data/services.json"))}

def esc(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

def js_steps(svc):
    rows = ["    { num: '%s', tag: '%s', title: '%s', desc: '%s' }," % (esc(t['num']), esc(t['tag']), esc(t['title']), esc(t['desc'])) for t in svc['how_steps']]
    return "const steps = [\n" + "\n".join(rows) + "\n];"

def js_features(items):
    rows = ["    { iconName: '%s', title: '%s', desc: '%s' }," % (i, esc(t), esc(d)) for i, t, d in items]
    return "const features = [\n" + "\n".join(rows) + "\n];"

FEATURES = {
 'google-ads-management': [
   ('Search', 'Keyword Research', 'A thorough analysis of relevant keywords: search volume, competition level and estimated cost per click. This becomes the foundation of the whole campaign.'),
   ('BarChart3', 'Conversion Tracking', 'Accurate Google Tag and conversion tracking setup, so we can see exactly which keywords actually generate leads \u2014 not just clicks.'),
   ('MapPin', 'Geographic Targeting', 'Limit delivery to specific cities or states \u2014 ideal for local businesses that only operate in a specific area.'),
   ('TrendingUp', 'Bidding Strategy', 'We pick the bidding strategy that fits: target CPA, maximise clicks or manual CPC \u2014 depending on your campaign objective.'),
   ('Eye', 'Negative Keywords', 'A negative keyword list that stops your ads showing for irrelevant searches \u2014 saving your budget significantly.'),
   ('Sparkles', 'Ad Extensions', 'Sitelink, callout and structured snippet extensions that make your ads more informative and lift CTR.'),
 ],
 'youtube-ads-management': [
   ('Video', 'Multiple Video Formats', 'Pick a format: 6-second bumper, 15-second non-skippable or 30-second skippable. Each plays a different role in the funnel.'),
   ('Target', 'Interest Targeting', 'Reach audiences by specific interest: beauty, parenting, automotive and 100+ other categories. Targeting down to fine detail.'),
   ('MapPin', 'Regional Targeting', 'Limit delivery to specific cities or states. Ideal for local businesses that only operate in a specific area.'),
   ('Sparkles', 'Placement Targeting', 'Choose the specific YouTube channels where your ads appear \u2014 for example only education channels, or only review channels.'),
   ('Eye', 'Keyword Targeting', 'Ads appear on videos containing specific keywords \u2014 a precise way to stay contextually relevant.'),
   ('TrendingUp', 'Brand Lift Measurement', 'On the Business plan, we measure brand lift to see the campaign\u2019s impact on how audiences perceive your brand.'),
 ],
 'instagram-management': [
   ('Camera', 'Feed Design', 'Every post goes through a visual design process that keeps your brand aesthetic consistent. Ideal for brands that want a professional-looking feed.'),
   ('Sparkles', 'Daily Stories', 'Stories posted routinely to stay visible among your followers. Interactive formats: polls, quizzes, Q&As, countdowns.'),
   ('Video', 'Short Reels', '15\u201330 second videos that follow trends while staying on-brand. Ideal for reaching new audiences via Explore.'),
   ('MessageCircle', 'DM Management', 'Our team replies to DMs and comments in a consistent brand tone. Fast responses build trust and conversion.'),
   ('BarChart3', 'Monthly Reports', 'Reports written in plain language: which posts performed, follower insights, reach, and strategy recommendations.'),
   ('Eye', 'Audience Insights', 'We analyse your Instagram audience: who they are, when they\u2019re active, and which content engages them most. This data drives the strategy.'),
 ],
 'tiktok-management': [
   ('Video', '15\u201330 Videos/Month', 'A consistent video volume: education, entertainment and reviews. We mix all three to keep variety high and the algorithm interested.'),
   ('Music2', 'Music Research', 'Research into the music and sounds trending in your industry. The right music can multiply a video\u2019s odds of hitting the FYP.'),
   ('Sparkles', 'Hook Copywriting', 'First-3-seconds copy that grabs attention. We write the hook for every video using proven formulas.'),
   ('TrendingUp', 'Hashtag Strategy', 'A relevant hashtag mix: branded, niche and trending. A strategy that gets your videos found by the right audience.'),
   ('BarChart3', 'Detailed Reports', 'Weekly or monthly reports: views, watch time, engagement, and iteration recommendations for the next batch of content.'),
   ('MessageCircle', 'Active Engagement', 'Our team replies to comments and DMs in your brand tone. Active engagement sends positive signals to the algorithm.'),
 ],
 'website-development': [
   ('Smartphone', 'Responsive Design', 'Your website renders perfectly on desktop, tablet and mobile. Today\u2019s industry standard \u2014 and a necessity.'),
   ('Zap', 'Fast Load Time', 'Optimised for speed: page loads under 3 seconds. A fast experience lifts both conversion and SEO ranking.'),
   ('Search', 'SEO Ready', 'Clean structure, proper meta tags and sitemaps from day one \u2014 so Google can find and rank your pages.'),
   ('Lock', 'SSL & Security', 'SSL certificate for HTTPS, uptime monitoring and routine backups. Your website stays secure and always reachable.'),
   ('Eye', 'Conversion Focused', 'Every element is designed to drive action: WhatsApp buttons, contact forms or a product catalogue.'),
   ('Layers', 'CMS (on selected plans)', 'The Corporate and E-commerce plans include a CMS so you can update content yourself \u2014 no coding needed.'),
 ],
 'landing-page-design': [
   ('Sparkles', 'Proven Copywriting', 'Headlines, sub-headlines and CTAs engineered for conversion. Copy matters just as much as design.'),
   ('Eye', 'Conversion-Focused Design', 'Every element steers visitors toward action: WhatsApp button, contact form or phone call.'),
   ('Search', 'Keyword Research', 'Analysis of relevant Google keywords: search volume, competition and the intent behind them.'),
   ('Target', 'Google Ads Targeting', 'Targeting by location, time, device and audience \u2014 matched to your business.'),
   ('BarChart3', 'Tracking & Analytics', 'Conversion tracking set up from day one. You see exactly which keywords bring in leads.'),
   ('TrendingUp', 'Ongoing Optimisation', 'For a full month we optimise keywords, copy and bidding strategy for the best results.'),
 ],
 'digital-marketing-agency': [
   ('Target', 'Omnichannel Strategy', 'An integrated cross-channel approach: paid ads, organic and conversion. Every channel reinforces the others.'),
   ('Sparkles', 'Strategy Consultation', 'An initial session to understand your business, audience and objectives \u2014 with a recommendation of the channels that fit best.'),
   ('Users', 'Specialist Team', 'One team of paid ads, organic and website specialists. No need to coordinate multiple agencies.'),
   ('BarChart3', 'Unified Reporting', 'Cross-channel reporting in one document: easy to read, with action recommendations for the next period.'),
   ('TrendingUp', 'Ongoing Optimisation', 'Every week we optimise: pause what underperforms, scale what works. Data drives every decision.'),
   ('MessageCircle', 'Regular Communication', 'Weekly updates via WhatsApp or email. Monthly reports via video call. You always know where the campaign stands.'),
 ],
}

STEPS_PAGES = ['instagram-ads-management', 'tiktok-ads-management', 'google-ads-management',
               'youtube-ads-management', 'instagram-management', 'tiktok-management',
               'website-development', 'landing-page-design', 'digital-marketing-agency']

for slug in STEPS_PAGES:
    fp = PAGES + slug + '.astro'
    s = open(fp, encoding='utf-8').read()
    s, n = re.subn(r'const steps = \[.*?\n\];', js_steps(SVC[slug]), s, count=1, flags=re.S)
    if n != 1: print('[%s] FATAL steps' % slug); sys.exit(1)
    if slug in FEATURES:
        s, n = re.subn(r'const features = \[.*?\n\];', js_features(FEATURES[slug]), s, count=1, flags=re.S)
        if n != 1: print('[%s] FATAL features' % slug); sys.exit(1)
    open(fp, 'w', encoding='utf-8').write(s)
    print('[%s] done' % slug)
print('ALL DONE')
