# FAUE — Revised MVP Documentation

## Fashion Intelligence Platform for African Style

**Version:** 1.0 — Revised MVP
**Date:** May 2026
**Status:** Pre-build validation phase

---

## 1. Executive Summary

FAUE is a fashion intelligence platform that helps African fashion consumers discover outfits, style fabrics for bespoke tailoring, and shop across multiple brands — all personalized to their taste, body, and cultural context.

This document defines the revised MVP scope. The original vision included seven major features (wardrobe management, cross-brand recommendations, virtual try-on, bespoke styling, brand dashboards, subscriptions, and a Spree Assistant). This revision strips to the minimum feature set that preserves FAUE's core identity while eliminating the two-sided marketplace cold start problem, reducing build time from 12 weeks to 4 weeks, and isolating the single most important assumption for testing.

The revised MVP tests one core loop:

**Style DNA Quiz → Personalized Recommendations (RTW + Bespoke) → Action (Shop or Send to Tailor) → Return**

---

## 2. Problem Statement

### The Pain

African fashion consumers face a fragmented, frustrating styling experience:

- **For ready-to-wear:** Discovery is scattered across dozens of brand Instagram pages with no way to see cross-brand outfit combinations. Finding pieces that match your style means hours of scrolling with no intelligent filtering.
- **For bespoke/fabric:** The gap between "I bought fabric" and "I know what to tell my tailor" is filled by chaotic Pinterest/Instagram browsing, screenshots sent to WhatsApp groups, and miscommunication with tailors that leads to wasted money.
- **For both:** No platform understands the Nigerian fashion context — Owambe dress codes, Aso-Ebi coordination, native-to-corporate style switching, or fabric-specific style constraints.

### Who Feels It Most

The primary early adopter is a fashion-conscious Nigerian professional (age 22-35) who attends social events regularly, buys fabric for bespoke tailoring 2-6 times per year, and spends ₦30,000-80,000 per event on the complete look (fabric + tailoring + accessories). They currently use Instagram, Pinterest, and WhatsApp groups to make styling decisions and are frustrated by how long it takes and how often the outcome disappoints.

### Why Now

- Nigerian fashion e-commerce is growing but still fragmented across individual brand websites and Instagram storefronts
- AI-powered recommendation and image understanding technology has matured enough to handle fabric pattern analysis and style matching
- No existing platform combines cross-brand discovery with bespoke/fabric styling intelligence in the African context

---

## 3. Core Assumption

> If you show someone a set of outfit recommendations and fabric style suggestions that are personalized to their taste (via Style DNA), culturally relevant, and immediately actionable (shop links + tailor-ready shares), they will act on them and return for the next styling need.

Everything in this MVP exists to test this assumption. Every feature that doesn't directly test it has been cut.

---

## 4. What Stays vs. What Gets Cut

### Features Included in MVP

| Feature | Why It Stays |
|---|---|
| Style DNA Quiz | Onboarding hook, generates personalization context, shareable (viral potential), solves cold start without requiring wardrobe uploads |
| Cross-Brand Outfit Recommendations | Core value proposition — FAUE's reason for existing. Catalog is self-curated, no brand partnerships needed at launch |
| Fabric/Bespoke Style Suggestions | Strongest differentiator. No competitor does "upload fabric → get specific style recommendations for that fabric type." This is the painkiller use case |
| "Shop This Look" (affiliate links) | Tests purchase intent without building commerce infrastructure |
| "Send to Tailor" (WhatsApp share) | Tests actionability of bespoke suggestions. Completes the fabric-to-tailor loop |
| Simple User Accounts | Email/phone login, save favorites. Enables return visit tracking |
| Light Wardrobe Input (checkboxes) | "Tell us what you already own" as simple checkboxes during the quiz — not photo uploads. Enough to personalize recommendations without the friction |

### Features Cut from MVP (Deferred to Post-Validation)

