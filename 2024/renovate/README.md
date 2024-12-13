# Renovate

Tech radar: https://www.thoughtworks.com/radar/tools/renovate

Docs: https://docs.renovatebot.com

Github: https://github.com/renovatebot/renovate

## Notes

- A tool to automate dependency updates
- List of presets available: https://docs.renovatebot.com/presets-default
- Available as a Github App
- Self-hosted option available
- A dashboard to give you access to the renovate logs behind the scenes: https://app.renovatebot.com
  - Uses Github OAuth to give you access to all of the repos that you have enabled Renovate for
- If you want to validate the config file before you push it up to the repo, check out `renovate-config-validator` here: https://docs.renovatebot.com/config-validation

## Examples

### A React app

```
{
  extends: [
    'config:recommended',
    ':disableRateLimiting',

    // If something has a major version bump, then open a separate PR for it. Otherwise just group the updates together for ease of reviewing.
    'group:allNonMajor',

    // Pin npm dependencies
    ':pinDependencies',
    ':pinDevDependencies',
  ],
  packageRules: [
    // Group the major version updates for eslint-related packages into a separate PR
    {
      matchPackagePatterns: ['eslint'],
      groupName: 'eslint',
      matchUpdateTypes: ['major'],
    },
  ],
  schedule: ['after 7am every weekday', 'before 5pm every weekday'],
  timezone: 'America/New_York',
  $schema: 'https://docs.renovatebot.com/renovate-schema.json',
}
```

### A Flux repo

A repo with Flux HelmRelease yaml files to deploy to Kubernetes.

```
{
    extends: [
        "config:recommended",
        ":disableRateLimiting",
        "schedule:weekly",

        // Group all minor and patch changes into one PR
        "group:allNonMajor",
    ],
    flux: {
        // Only make changes to the dev folders, and we'll manually merge to the higher environments
        fileMatch: [".yaml$"],
        ignorePaths: [
            "*-future/**",
            "*-qa/**",
            "*-hotfix/**",
            "*-prod/**",
            "clusters/*-future/**",
            "clusters/*-qa/**",
            "clusters/*-hotfix/**",
            "clusters/*-prod/**",
        ],
    },
}
```

### A repo with misc tools

Notable is `:dependencyDashboardApproval` to require manually approving update PRs before creating them.

```
{
  $schema: "https://docs.renovatebot.com/renovate-schema.json",
  extends: [
    "config:recommended",
    ":disableRateLimiting",
    ":dependencyDashboardApproval",

    // If something has a major version bump, then open a separate PR for it. Otherwise just group the updates together for ease of reviewing.
    "group:allNonMajor",

    // Pin npm dependencies
    ":pinDependencies",
    ":pinDevDependencies",
  ]
}
```

### Basic updates to a Go repo

```
{
  extends: [
    "config:base",
    ":disableRateLimiting",
    "group:allNonMajor",
    "schedule:weekly",
  ],
}
```

### Update only internal packages in a Node.js repo

```
{
  "extends": [
    "config:recommended",
    ":rebaseStalePrs"
  ],
  // Only scan for npm package changes, and not Dockerfile, Kubernetes, or NVM changes.
  "enabledManagers": [
    "npm"
  ],
  "hostRules": [
    {
      "matchHost": "https://npm.pkg.github.com/",
      "hostType": "npm",
      // Set up the _authToken for the .npmrc file.
      // This is encrypted with the Renovate public key, so it's safe to have in plaintext here.
      "encrypted": {
        "token": "abc123abc123abc123..."
      }
    }
  ],
  "npmrc": "@widgetcorp:registry=https://npm.pkg.github.com/",
  "packageRules": [
    {
      // Disable npm package scanning for everything but @widgetcorp packages.
      "enabled": false,
      "packagePatterns": [
        "*"
      ],
      "excludePackagePatterns": [
        "widgetcorp"
      ]
    }
  ]
}
```

### Recommended starter config

- Enable the Renovate Github App
- In your personal / organization Github App settings, enable only for some select repos
  - To prevent the "onboarding" PR from being automatically made by Renovate in all of your repos
- Place a file like this at `.github/renovate.json5`:
  ```
  {
    extends: [
      'config:recommended',
      ':disableRateLimiting',
      'group:allNonMajor',
    ],
    schedule: ['after 7am every weekday', 'before 5pm every weekday'],
    timezone: 'America/New_York',
    $schema: 'https://docs.renovatebot.com/renovate-schema.json',
  }
  ```
