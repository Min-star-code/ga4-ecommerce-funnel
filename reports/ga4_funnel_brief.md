# Briefing Note: Where the Google Merchandise Store loses its online buyers

**Prepared by:** Mincheng Li | **Data:** Google Analytics 4 sample export for the Google Merchandise Store, 1 Nov 2020 to 31 Jan 2021 (BigQuery public dataset `ga4_obfuscated_sample_ecommerce`)

## Issue

Out of 270,154 users who visited the store in three months, 4,419 (1.6%) bought something. This note uses the store's GA4 event data to show where the other users leave, which traffic sources bring buyers, and how far the data can be trusted.

## Background

GA4 records each action on a website as an event: viewing a product, adding it to the cart, starting checkout, entering shipping and payment details, and buying. The SQL in `sql/` counts the users who reached each step at least once. Google has obfuscated parts of this sample, so some values are hidden and the data is not perfectly consistent. Every figure below comes from `analysis.py` and the files in `outputs/`, and the saved results pass 6 consistency checks, such as revenue adding up to the same total by month, by traffic source and by device.

## Key findings

1. **The biggest loss is between viewing a product and adding it to the cart.** 61,252 users viewed at least one product, but only 12,545 (20.5%) added one to the cart. After that, 77% of cart users started checkout.
2. **The second-biggest loss is at payment.** 9,714 users entered shipping details, but only 5,751 (59%) went on to enter payment details. Of those, 77% completed the purchase.
3. **Referral visitors convert best; the other sources are close together.** 1.86% of users who first arrived from a referral link bought something, compared with 1.58% for direct visits, 1.53% for organic search and 1.53% for paid search (cpc). Referral users also brought the most revenue per user ($1.55).
4. **Mobile converts as well as desktop.** 1.70% of mobile users bought something, against 1.60% on desktop, and cart-to-purchase rates were similar (36% and 34%).
5. **Revenue fell 64% after the holidays.** Purchase revenue was $160,555 in December and $57,350 in January, while users fell only 9% (104,315 to 94,790). Revenue per session dropped from $1.20 to $0.48.

## Data quality

- **15.9% of purchase events (906 of 5,692) have no transaction ID**, and 335 more repeat an ID that was already recorded. Counting purchase events would overstate orders, so this note counts purchasing users instead. It also means the November average order value ($114.58) is not reliable.
- **450 purchase events record zero revenue.**
- **18.5% of users (50,001) have a hidden traffic source** (`<Other>` or `(data deleted)`), so the source comparison covers about four in five users.
- **A user's traffic source can change between events in this sample.** My first query grouped events by source and counted 328,574 users, more than the 270,154 in the store. A consistency check caught this, so each user is now assigned the source of their earliest event.

## Considerations

- The funnel counts users who did each step at least once in three months; it does not require the steps to happen in order or in one visit.
- The sample covers the holiday season, so the December peak and January drop may not reflect a normal quarter.
- Device groups overlap, because some users visited on more than one device.

## Suggested next steps

- Look at which products are viewed most but rarely added to the cart, and test clearer prices, photos or stock information on those pages.
- Check the payment step for errors or missing payment options, since 41% of users who entered shipping details stopped there.
- Fix purchase tracking so every purchase event sends a unique transaction ID before using GA4 order counts in reports.
