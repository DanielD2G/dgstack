# PRD: Smart Reminders

Owner: Product. Target: Q4 2026. Status: ready for review.

## Problem
Users forget to log their habits and churn. Our users have been asking for
smarter reminders constantly; it is the most requested thing we hear.

## Goal
Increase D30 retention by 20%.

## Solution
Replace today's fixed-time reminder with Smart Reminders:

1. **ML send-time model.** Learns, per user, the time of day they are most
   likely to log, and sends the reminder then.
2. **Push on iOS, Android and web.** New rich notification with a one-tap
   "Done" action.
3. **SMS fallback.** Users who have not granted push permission get a daily
   SMS reminder instead, so everyone is covered.
4. **Admin dashboard** for the growth team to tune the model and see sends,
   opens and conversions.

## Non-goals
- No changes to the iOS and Android apps in this phase. We ship server-side
  only and reuse what the apps already have.
- No new data collection.

## Success metric
Reminder open rate above 15% within four weeks of launch.

## Plan
Two sprints (four weeks), two backend engineers. The ML model, the SMS
provider integration and the dashboard run in parallel in sprint 1; push and
the launch in sprint 2.

## Risks
None major. SMS costs are small.
