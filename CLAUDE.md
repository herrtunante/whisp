# WHISP APP DEVELOPMENT GUIDE

## Commands
- `npm run dev` - Start development server
- `npm run build` - Build the application
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run test` - Run Jest tests
- To run a single test: `npx jest path/to/test-file.test.ts`

## Code Style Guidelines
- **Imports**: Group imports by external packages first, then internal modules
- **Types**: Use TypeScript interfaces for props and state; export types when reused
- **Components**: Use functional components with React.FC type annotation
- **Naming**: PascalCase for components, camelCase for functions and variables
- **State Management**: Use Zustand for global state
- **Styling**: Use Tailwind CSS classes directly in components
- **Error Handling**: Display user-friendly messages via ErrorBar component
- **File Structure**: Group related components in subdirectories (ui, results)
- **Path Aliases**: Import from src using @/* path alias

## Project Structure
- `src/components` - Reusable UI components
- `src/app` - Next.js page components
- `src/utils` - Utility functions
- `src/types` - TypeScript type definitions