| Feature | Why It's Cut | When It Returns |
|---|---|---|
| Digital Wardrobe (photo upload) | Highest friction feature. Photo-based wardrobe apps consistently fail on upload adoption, especially on slower mobile connections | Month 2 — if engagement holds without it |
| Virtual Try-On (VTO) | Impressive technology but doesn't test whether recommendations drive action. Adds significant build complexity | Month 2 — as a retention booster |
| Brand Dashboard | Requires brand partnerships on day one, creating a two-sided cold start. Self-curated catalog eliminates this dependency | Month 3 — after proving traffic to brands with data |
| Subscription Tiers / Payment | Testing value, not monetization. Premature pricing gates will suppress the engagement data needed to validate | Month 3-4 — after proving retention |
| Spree Assistant | Phase 2 feature. Event-specific shopping guidance requires a working recommendation engine first | Month 4+ |
| Brand Analytics | No brands on platform yet. Analytics for a self-curated catalog adds no value | Month 3 — alongside Brand Dashboard |

---

## 5. Feature Specifications

### 5.1 Style DNA Quiz

**Purpose:** Replace wardrobe uploads as the primary personalization signal. Generate enough user context to power relevant recommendations from the first session.

**Flow:**
1. User opens FAUE → lands on onboarding → taps "Get Started"
2. Quiz presents 10 questions covering: style archetype (minimalist, maximalist, eclectic, classic), color palette preferences, body comfort zones, occasion mix (corporate vs. casual vs. event ratio), fabric preferences (Ankara, Lace, Cotton, Denim), native style affinity (Agbada, Kaftan, Senator, Buba & Iro), brand awareness level, budget range, and lifestyle context
3. Questions use visual selection (tap on images) where possible, not text-heavy dropdowns
4. On completion: user receives a "Style DNA Card" — a shareable visual summary of their style profile

**Viral Mechanism:** The Style DNA Card is designed to be screenshot-worthy and shareable on Instagram Stories, Twitter, and WhatsApp Status. It should feel like a personality quiz result — something people post and compare with friends.

**Technical Notes:**
- Quiz responses are converted to a multi-dimensional style vector
- This vector is used for embedding similarity matching against the product catalog
- Quiz can be retaken at any time to update preferences

**Light Wardrobe Input:** At the end of the quiz, a single optional screen: "What do you already own?" with icon-based checkboxes (dark jeans, white sneakers, blazer, Agbada, etc.). No photos. 15-20 common items. This informs recommendations to avoid suggesting duplicates and to build on what the user has.

### 5.2 Cross-Brand Outfit Recommendations

**Purpose:** Show users complete outfit combinations pulled from multiple brands, personalized to their Style DNA.

**How It Works (Without Brand Partnerships):**
- FAUE team manually curates a product catalog of 500-1,000 items from 10-15 Nigerian fashion brands
- Products are sourced from public brand websites and Instagram pages — with full attribution and direct links
- Each product is tagged with: category, color, fabric type, occasion suitability, style archetype match, price range, and brand
- CLIP embeddings are generated for all product images
- Recommendation engine: Style DNA vector → embedding similarity → outfit assembly with color/style/occasion compatibility rules

