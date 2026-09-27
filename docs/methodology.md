# Methodology

## Purpose

Technical SEO URL Checker inspects evidence available from one HTTP request and, when the response is HTML, the page's parsed HTML.

It is intentionally narrower than a crawler or search-engine diagnostic platform.

## Evidence model

### HTTP layer

The checker records:

- final HTTP status
- final URL
- redirect count
- redirect sequence returned by the HTTP client
- response Content-Type
- final URL scheme
- whether an HTTP request ended on HTTPS

A successful HTTP response is not the same as search-engine indexing.

### HTML layer

For HTML responses, the checker extracts:

- `<title>`
- `<meta name="description">`
- `<meta name="robots">`
- `<link rel="canonical">`
- `X-Robots-Tag` response directives

Relative canonical URLs are resolved against the final URL.

### Comparison rules

Canonical comparison normalizes:

- scheme and hostname case
- default HTTP/HTTPS ports
- empty paths to `/`
- URL fragments are removed for comparison

Query strings and non-default ports remain significant.

Multiple canonical elements are reported because they create conflicting implementation evidence that should be investigated.

## What the checker does not know

The checker cannot determine:

- whether Google, Bing, or another search engine indexed a URL
- which canonical a search engine selected
- whether a page ranks for a query
- whether a redirect is appropriate for the site's business intent
- how JavaScript changes the final rendered DOM
- how a crawler with a different user agent or network context will experience the URL
- whether authentication, WAF rules, geo restrictions, rate limits, or bot mitigation will change another crawler's response

## Request behavior

The tool uses an ordinary HTTP GET with redirects enabled.

A custom User-Agent can be supplied, but changing the User-Agent does not turn this into a full crawler simulation.

The default request timeout is 20 seconds.

## Interpreting signals

Signals are observations that may deserve review; they are not automatic severity ratings.

Examples:

- `noindex` is an explicit directive observed in the response/page and should be checked against the intended indexing policy.
- Multiple canonical elements are an implementation inconsistency worth reviewing.
- A redirect chain may add unnecessary hops, but whether it should be changed depends on the site's redirect design.
- Missing title or meta description is reported as an absence, not as a prediction of ranking impact.

Use the evidence together with the site's intended architecture and deployment context.

## Responsible use

Only check URLs you are authorized to request. Respect applicable terms, rate limits, access controls, and network policies. This project does not attempt to bypass authentication, robots restrictions, WAF controls, or other access mechanisms.
