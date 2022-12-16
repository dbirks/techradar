# k6

Tech radar: https://www.thoughtworks.com/radar/tools?blipid=202010078

Github: https://github.com/grafana/k6

Homepage: https://k6.io/

## Description

- a load testing tool
- scripts are written in javascript
- example scripts:
  ```
  k6 run script.js
  k6 run smoke-test.js
  ```
- the k6 cli is distributed as a Go binary

- has some low-code tools
  - Test builder ([link](https://k6.io/docs/test-authoring/test-builder/))
    - available on k6 Cloud: https://app.k6.io
  - Browser recorder
    - available for Chrome and Firefox

- has some converters ([link](https://k6.io/docs/integrations/#converters))
  - HAR file (downloaded from the network tab in browsers) -> k6 script
  - Postman collection -> k6 script
  - Swagger/OpenAPI spec -> k6 script

- options for running in a distributed way
  - k6 Cloud: https://app.k6.io
    - free to sign in and use their test builder UI
  - k6 operator for Kubernetes ([link](https://k6.io/blog/running-distributed-tests-on-k8s/))
    - you put your k6 js script into a ConfigMap
    - and then create one of their Custom Resources to reference the ConfigMap, and optionally set parallelism

- looks like a well-thought-out approach to extensions
  - xk6 gives you a way to extend the k6 binary and make custom builds ([docs](https://k6.io/docs/extensions/))
  - some examples:
    - [xk6-output-prometheus-remote](https://github.com/grafana/xk6-output-prometheus-remote): for sending metrics on k6 tests to Prometheus
    - [xk6-amqp](https://github.com/grafana/xk6-amqp): for sending messages to a message queue as part of your tests
    - more examples on their Explore page: [link](https://k6.io/docs/extensions/get-started/explore/)

- xk6-browser ([docs](https://k6.io/docs/javascript-api/xk6-browser/))
  - launches a Chromium browser in the backgroun
  - more similar now to a tool like Cypress
  - says it "aims to provide rough compatibility with the Playwright API"

- xk6-disruptor ([docs](https://k6.io/docs/javascript-api/xk6-disruptor/))
  - injects faults to do chaos engineering

## Alternatives

- Cypress
  - records videos of the tests for viewing afterwards
  - has a open source dashboard (called Sorry Cypress [link](https://sorry-cypress.dev/)), so you might be able to get more functionality from the open source side of things, depending on your needs
- JMeter
  - https://k6.io/blog/k6-vs-jmeter/
    - JMeter's GUI vs k6's Test builder
    - Selenium vs xk6-browser
    - writing scripts in XML vs javascript

## Cons

- cloud offering can get pricey
  - currently $99/month/developer
  - but looks targeted at enterprises
  - you can get quite a lot of mileage out of the open source core of it

## Further reading

- Introductory slide deck from Grafana: https://github.com/grafana/k6-learn
- TypeScript template: https://github.com/grafana/k6-template-typescript
- Awesome k6: https://github.com/grafana/awesome-k6

## Recommendation

Tech Radar recommendation: Adopt

My recommendation: Trial
