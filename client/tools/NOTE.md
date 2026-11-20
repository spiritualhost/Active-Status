# Note on Tools

To push a fix and trigger a release on Github:

```bash
git add .
git commit -m {message}
git tag v{version-number}
git push origin main v{version-number}
```

See GitHub actions for more information on CI/CD.
