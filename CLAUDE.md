# AutoQA Development Guide

## Commands
- **Start Dev Environment**: `./dev.sh` (starts both backend and frontend)
- **Backend Only**: `python run_backend.py`
- **Frontend Only**: `cd frontend && npm run dev`
- **Build Frontend**: `cd frontend && npm run build`
- **Lint Frontend**: `cd frontend && npm run lint`
- **Run Tests**: `python -m pytest [test_path]`
- **Format Python**: `black .`
- **Sort Imports**: `isort .`
- **Install Dependencies**: `uv pip install -e .`

## Code Style
- **Python**: Black formatter (88 char line length), isort for imports
- **Python Version**: 3.13+
- **Typing**: Use type hints consistently
- **Imports**: Group by standard lib, third-party, local
- **Error Handling**: Use explicit try/except blocks with specific exceptions
- **Frontend**: TypeScript with Next.js, follow ESLint rules
- **React Components**: Functional components with hooks
- **CSS**: Tailwind with DaisyUI components
- **Testing**: Pytest for backend, React Testing Library for frontend
- **Comments**: Please do not add useless comments that just reiterate exactly what the code is doing, if needed comments should describe why the code is there, not what it is doing.

## Project Structure

```
mad-ai-hackathon/
├── autoqa/                     # Core AutoQA Python package
│   ├── core.py                 # Main AutoQA logic and test execution
│   ├── models.py               # Data models and schemas
│   ├── report.py               # Test result reporting functionality
│   ├── cli.py                  # Command line interface
│   └── test_plan.json          # Test plan configuration
├── backend/                    # FastAPI backend service
│   ├── main.py                 # FastAPI application entry point
│   ├── autoqa_service.py       # AutoQA service integration
│   ├── crud.py                 # Database operations
│   └── database.py             # Database configuration
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   ├── app/                # Next.js app router
│   │   │   ├── api/auth/       # NextAuth API routes
│   │   │   ├── auth/signin/    # Sign in page
│   │   │   ├── history/        # Test history page
│   │   │   ├── tests/          # Test execution pages
│   │   │   └── providers.tsx   # Authentication providers
│   │   ├── auth/               # Authentication configuration
│   │   │   ├── auth.config.ts  # Auth configuration
│   │   │   └── auth.ts         # Auth setup
│   │   ├── components/         # React components
│   │   │   ├── forms/          # Form components
│   │   │   ├── layout/         # Layout components
│   │   │   ├── tests/          # Test-related components
│   │   │   └── ui/             # UI components
│   │   └── lib/                # Utility libraries
│   │       ├── api.ts          # API client
│   │       └── hooks.ts        # Custom React hooks
│   └── middleware.ts           # Next.js middleware
├── data/                       # Generated test data and reports
│   ├── test_plans/             # Stored test plans
│   ├── test_results/           # Test execution results
│   └── test_report/            # Generated reports
├── dev.sh                      # Development environment startup script
├── run_backend.py              # Backend service runner
└── pyproject.toml              # Python project configuration
```