# Urban Company — Graduation Project November 2026 | PMF Cohort 52

**Submission deadline:** Dec 13, 3:59:00 PM (Asia/Calcutta)

## Attempt 1 - Problem Statement

You are a Product Manager on the Consumer Growth Team at Urban Company.

A customer books a home service on Urban Company: a deep clean, an AC service, a plumber, a salon visit. The professional arrives, the job is done, and they pay. Then they get on with their week.

Some book again within a few weeks. Many do not. The team does not know what separates the two.

One of your company's strategic goals is to:

> **Increase the percentage of customers who book another service within 90 days of a completed booking.**

Pick a month. Every customer whose first completed booking in that month was in a core category is counted once, and that booking is their anchor booking. Quick-service housekeeping (InstaHelp) is excluded. A customer "books another service" if they complete any later booking, in any category, within 90 days of the anchor booking. Redos, warranty claims and bookings that end in a refund do not count.

Customers who return are central to the business: about 84% of Urban Company's net transaction value comes from repeat customers.

However, you are not being given the underlying user problem. Your task is to discover it. And for the solution, the constraint is that you **CANNOT** offer discounts, coupons or memberships, change pricing, or change what service professionals earn or how they are managed. Your solution must work from the customer's side.

## Part 1: Build an AI-Powered Discovery Engine

Before proposing any solution, you must build an AI-powered system that analyzes user feedback at scale.

You may use: Claude, GPTs, Agents, Workflows, n8n, Zapier, Perplexity, or any AI-native stack of your choice.

The goal is to analyze sources such as:
- App Store reviews
- Play Store reviews
- Review and complaint sites such as Trustpilot and consumer complaint forums
- Reddit discussions from Indian city and household communities
- Social media conversations about home services
- YouTube comments on home-service and cleaning videos
- Urban Company's public shareholder letters and earnings-call transcripts
- Other publicly available conversations about booking home services in India

**Use only sources you are permitted to access. Do not scrape logged-in Urban Company pages or the app.**

Your discovery engine should help answer questions such as:
- What do customers expect once a booking is complete?
- How do they decide that a home service is needed, and when?
- Who or what do they turn to when they need the same kind of service again, or a different one?
- How do customers describe why they did or did not book again, in their own words?
- What do they do outside the app: local providers, neighbours, family, WhatsApp groups?
- What separates customers who return from customers who do not, in their own accounts?
- How do these patterns differ by service category, city, household type and how the customer first found Urban Company?
- What unmet needs emerge consistently across conversations?

Public posts over-represent people who had a bad experience, and customers who simply never came back leave no trace at all. Your workflow should show how it accounts for both biases.

Your workflow should go beyond summarizing reviews or performing sentiment analysis. It should enable you to identify, quantify where possible, and compare potential opportunity areas that could influence the stated business metric.

You should demonstrate how your workflow gathers and analyzes data, how themes are identified, how insights are generated, and how you validated the quality of the insights (see the AI Evidence Log under Deliverables).

## Part 2: Break Down the Business Metric

Break down:

> **Share of customers who complete another booking within 90 days of a completed booking**

into the relevant product outcomes and user behaviors that could influence it.

Develop your own decomposition from your understanding of the product and the evidence from your discovery engine. Consider questions such as (sample questions only):
- Which parts of this metric can the product influence from the customer's side, and which cannot?
- How would you measure each part using only what a customer can tell you or what is publicly available?
- Does the metric behave differently for different service categories, cities or kinds of households?

Use this decomposition alongside the output of your discovery engine to determine where the highest-potential opportunities lie.

## Part 3: Validate the Opportunity Through User Research

AI-generated insights are only a starting point.

Choose a target user segment and opportunity area based on your analysis. Conduct 5 to 6 user interviews with respondents belonging to the segment you have chosen. Respondents should have completed an Urban Company booking in the last 6 months. Include both people who booked again within 90 days and people who did not, and together cover more than one service category. Record how many bookings each respondent has made in total.

Think carefully about the research methodology you would choose.

