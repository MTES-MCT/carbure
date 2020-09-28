# CarbuRe React frontend

## Dependencies

- `react-scripts` (create-react-app)
- `react`
- `react-dom`
- `react-router-dom` (client-side routing)
- `clsx` (conditional css class selection)
- `js-cookie`

## Structure

- `public`: static files
- `src`: app source code
  - `assets`: static files that will be imported in the source code
  - `components`: presentational and helper components
    - `system`: design components that are shared all over the app
  - `hooks`: custom react hooks for business logic
  - `routes`: "controller" components rendered at a given route
  - `services`: helper functions to talk to external services
  - `utils`: general helper functions
  - `app.tsx`: application root component
  - `index.tsx`: application entry point
