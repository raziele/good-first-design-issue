# Frontend Test Dependencies

The frontend tests in this directory require the following additional packages
to be installed in `src/frontend/` (added to its `devDependencies`):

```
@testing-library/react >= 16.0
@testing-library/jest-dom >= 6.0
```

Install command (run from `src/frontend/`):
```
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

These are test-only dependencies — not required in production builds.
