#!/usr/bin/env python3
"""F1-7c: full English rewrite of legal pages (terms, disclaimer, privacy)."""
import io

PAGES = "/Users/maabook/Desktop/beriklan.my/web/src/pages/"

TERMS = '''---
import Layout from '../layouts/Layout.astro';
import Navbar from '../components/Navbar.svelte';
import Footer from '../components/Footer.svelte';
import StickyCTA from '../components/StickyCTA.svelte';

const lastUpdated = "14 July 2026";
---

<Layout
    title="Terms of Service — Beriklan.my"
    description="Terms of service for Beriklan.my digital advertising services. Applies to professional clients, SMEs and corporations. Contact legal@beriklan.my with any questions."
    canonical="https://beriklan.my/terms-of-service/"
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <article class="pt-28 md:pt-44 pb-20 bg-gradient-to-br from-white via-soft to-beige">
        <div class="container mx-auto px-6 max-w-3xl">
            <div class="bg-white rounded-2xl p-8 md:p-12 shadow-soft border border-gray-100 prose-content">

                <header class="mb-10 pb-8 border-b border-gray-100">
                    <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Legal</p>
                    <h1 class="font-display font-extrabold text-3xl md:text-4xl text-ink mb-3">Terms of Service</h1>
                    <p class="text-sm text-muted">Last updated: <strong>{lastUpdated}</strong></p>
                </header>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">1. Acceptance of Terms</h2>
                    <p>
                        By using the services of Beriklan.my ("Beriklan"), you agree to these
                        terms of service. If you do not agree, please do not use our services.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">2. Services</h2>
                    <p>Beriklan provides:</p>
                    <ul>
                        <li>Digital advertising management: Meta Ads, Google Ads, TikTok Ads, YouTube Ads.</li>
                        <li>Organic content management: Instagram, TikTok.</li>
                        <li>Website & landing page development.</li>
                        <li>Digital marketing strategy consulting.</li>
                    </ul>
                    <p>Specific services, deliverables and pricing are agreed in a separate <strong>service agreement</strong>.</p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">3. Client Responsibilities</h2>
                    <ul>
                        <li>Provide full access to your ad accounts (Meta Business, Google Ads, TikTok Ads, YouTube)</li>
                        <li>Approve the strategy before execution</li>
                        <li>Pay fees according to the agreed schedule</li>
                        <li>Provide creative materials, or approve the materials we produce</li>
                        <li>Not use the ad accounts for anything outside the agreed scope of work</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">4. Payments & Fees</h2>
                    <ul>
                        <li>The management fee is separate from your ad budget (the amount spent on the ad platforms).</li>
                        <li>Fees are invoiced monthly, due on the 5th of each month via bank transfer.</li>
                        <li>Ad budget is paid directly into the client's own ad account (or via another agreed method).</li>
                        <li>Payments overdue by more than 14 days: campaigns may be paused without prior notice.</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">5. Guarantees & Results Disclaimer</h2>
                    <p>
                        <strong>There is no numerical guarantee</strong> of results (number of leads,
                        conversions, revenue) because outcomes depend on many factors outside our
                        control: your niche, product quality, pricing, landing page and market
                        conditions. What we do guarantee is:
                    </p>
                    <ul>
                        <li>Campaign setup according to platform best practices</li>
                        <li>Transparent weekly reports</li>
                        <li>Weekly, data-driven iteration</li>
                        <li>Full dashboard access so you can monitor everything yourself</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">6. Engagement & Termination</h2>
                    <ul>
                        <li>Engagements run on <strong>30-day cycles</strong> — there is no long-term lock-in contract.</li>
                        <li>To stop, simply give notice before the next cycle begins; you are never charged for cycles that have not started.</li>
                        <li>Fees for a cycle already in progress remain payable in full.</li>
                        <li>When the engagement ends: we hand over all assets in full (ad accounts, landing page source, creatives).</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">7. Intellectual Property</h2>
                    <ul>
                        <li>Creatives, copy and strategies we produce for you belong to you once payment is settled.</li>
                        <li>Beriklan's internal frameworks, methodologies and tools remain the property of Beriklan.</li>
                        <li>Case studies and campaign results may be used in Beriklan's portfolio only with your written consent.</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">8. Limitation of Liability</h2>
                    <p>
                        Beriklan's total liability to you in any event will not exceed the fees
                        paid in the most recent 3 months. We are not liable for indirect or
                        consequential losses, or for reputational damage.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">9. Governing Law</h2>
                    <p>
                        These terms are governed by the laws of the Republic of Indonesia, where
                        Beriklan Digital Agency is incorporated. Any dispute will first be resolved
                        amicably and, failing that, through the Bandung District Court.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">10. Legal Contact</h2>
                    <div class="bg-soft p-5 rounded-xl">
                        <p class="mb-1"><strong>Legal · Beriklan Digital Agency</strong></p>
                        <p class="mb-1">Jl. Arcamanik Endah No.76, Bandung 40195, Indonesia</p>
                        <p>Email: <a href="mailto:legal@beriklan.my" class="text-accent hover:underline">legal@beriklan.my</a></p>
                    </div>
                </section>

            </div>
        </div>
    </article>

    <Footer client:only="svelte" />
</Layout>

<style is:global>
    .prose-content h2 { margin-top: 2rem; }
    .prose-content ul { list-style: disc; padding-left: 1.5rem; margin: 1rem 0; }
    .prose-content ul li { margin-bottom: 0.5rem; line-height: 1.65; color: #4b5563; }
    .prose-content p { line-height: 1.75; color: #4b5563; margin: 1rem 0; }
    .prose-content strong { color: #0b1426; }
    .prose-content a { color: #f59e0b; }
</style>
'''

