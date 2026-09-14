/* Cookie consent, and the analytics it gates.

   WHY THIS FILE EXISTS. This site had no analytics at all, so a reader arriving
   from one of our letters was indistinguishable from any other visitor and the
   "Set up your AIs" button in the activation letter could not be measured. It
   also had no cookie banner, while Cookie Policy §6 — published, and
   incorporated into the Terms — promises one: "When you first visit, you can
   accept or decline non-essential cookies." Adding analytics without the banner
   would have made that sentence false and the storage unlawful under PECR,
   which requires consent BEFORE a non-essential cookie is set.

   WHY IT IS ITS OWN IMPLEMENTATION. The product surfaces share
   @sekondbrainailabs/ui/consent, which is React and needs a bundler; this site
   is static HTML served by GitHub Pages with no build step. What it does share
   is the STORAGE CONTRACT below, byte for byte, so the two cannot disagree
   about what counts as consent. Consent is origin-scoped, so a choice made on
   the dashboard does not reach docs.sekondbrain.ai and vice versa — this banner
   is not a duplicate of that one, it is the only one this origin has.

   FAIL CLOSED. Every path that cannot prove consent is on record behaves as
   "no": a malformed record, a record written against an older policy version, a
   localStorage that throws (private browsing, blocked site data). Analytics is
   loaded from exactly one place, after exactly one check.
*/
(function () {
  'use strict';

  // The shared contract. Changing any of these without changing
  // @sekondbrainailabs/ui/consent splits the platform's idea of consent in two.
  var STORAGE_KEY = 's9n_cookie_consent';
  var POLICY_VERSION = 1;

  // Production project. A PostHog project key is a publishable client-side
  // credential — it can only write events — and this one is already committed
  // across the platform's Helm values. It is not a secret.
  var POSTHOG_KEY = 'phc_z4mKFoFrkpiUtN7qSpCnUE5ns8nLHhpW9rVf6B5MGwwe';
  var POSTHOG_HOST = 'https://eu.i.posthog.com';
  // Platform contract: one project per environment, services separated by the
  // `service` property. See Kemory/dashboard/src/lib/posthog.ts.
  var SERVICE = 'docs-site';

  function read() {
    var raw;
    try {
      raw = window.localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null; // Storage unavailable is not consent.
    }
    if (!raw) return null;
    try {
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== 'object') return null;
      if (parsed.version !== POLICY_VERSION) return null;
      if (typeof parsed.analytics !== 'boolean') return null;
      if (typeof parsed.preference !== 'boolean') return null;
      return parsed;
    } catch (e) {
      return null; // Unparseable is not consent.
    }
  }

  function write(analytics) {
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          preference: analytics,
          analytics: analytics,
          timestamp: new Date().toISOString(),
          version: POLICY_VERSION
        })
      );
    } catch (e) {
      /* A reader who blocks storage simply gets asked again; nothing breaks. */
    }
  }

  /* Local work must never reach the production project. There is one PostHog
     project for production and this site is only ever served from one host, so
     a developer opening these pages from localhost or a file:// path would
     otherwise post real $pageview events with a localhost $current_url. */
  function isLocal() {
    var h = window.location.hostname;
    return (
      window.location.protocol === 'file:' ||
      h === 'localhost' ||
      h === '127.0.0.1' ||
      h === '[::1]' ||
      h === '' ||
      /\.local$/.test(h)
    );
  }

  var _loaded = false;

  function loadAnalytics() {
    if (_loaded) return;
    if (!read() || read().analytics !== true) return; // The only gate.
    if (isLocal()) return;
    _loaded = true;

    /* PostHog's official loader, trimmed to the calls this site makes. */
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys getNextSurveyStep onSessionId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

    window.posthog.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      // This is a public documentation site. Autocapture would record a click
      // on every element of every page for a reader we have no other reason to
      // profile; pageviews plus the campaign parameters on the URL are what the
      // letters actually need measured.
      autocapture: false,
      capture_pageview: true,
      capture_pageleave: false,
      disable_session_recording: true,
      // Anonymous readers stay anonymous. A person profile per docs visitor is
      // data we did not need and would then have to hold.
      person_profiles: 'identified_only',
      respect_dnt: true,
      loaded: function (ph) {
        ph.register({ service: SERVICE });
      }
      /* WHERE THE CAMPAIGN PARAMETERS LAND, because the obvious guess is wrong.
         posthog-js does NOT put utm_source/utm_campaign on the event as plain
         properties. It records the parameters of the URL that STARTED the
         session, as $session_entry_utm_source, $session_entry_utm_medium,
         $session_entry_utm_campaign and $session_entry_utm_content. Those are
         the property names to filter on when asking what a letter produced;
         looking for `utm_campaign` finds nothing and reads as "the tagging did
         not work". Session-scoped is also the behaviour we want: a reader who
         arrives from a letter and then clicks through three pages stays
         attributed to that letter for the whole visit. */
    });
  }

  /* ─── The banner ──────────────────────────────────────────────────────── */

  function styles() {
    if (document.getElementById('s9n-consent-style')) return;
    var css = document.createElement('style');
    css.id = 's9n-consent-style';
    css.textContent = [
      '.s9n-consent{position:fixed;left:var(--sp-4,16px);right:var(--sp-4,16px);',
      'bottom:var(--sp-4,16px);z-index:9999;max-width:640px;margin:0 auto;',
      'background:var(--paper,#FAFAF7);color:var(--ink,#000);',
      'border:1px solid var(--hair,rgba(0,0,0,.08));border-radius:var(--r-lg,14px);',
      'box-shadow:0 8px 32px rgba(0,0,0,.12);padding:var(--sp-5,24px);',
      'font-family:var(--font,-apple-system,BlinkMacSystemFont,sans-serif);',
      'font-size:14px;line-height:1.55}',
      '.s9n-consent p{margin:0 0 var(--sp-4,16px) 0}',
      '.s9n-consent a{color:var(--c-blue,#1A8AF6)}',
      '.s9n-consent-actions{display:flex;gap:var(--sp-2,8px);flex-wrap:wrap}',
      '.s9n-consent button{font:inherit;cursor:pointer;padding:9px 16px;',
      'border-radius:999px;border:1px solid var(--hair,rgba(0,0,0,.08));',
      'background:transparent;color:var(--ink,#000)}',
      '.s9n-consent button.primary{background:var(--ink,#000);color:var(--paper,#FAFAF7);',
      'border-color:var(--ink,#000)}',
      '.s9n-consent button:focus-visible{outline:2px solid var(--c-blue,#1A8AF6);outline-offset:2px}',
      '@media (prefers-reduced-motion:no-preference){',
      '.s9n-consent{animation:s9n-consent-in .18s ease-out}',
      '@keyframes s9n-consent-in{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}}'
    ].join('');
    document.head.appendChild(css);
  }

  function dismiss(el) {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }

  function showBanner() {
    if (document.querySelector('.s9n-consent')) return;
    styles();

    var box = document.createElement('div');
    box.className = 's9n-consent';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-label', 'Cookies');
    box.setAttribute('aria-live', 'polite');

    var copy = document.createElement('p');
    copy.innerHTML =
      'We would like to use analytics cookies to see which pages are read and ' +
      'where they fall short. They are never used for advertising, and the site ' +
      'works the same either way. Our <a href="/legal/cookies/">Cookie Policy</a> ' +
      'explains what we store.';

    var actions = document.createElement('div');
    actions.className = 's9n-consent-actions';

    var accept = document.createElement('button');
    accept.type = 'button';
    accept.className = 'primary';
    accept.textContent = 'Accept analytics';
    accept.addEventListener('click', function () {
      write(true);
      dismiss(box);
      loadAnalytics();
    });

    var decline = document.createElement('button');
    decline.type = 'button';
    decline.textContent = 'Decline';
    decline.addEventListener('click', function () {
      write(false);
      dismiss(box);
    });

    // Declining is first in the DOM order a screen reader and a keyboard walk,
    // because the choice that stores nothing should never be the harder one.
    actions.appendChild(decline);
    actions.appendChild(accept);
    box.appendChild(copy);
    box.appendChild(actions);
    document.body.appendChild(box);
    decline.focus();
  }

  function start() {
    var choice = read();
    if (choice === null) {
      showBanner();
    } else if (choice.analytics === true) {
      loadAnalytics();
    }

    // Cookie Policy §6: "withdrawing consent is as easy as giving it". Any
    // element marked data-cookie-settings reopens the choice; the policy page
    // carries one.
    document.addEventListener('click', function (e) {
      var trigger = e.target.closest && e.target.closest('[data-cookie-settings]');
      if (!trigger) return;
      e.preventDefault();
      try {
        window.localStorage.removeItem(STORAGE_KEY);
      } catch (err) {
        /* nothing to clear */
      }
      showBanner();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
