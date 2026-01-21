# 🕵️‍♂️ Scraper Status Report

**Last Updated:** 2026-01-21
**System Status:** ✅ Operational (12/18 Sources Active)

---

## 🔴 Currently Blocked / Not Working
The following portals are currently not returning results.

| Portal | Status | Technical Reason | Potential Fix (Advanced) |
| :--- | :--- | :--- | :--- |
| **Naukri.com** | ❌ Blocked | **Cloudflare / Akamai**: Detects the browser is automated ("Headless") and returns "Access Denied". Even with stealth mode, the IP is flagged. | **Residential Proxies** (e.g., BrightData) or **Stealth Browser Service** (ZenRows). |
| **LinkedIn** | ❌ Blocked | **Auth Wall**: Guest search is redirecting to the Login Page after a few requests. LinkedIn has strict rate limits. | **Manual Cookies**: Export cookies from your real browser and inject them into the scraper. |
| **Instahyre** | ❌ Blocked | **Redirect Loop**: Searching for jobs redirects to the homepage. Likely detecting bot behavior or URL pattern change. | **Reverse Engineering**: Needs deep analysis of their internal API calls (XHR) instead of HTML scraping. |
| **Glassdoor** | ❌ Blocked | **Login Required**: Glassdoor mandates login to view details. | **Account Injection**: Hardcode dummy credentials (risky) or use cookies. |
| **JSearch** | ⚠️ Limited | **Quota Exceeded (429)**: The RapidAPI free tier is exhausted. | **Upgrade Plan**: Pay for RapidAPI or wait for monthly reset. |

---

## 🟢 Working Perfectly
These sources are reliable and actively providing data.

1.  **Indeed** (New! ~25-50 jobs) - *Uses Playwright Stealth*
2.  **Apna** (New! ~30 jobs)
3.  **Foundit (Monster)** (New! ~30 jobs)
4.  **Freshersworld** (New! ~30 jobs)
5.  **Adzuna** (Aggregator: ~200+ jobs)
6.  **IIMJobs** (Premium: ~20 jobs)
7.  **Hirist** (Tech Premium)
8.  **Remotive** (Remote API)
9.  **Cutshort**
10. **HerKey**
11. **ZipRecruiter**
12. **Bayt / GulfTalent** (Middle East)

---

### Summary
*   **Coverage**: You have excellent coverage across entry-level (Apna/Freshersworld), Tech (Hirist/Cutshort), and General (Indeed/Adzuna/Foundit).
*   **Missing**: The main loss is **Naukri/LinkedIn**, but **Adzuna/Indeed** often aggregate listings from these sites anyway.