DISCLAIMER = '''---
import Layout from '../layouts/Layout.astro';
import Navbar from '../components/Navbar.svelte';
import Footer from '../components/Footer.svelte';
import StickyCTA from '../components/StickyCTA.svelte';

const lastUpdated = "14 July 2026";
---

<Layout
    title="Disclaimer — Beriklan.my"
    description="Beriklan.my service disclaimer: not financial advice, campaign results depend on many factors, no numerical guarantees."
    canonical="https://beriklan.my/disclaimer/"
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <article class="pt-28 md:pt-44 pb-20 bg-gradient-to-br from-white via-soft to-beige">
        <div class="container mx-auto px-6 max-w-3xl">
            <div class="bg-white rounded-2xl p-8 md:p-12 shadow-soft border border-gray-100 prose-content">

                <header class="mb-10 pb-8 border-b border-gray-100">
                    <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Legal</p>
                    <h1 class="font-display font-extrabold text-3xl md:text-4xl text-ink mb-3">Disclaimer</h1>
                    <p class="text-sm text-muted">Last updated: <strong>{lastUpdated}</strong></p>
                </header>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">1. Not Financial Advice</h2>
                    <p>
                        The content on <strong>beriklan.my</strong> — including blog articles, case
                        studies, testimonials and other materials — is <strong>educational and
                        informational</strong> in nature, not professional financial advice. Business
                        investment decisions, ad budget allocation and marketing strategy remain your
                        own responsibility. Consult a trusted business adviser before making decisions
                        based on information from this website.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">2. No Guarantee of Results</h2>
                    <p>
                        Beriklan does not guarantee any specific number of prospects, leads,
                        conversions or revenue from ad campaigns. Results depend on many factors:
                    </p>
                    <ul>
                        <li>Industry niche and competitors</li>
                        <li>Product / service quality and pricing</li>
                        <li>Landing page and website quality</li>
                        <li>Target audience and targeting</li>
                        <li>Market conditions and seasonality</li>
                        <li>Ad budget versus market expectations</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">3. Testimonials & Case Studies</h2>
                    <p>
                        The testimonials and case studies shown on this website come from real
                        clients who gave permission to publish. Names and figures have been
                        simplified to protect client privacy. Each testimonial reflects an
                        individual experience — not a guarantee of the same result for you.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">4. Platform Changes</h2>
                    <p>
                        Ad platforms (Meta, Google, TikTok, YouTube) may change their algorithms,
                        features and policies at any time without notice. We are not responsible
                        for such changes and any impact they may have on your campaign performance.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">5. External Links</h2>
                    <p>
                        This website may contain links to third-party websites. We are not
                        responsible for the content, privacy policies or practices of those
                        third parties.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">6. Use of Content</h2>
                    <p>
                        Articles and materials on the Beriklan blog may be cited with attribution
                        and a link back to the original article. Commercial reproduction without
                        written permission is not allowed.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">7. YMYL Compliance</h2>
                    <p>
                        Some topics (ad budgets, ROAS, financial matters) may be considered YMYL
                        (Your Money Your Life) under Google's Quality Rater guidelines. We include
                        this disclaimer as mitigation. For significant financial decisions, always
                        consult a licensed professional.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">8. Contact</h2>
                    <div class="bg-soft p-5 rounded-xl">
                        <p class="mb-1"><strong>Questions about this disclaimer:</strong></p>
                        <p>Email: <a href="mailto:legal@beriklan.my" class="text-accent hover:underline">legal@beriklan.my</a></p>
                    </div>
                </section>

            </div>
        </div>
    </article>

    <Footer client:only="svelte" />
</Layout>

<style is:global>
    .prose-content h2 { margin-top: 2rem; }
    .prose-content ul { list-style: disc; padding-left: 1.5rem; margin: 1rem 0; }
    .prose-content ul li { margin-bottom: 0.5rem; line-height: 1.65; color: #4b5563; }
    .prose-content p { line-height: 1.75; color: #4b5563; margin: 1rem 0; }
    .prose-content strong { color: #0b1426; }
    .prose-content a { color: #f59e0b; }
</style>
'''