Understand:
- How they decided to book that service, and how they found Urban Company
- What happened after the service was done, and what they expected
- What other services their home or household has needed since, and how they handled each
- What they did when they needed something done, and who or what they turned to
- What would have made them book again, or what stopped them
- How they think about home services in general: planned, reactive or avoided

**Do not collect booking screenshots, invoices, addresses, phone numbers or other personal documents from respondents.**

## Part 4: Define the Problem

Based on your discovery engine and primary research, clearly articulate:
- Your target user segment
- The scenario in the customer journey you are solving for
- The product outcome you intend to influence
- The root cause
- Existing user workarounds
- Why solving the problem creates meaningful user value
- Why solving the problem makes business sense for Urban Company

Show how your thinking evolved across:

**Business Metric -> Product Outcomes -> AI Discovery -> Primary Research -> Problem Definition**

Show how your primary research validated or challenged what your discovery engine surfaced.

**DO NOT frame the problem simply as:**
- "Customers had a bad experience."
- "Customers need an offer to come back."

Your research should uncover why customers in the segment you chose did or did not book again, even when nothing went wrong with the booking.

## Part 5: Build and Deploy an AI-Native MVP

Based on the problem you identify, design, build and deploy a functional MVP. It may take the form of:
- A feature within the Urban Company app
- An AI-powered workflow
- An AI agent
- A standalone experience connected to the home-services journey

Your MVP must not book services, message Urban Company or service professionals, or take any action on a customer's account on their behalf, and it must not scrape Urban Company. It should work from what the customer provides and from publicly available information.

You must deploy the MVP to production so another person can use it to attempt a real task. Mentors will test it.

## Part 6: Test Your MVP With Users

Return to at least 3 users from your target segment and ask them to use your MVP on a real task. Document what you learned and what you would change in the next iteration.

## Part 7: Define Success

Start with the business metric. Then define the metrics your solution would influence: leading indicators, guardrail metrics, the definition of each, and your rationale for choosing them. Include how you would measure whether your agent chooses the right tool at the right moment, and how you would know your solution is not nudging customers towards services they do not need.

## Part 8: Risks & Mitigation Steps

Think about why your solution might fail. Identify the most important risks for your specific solution and propose mitigation plans.

## Deliverables

1. **[Link] AI Discovery Engine** — Link where the workflow can be tested; a 1-slide explanation inside the final deck outlining how it works.
2. **[PDF] 10-slide deck** — Business metric decomposition; Discovery engine findings; User research; Chosen target segment; Root cause and problem definition; Solution rationale; MVP and user testing; Success metrics; Risks and limitations.
3. **[Link] Deployed AI-Native MVP** — A publicly accessible prototype, workflow or agent that can be interacted with and tested.
4. **[Link] AI Evidence Log** (one document, view access for anyone with the link) — Sources and volume your discovery engine analysed; A golden set of about 20 items you labelled by hand, how often your engine agreed with you, and where it failed; 2 to 3 places where you rejected or corrected AI output, and why.

## Guidelines for the Deck

- Name of the Fellow should NOT be present anywhere in the slide deck.
- 10 slides max (title slide, if you choose to have it, should be counted within the 10 slides).
- Slide title should state the key message of the slide for easier reading. For example: don't write "Problem" as the slide title, state the problem succinctly in the slide title.
- If you are using a background colour for the slides, please ensure the text is readable.
- When using colours, keep in mind the reader may be colour blind. So, choose colours carefully.
- Link supporting artefacts (eg. survey URLs etc) via a hyperlink. Please ensure the reader has access to the documents. If you do not provide access, this might lead to reduction in your scores.
- Maximum file size should be less than 40 MB.
- Naming of the file should be e.g. NL_PhonePe.
- Minimum font size: 14 for Google Slides or PPT (strictly adhered to). Minimum font size: 26 for Figma with frame of 1920*1080px. Minimum font size: 22 for Canva with frame of 1920*1080px.
- **Submission Deadline:** 13 December, 2026 3:59:00 PM IST (no submissions accepted after the deadline, even if by a few seconds).