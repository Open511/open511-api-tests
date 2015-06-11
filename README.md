Integration tests for an Open511 API.

These tests are written for Open North's [Open511 server](https://github.com/open511/open511), but are loosely coupled so that they could be used with minimal effort to test another Open511 implementation.

# Setup

So that test data can be loaded, the Open511 API implementation must provide an HTTP endpoint to communicate with the test client.

That endpoint needs to receive POST requests with x-www-form-urlencoded data. The `command` parameter will be equal to either `clear` or `load`.

## `clear` commands

* Ensure a jurisdiction exists with ID `test.open511.org` and a default timezone of `America/Montreal`
* Ensure that there are no road events in the database associated with that jurisdiction

## `load` commands

An Open511 XML document will be sent in the `xml` parameter of the request. That document should be loaded into the database.

This will be a compliant Open511 document, with a few exceptions:
* Events will not contain a self link.
* Events will not contain a jurisdiction link. All events should be loaded into the test.open511.org jurisdiction
* Events will not contain `created` or `updated` timestamps
* `event` tags will have an `id` attribute. That ID should often be used in generating the event's URL, and must be used to determine whether to create a new event or update an existing one. That is, if the test client uploads a document containing `<event id="hello">`, and then later uploads another document containing `<event id="hello">`, the existing event object should be updated, and its `created` timestamp should not change.

# Running tests

```
python run_tests.py http://url-to-open511-root-resource http://url-to-test-endpoint
```