**Output:**
- Feed of 10+ outfit combinations, each showing 3-5 items from across brands
- Each outfit tagged with occasion suitability (Owambe, Corporate, Casual, Date Night)
- Each item shows: product image, brand name, price, and "Shop This" button (affiliate link to brand's site)
- Users can save/favorite outfits
- "More like this" and "Not my style" feedback buttons to refine future recommendations

**Initial Brand Catalog Targets (10-15 brands, self-curated):**
- Mix of RTW brands across price points: accessible (₦5k-15k items), mid-range (₦15k-40k), premium (₦40k+)
- Include both menswear and womenswear brands
- Include accessory brands (shoes, bags, jewelry)
- Priority: brands with active online stores where affiliate links can drive trackable conversions

### 5.3 Fabric/Bespoke Style Suggestions

**Purpose:** Solve the "I bought fabric, now what do I sew?" problem — FAUE's strongest differentiator.

**Flow:**
1. User taps "Style My Fabric" from the home screen
2. Uploads a photo of their fabric (camera or gallery)
3. Selects fabric type if not auto-detected: Ankara, Lace, Aso-Oke, Adire, Cotton, Chiffon
4. Optionally specifies: occasion (Owambe, Wedding, Church, Corporate), gender, and any constraints ("I want something modest" / "I want to stand out")
5. Receives 3-5 style suggestions, each showing:
   - Style name (e.g., "Fitted Kaftan with Side Slit")
   - Reference image of the style on a similar fabric type
   - Why it works for this fabric ("This Ankara pattern has large motifs — a Kaftan lets the pattern breathe without cutting through the design")
   - Accessory pairings: 2-3 accessories per style (shoes, bag, jewelry) with "Shop This" links
6. User selects preferred style → taps "Send to Tailor"
7. "Send to Tailor" generates a WhatsApp-shareable image containing: the fabric photo, the chosen style reference image, key measurements/notes, and FAUE branding

**Style Library (MVP):**
- 30 curated native styles across menswear and womenswear
- Each style has 3-5 reference images showing it on different fabric types
- Each style is tagged with: fabric suitability (which fabrics work/don't work), occasion match, formality level, and body type notes
- Style-to-fabric matching is rule-based for MVP (e.g., heavyweight Aso-Oke → structured styles like Agbada; lightweight Chiffon → flowing styles like Boubou). No ML required for 30 styles.

**Accessory Pairing Database:**
- 20-30 accessories manually matched to styles
- Each accessory has: image, brand, price, and affiliate link
- Pairings are occasion-aware (gold jewelry for Owambe, minimal accessories for corporate)

### 5.4 Action Layer

**"Shop This Look" Button:**
- Present on every recommended outfit item and every bespoke accessory suggestion
- Links directly to the product page on the brand's website
- Tracks: click-through rate (CTR) per item, per brand, per outfit
- This is the primary revenue validation signal — if nobody clicks, the recommendation quality isn't high enough

**"Send to Tailor" Button:**
- Present on every bespoke style suggestion
- Generates a clean, branded image containing: fabric photo + style reference + style name + optional notes
- Opens WhatsApp share sheet with the image pre-attached
- Tracks: share rate, which styles get shared most, repeat usage

### 5.5 User Accounts

**Scope (MVP):**
- Sign up with email or phone number (OTP verification)
- Save/favorite outfits and style suggestions
- Style DNA profile stored and editable
- Basic activity history (saved items, shared styles)

**Not in MVP:**
- Social features (following, sharing profiles)
- User-generated content
- Community features

---

## 6. Technical Architecture (MVP)

### Stack

| Layer | Technology | Rationale |
|---|---|---|
| Frontend | React (Next.js), Tailwind CSS | Mobile-first responsive web app. No native app for MVP — reduces build time and enables instant iteration |
| Backend | FastAPI (Python) | Lightweight, fast, and native to ML ecosystem. Handles API, auth, and recommendation logic |
| Database | PostgreSQL + pgvector | Relational data (users, products, styles) + vector similarity search for recommendations in one database |
| Image Storage | Cloudinary | Fabric photo uploads, product images, generated share images. CDN-backed, transformation API for "Send to Tailor" image generation |
| Embeddings | CLIP (OpenAI) via HuggingFace | Generate embeddings for product images and fabric photos. Pre-compute product embeddings, compute fabric embeddings on upload |
| Auth | NextAuth.js or custom JWT | Email/phone OTP login |
| Analytics | Mixpanel or PostHog | Event tracking: quiz completion, recommendation views, saves, clicks, shares, returns |
| Hosting | Vercel (frontend) + Railway or Render (backend) | Fast deployment, reasonable free/low-cost tiers for MVP scale |

### Data Pipeline

```
User completes Style DNA Quiz
        ↓
Quiz responses → Style Vector (multi-dimensional)
        ↓
Style Vector → pgvector similarity search against product embeddings
        ↓
Top matches → Outfit Assembly Engine (compatibility rules: color, occasion, category mix)
        ↓
Assembled outfits → Ranked by relevance score → Displayed in feed
```

```
User uploads fabric photo
        ↓
Fabric photo → CLIP embedding + fabric type classification
        ↓
Fabric type → Rule-based style matching (30 styles, tagged by fabric suitability)
        ↓
Top 3-5 styles → Accessory pairing lookup → Display with "Send to Tailor"
```

### Key Technical Decisions

- **No ML model training for MVP.** Use pre-trained CLIP for embeddings and rule-based logic for style matching. ML models for fabric analysis and recommendation ranking come in Month 2-3 after collecting user interaction data.
- **Web app, not native.** A responsive web app can be shared via link (critical for WhatsApp virality), doesn't require app store approval, and can be iterated on daily. Native apps come after product-market fit.
- **Self-curated catalog, not API integrations.** Manually adding 500-1,000 products is faster than building and maintaining API integrations with 15 different brand backends (most of which don't have APIs). The catalog is a spreadsheet that gets imported.

---

## 7. Product Catalog Strategy

### Curation Process

1. Identify 10-15 Nigerian fashion brands with active online stores
2. For each brand, photograph/screenshot 50-100 products from their website and Instagram
3. For each product, record: name, brand, category, price, color(s), fabric type, occasion tags, direct purchase URL
4. Generate CLIP embeddings for all product images
5. Import into PostgreSQL with pgvector

### Catalog Maintenance

- Weekly refresh: check for sold-out items, add new arrivals from priority brands
- Track which brands' products get the most saves and clicks — double down on those catalogs
- Target: 500 products at launch, 1,000 by end of Month 1

### Why This Works Without Brand Partnerships

FAUE is functioning as a fashion recommendation and affiliate platform, not a marketplace. You're linking to brands' own stores — they benefit from the traffic. No permission is needed to recommend publicly listed products and link to them. This is how every fashion blog, Pinterest board, and affiliate site operates. When you have data showing you drove X clicks and Y purchases to a brand, that's when you approach them for a formal partnership (catalog access, affiliate commission, dashboard).

---

## 8. Metrics & Success Criteria

### Primary Metrics (Must-hit for validation)

| Metric | Target | Measurement |
|---|---|---|
| Quiz Completion Rate | 60%+ of users who start the quiz finish it | Analytics: quiz_started vs quiz_completed events |
| Recommendation Save Rate | 15%+ of users save at least one outfit | Analytics: save_outfit events / active_users |
| "Shop This" Click Rate | 10%+ of users click at least one affiliate link | Analytics: shop_click events / active_users |
| "Send to Tailor" Share Rate | 10%+ of fabric uploaders share to WhatsApp | Analytics: share_tailor events / fabric_uploaded events |
| 14-Day Return Rate | 20%+ of users return within 14 days without prompting | Analytics: returning_users / total_users (exclude push/email driven) |
| Style DNA Card Share Rate | 5%+ share their card on social media | Analytics: share_dna events / quiz_completed events |

### Secondary Metrics (Informational, not gating)

| Metric | What It Tells You |
|---|---|
| Fabric upload rate | Whether bespoke styling is a pull feature or needs promotion |
| Average outfits viewed per session | Whether the recommendation feed is engaging enough to browse |
| Most-saved brands | Which brands to prioritize for partnership outreach |
| Most-shared bespoke styles | Which styles to expand reference images for |
| Accessory click rate vs. main item click rate | Whether accessory pairing adds purchase intent |

### Disproof Signals (Stop and reassess if these occur)

- Quiz completion below 40% — the quiz is too long, too confusing, or not compelling enough
- Recommendation save rate below 5% — recommendations aren't relevant to users' taste
- Zero "Send to Tailor" shares in the first 50 fabric uploads — the bespoke output isn't actionable
- Zero unprompted returns in 30 days — no habit is forming, the product is a one-time novelty
- Zero social shares of Style DNA cards — the viral loop is broken

---

## 9. Build Timeline — 4 Weeks

### Week 1: Foundation + Content

**Engineering:**
- Set up Next.js project with Tailwind CSS, deploy to Vercel
- Set up FastAPI backend, deploy to Railway/Render
- PostgreSQL + pgvector database schema: users, products, styles, quiz_responses, saved_outfits, fabric_uploads
- User auth: email/phone OTP login flow
- Style DNA Quiz: frontend (10 visual-selection screens) + backend (response → style vector computation)

**Content/Catalog:**
- Identify and list 10-15 target brands
- Begin product curation: photograph/scrape first 300 products
- Tag each product: category, color, fabric, occasion, price, URL
- Curate bespoke style library: first 15 native styles with 3-5 reference images each

### Week 2: Core Engine

**Engineering:**
- Generate CLIP embeddings for all curated products
- Build recommendation engine: style vector → product similarity → outfit assembly
- Outfit assembly rules: ensure category diversity (top + bottom + shoes + accessory), color compatibility, occasion matching
- Build recommendation feed UI: outfit cards, save button, "Shop This" links
- Style DNA Card generator: shareable image from quiz results

**Content/Catalog:**
- Complete product catalog to 500+ items
- Complete bespoke style library to 30 styles
- Build accessory pairing database: 20-30 accessories matched to styles

### Week 3: Bespoke Flow + Polish

**Engineering:**
- Fabric upload flow: camera/gallery → Cloudinary upload → fabric type selection
- Fabric → style suggestion engine (rule-based matching)
- Bespoke results UI: style cards with reference images, fabric-specific reasoning, accessory pairings
- "Send to Tailor" image generator: composite image (fabric + style + notes) via Cloudinary transformations
- WhatsApp share integration (deep link with pre-attached image)
- "More like this" / "Not my style" feedback buttons on recommendations
- Mobile responsiveness polish across all screens
- Light wardrobe input screen (checkboxes at end of quiz)

**Content:**
- QA all product links (ensure none are broken/sold-out)
- Write fabric-specific style reasoning for all 30 styles × relevant fabric types

### Week 4: Launch + Measure

**Day 1-2:**
- Integration testing end-to-end: quiz → recommendations → shop clicks → fabric upload → tailor share
- Set up Mixpanel/PostHog event tracking for all primary metrics
- Fix critical bugs

**Day 3-4:**
- Deploy production build
- Recruit 50-100 beta users from pre-identified channels (see Section 10)
- Send personalized invitations with unique links (for tracking source)

**Day 5-7:**
- Monitor analytics dashboard daily
- Follow up individually with first 20 users within 24 hours of their first session
- Collect qualitative feedback: "Did you find an outfit you liked?" / "Did you share with your tailor?" / "What was missing?"
- Fix any high-frequency bugs or UX friction points
- Document all feedback for Week 5 iteration planning

---

## 10. User Acquisition Plan (First 100 Users)

### Channel 1: Aso-Ebi WhatsApp Groups

**Strategy:** Identify 5-10 upcoming weddings through personal and extended network. Get introduced into the Aso-Ebi WhatsApp groups where fabric has been purchased but styles haven't been decided. Offer FAUE as a free styling tool for the group.

**Target:** 30-40 users from 5-8 wedding groups

**Approach:** Position FAUE as a helpful tool, not a product launch. "I built something that helps you figure out what style to sew — want to try it with your aso-ebi fabric?"

### Channel 2: Campus Ambassadors (FUNAAB, UNILAG)

**Strategy:** Recruit 2-3 fashion-forward students as informal ambassadors. They share FAUE in their social circles, fashion clubs, and event planning groups. Incentive: early access + feature input.

**Target:** 20-30 users

### Channel 3: Fashion Twitter/X Nigeria

**Strategy:** Search for tweets expressing the exact pain point: "what should I sew," "need Agbada inspiration," "outfit ideas for [event]." Reply with a genuine, helpful offer to try FAUE — not a promotional pitch.

**Target:** 15-20 users

### Channel 4: Balogun Market Vendor Referrals

**Strategy:** Visit Balogun Market, build relationships with 2-3 fabric vendors. When customers buy fabric and ask "what style would work?", vendors refer them to FAUE.

**Target:** 10-15 users

### Channel 5: Personal Network

**Strategy:** Direct outreach to friends, family, and professional connections who fit the early adopter profile.

**Target:** 10-15 users

---

## 11. Post-MVP Roadmap (Conditional on Validation)

Each phase unlocks only if the prior phase hits its success criteria.

### Month 2 — Deepen Engagement (if 20%+ 14-day return rate)

- Digital wardrobe photo upload (the friction feature, now justified by proven engagement)
- Virtual Try-On integration (retention booster — gives users a reason to return between events)
- ML model training on collected interaction data (replace rule-based matching with learned preferences)
- Expand catalog to 2,000+ products

### Month 3 — Monetize + Partner (if 10%+ click-through on affiliate links)

- Approach top 5 brands whose products received the most clicks and saves, armed with traffic data
- Launch Brand Dashboard: catalog management, analytics, promoted placement
- Introduce FAUE Pro subscription (₦2,500/month): unlimited style suggestions, priority access to new features, exclusive Style DNA insights
- Formalize affiliate commission agreements with partner brands

### Month 4-6 — Scale

- Spree Assistant (event-specific shopping guidance)
- Aso-Ebi Group Coordination feature (in-app group styling for wedding parties)
- Push notifications for new arrivals matching user's Style DNA
- Expand to other West African markets (Ghana, Senegal)
- Native mobile app (iOS + Android) — justified by proven PMF

### Year 2-3 — Platform Maturity

- FAUE private label clothing line (the original brand foundation vision — now with distribution, data, and audience)
- Brand marketplace (brands sell directly through FAUE)
- Tailor network integration (vetted tailors, in-app booking, quality tracking)
- Style DNA API (let other platforms use FAUE's style intelligence)

---

## 12. Team Requirements (MVP Phase)

### Minimum Viable Team

| Role | Responsibility | Status |
|---|---|---|
| Technical Lead / Full-Stack Engineer | Architecture, backend, recommendation engine, deployment | Founder (Testimony) |
| Product Manager / Content Lead | Product catalog curation, style library, user research, community management | To hire or partner |

### Key Principle

The founder builds. The PM curates content, recruits users, and collects feedback. No other roles are needed until post-validation. Design is handled by the founder using the established design system. Marketing is manual outreach, not campaigns.

### Post-Validation Hires (Month 2-3, conditional)

- ML Engineer (if recommendation quality needs model training beyond rule-based)
- Community/Growth Lead (if viral loops show promise and need dedicated nurturing)
- Brand Partnerships Lead (if affiliate click data justifies formal brand outreach)

---

## 13. Budget Estimate (MVP Phase — 4 Weeks)

| Item | Cost | Notes |
|---|---|---|
| Vercel (frontend hosting) | Free tier | Hobby plan covers MVP traffic |
| Railway/Render (backend) | ~$5-10/month | Starter plan sufficient |
| PostgreSQL (Supabase or Railway) | Free-$10/month | Free tier covers MVP data volume |
| Cloudinary | Free tier | 25GB storage, 25GB bandwidth — sufficient for MVP |
| Mixpanel/PostHog | Free tier | Up to 20M events/month |
| Domain (faue.app or similar) | ~$10-15/year | One-time |
| HuggingFace API (CLIP embeddings) | Free tier or ~$10/month | Inference API for embedding generation |
| WhatsApp Business API | Free for share links | Deep links, not API messaging |
| **Total MVP Infrastructure** | **~$25-45/month** | |

Content curation (product photography, style library) is sweat equity, not cash cost.

---

## 14. Risk Register (MVP-Specific)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Recommendation quality too low with rule-based engine | Medium | High | Supplement with editorial curation — hand-pick "hero outfits" for common style profiles. Collect feedback aggressively to identify gaps |
| Quiz abandonment too high | Medium | High | A/B test quiz length (10 vs 7 vs 5 questions). Make every question visual, not text-heavy. Show progress bar |
| Fabric style suggestions feel generic | Medium | High | Write specific fabric-style reasoning for each match. Show the suggestion on similar fabric types, not generic models |
| Curated catalog goes stale (sold-out items, broken links) | High | Medium | Weekly catalog audit. Track 404s on affiliate links automatically. Prioritize brands with stable inventory |
| Users complete quiz but never return | Medium | High | Style DNA Card must be compelling enough to share. Follow up with personalized "new outfits matching your DNA" notification at Day 3 and Day 7 |
| "Send to Tailor" image quality too low | Low | Medium | Test the generated share image on 5 different phone screens before launch. Ensure it's clear, well-branded, and useful for a tailor to interpret |

---

## 15. Decision Log

| Decision | Rationale | Reversible? |
|---|---|---|
| Web app, not native | Faster to build, easier to share via links (WhatsApp virality), no app store delays. Convert to native after PMF | Yes — Month 4-6 |
| Self-curated catalog, not brand partnerships | Eliminates two-sided cold start. FAUE controls quality and speed. Brands are recruited with data, not promises | Yes — Month 3 |
| Rule-based matching, not ML | 30 styles × 6 fabric types = 180 combinations. Manageable with rules. ML comes when interaction data justifies training | Yes — Month 2 |
| No wardrobe photo upload | Highest friction feature in comparable apps. Checkbox input gives 80% of the value at 5% of the friction | Yes — Month 2 |
| No VTO at launch | Doesn't test the core assumption. Adds 2-3 weeks of build time for a retention feature before retention is proven | Yes — Month 2 |
| No monetization at launch | Testing value before price. Subscription gates would suppress the engagement signal needed for validation | Yes — Month 3 |
| Quiz as primary personalization | Replaces wardrobe upload as the cold-start personalization mechanism. Lower friction, higher completion, shareable output | Partially — quiz stays, wardrobe adds to it |

---

*This document defines the scope, architecture, timeline, and success criteria for FAUE's revised MVP. Everything beyond this scope is deferred until the core assumption is validated with real users. Build the wedge. Prove the loop. Then expand.*