PRIVACY = '''---
import Layout from '../layouts/Layout.astro';
import Navbar from '../components/Navbar.svelte';
import Footer from '../components/Footer.svelte';
import StickyCTA from '../components/StickyCTA.svelte';

const lastUpdated = "14 July 2026";
const schema = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "Beriklan.my Privacy Policy",
    "description": "How Beriklan.my collects, uses and protects your personal data.",
    "dateModified": "2026-07-14"
};
---

<Layout
    title="Privacy Policy — Beriklan.my | PDPA & GDPR Compliance"
    description="Beriklan.my privacy policy aligned with Malaysia's PDPA 2010 and the GDPR. Rights of access, correction and erasure. DPO contact: dpo@beriklan.my."
    canonical="https://beriklan.my/privacy-policy/"
>
    <Navbar client:only="svelte" />
    <StickyCTA client:only="svelte" />

    <article class="pt-28 md:pt-44 pb-20 bg-gradient-to-br from-white via-soft to-beige">
        <div class="container mx-auto px-6 max-w-3xl">
            <div class="bg-white rounded-2xl p-8 md:p-12 shadow-soft border border-gray-100 prose-content">

                <header class="mb-10 pb-8 border-b border-gray-100">
                    <p class="text-xs font-bold uppercase tracking-[0.2em] text-accent mb-3">Legal</p>
                    <h1 class="font-display font-extrabold text-3xl md:text-4xl text-ink mb-3">Privacy Policy</h1>
                    <p class="text-sm text-muted">Last updated: <strong>{lastUpdated}</strong></p>
                </header>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">1. Introduction</h2>
                    <p>
                        Beriklan Digital Agency ("Beriklan", "we", "us") respects the privacy of
                        every visitor to <strong>beriklan.my</strong>. This policy explains what
                        data we collect, how we use it, and your rights as a user under
                        <strong>Malaysia's Personal Data Protection Act 2010 (PDPA)</strong>,
                        <strong>Indonesia's Personal Data Protection Law No. 27/2022</strong>
                        (where we are incorporated) and the <strong>GDPR</strong> for
                        European Union users.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">2. Data We Collect</h2>
                    <ul>
                        <li><strong>Data you provide directly:</strong> name, WhatsApp number, email address, business/brand name, and relevant information when you fill in an inquiry form or contact us.</li>
                        <li><strong>Automatic data:</strong> IP address, browser, device type, pages visited, visit duration, referrer — collected via Cloudflare Web Analytics & Google Analytics.</li>
                        <li><strong>Cookies:</strong> for advertising (Google AdSense), analytics and preferences. You can manage these through the consent banner.</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">3. How We Use Your Data</h2>
                    <ul>
                        <li>Responding to inquiries and consultations</li>
                        <li>Managing ad campaigns (Meta, Google, TikTok) on your behalf</li>
                        <li>Sending weekly reports via WhatsApp/email</li>
                        <li>Improving our services & website content</li>
                        <li>Google AdSense ad personalisation (cookie consent)</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">4. Storage & Retention</h2>
                    <ul>
                        <li>Inquiry data (WhatsApp / form): <strong>90 days</strong> after the last inquiry, unless an active engagement exists.</li>
                        <li>Active client data: for the duration of the engagement + 2 years afterwards (for tax obligations).</li>
                        <li>Analytics (aggregated, anonymous): <strong>24 months</strong>.</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">5. Third Parties (Processors)</h2>
                    <ul>
                        <li><strong>Cloudflare</strong> — CDN & Workers (hosting)</li>
                        <li><strong>GitHub</strong> — code repository</li>
                        <li><strong>Google</strong> — AdSense, Analytics, Tag Manager</li>
                        <li><strong>Meta (Facebook)</strong>, <strong>TikTok</strong> — ad platforms for clients</li>
                        <li><strong>OpenAI / Google Gemini</strong> — AI content generation (data not used for training)</li>
                    </ul>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">6. Your Rights</h2>
                    <p>You have the right to:</p>
                    <ul>
                        <li><strong>Access</strong> — request a copy of your personal data</li>
                        <li><strong>Correction</strong> — update inaccurate data</li>
                        <li><strong>Erasure</strong> — request deletion of your data (right to be forgotten)</li>
                        <li><strong>Restrict processing</strong></li>
                        <li><strong>Data portability</strong> — receive your data in a structured format</li>
                        <li><strong>Withdraw consent</strong> — at any time, without affecting prior processing</li>
                    </ul>
                    <p>To exercise these rights, contact <strong>dpo@beriklan.my</strong> with the subject "Personal Data Request". We respond within 7 working days.</p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">7. Data Security</h2>
                    <p>
                        We apply common industry security standards: HTTPS/TLS for all transmissions,
                        database access restricted to the team that needs it, encrypted daily backups,
                        and periodic audits.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">8. Children's Data</h2>
                    <p>
                        Our services are not intended for anyone under 17 years old. We do not
                        knowingly collect children's personal data. If you believe we hold data
                        about a child, contact <strong>dpo@beriklan.my</strong> for deletion.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">9. Changes to This Policy</h2>
                    <p>
                        We may update this policy from time to time. The latest version is always
                        available on this page with the update date shown above. For material
                        changes, we will notify you via a banner on the website or by email.
                    </p>
                </section>

                <section class="mb-8">
                    <h2 class="font-display font-bold text-xl text-ink mb-3">10. DPO Contact</h2>
                    <div class="bg-soft p-5 rounded-xl">
                        <p class="mb-1"><strong>Beriklan Digital Agency</strong></p>
                        <p class="mb-1">Jl. Arcamanik Endah No.76, Bandung 40195, Indonesia</p>
                        <p class="mb-1">Email: <a href="mailto:dpo@beriklan.my" class="text-accent hover:underline">dpo@beriklan.my</a></p>
                        <p>WhatsApp: <a href="https://wa.me/62811919328" class="text-accent hover:underline">+62 81-1919-328</a></p>
                    </div>
                </section>

            </div>
        </div>
    </article>

    <Footer client:only="svelte" />
</Layout>

<script type="application/ld+json" set:html={JSON.stringify(schema)} />

<style is:global>
    .prose-content h2 { margin-top: 2rem; }
    .prose-content ul { list-style: disc; padding-left: 1.5rem; margin: 1rem 0; }
    .prose-content ul li { margin-bottom: 0.5rem; line-height: 1.65; color: #4b5563; }
    .prose-content p { line-height: 1.75; color: #4b5563; margin: 1rem 0; }
    .prose-content strong { color: #0b1426; }
    .prose-content a { color: #f59e0b; }
    .prose-content a:hover { color: #d97706; text-decoration: underline; }
</style>
'''

for fname, content in [
    ('terms-of-service.astro', TERMS),
    ('disclaimer.astro', DISCLAIMER),
    ('privacy-policy.astro', PRIVACY),
]:
    with io.open(PAGES + fname, 'w', encoding='utf-8') as f:
        f.write(content)
    print('WROTE %s (%d lines)' % (fname, content.count('\n')))
print('DONE legal pages')
