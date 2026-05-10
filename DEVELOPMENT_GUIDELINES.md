# Development Guidelines

This document outlines the rules and best practices for code development and documentation maintenance in this project.

## Code Development Rules

### 1. File Naming
- Use snake_case for Python files (e.g., `docker_image_downloader.py`)
- Use descriptive names that reflect functionality
- Avoid abbreviations unless widely understood

### 2. Code Structure
- Keep functions focused and single-purpose
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Follow PEP 8 style guidelines

### 3. Configuration
- All configurable values should be in `config.yml`
- Provide sensible defaults in code
- Document configuration options clearly

### 4. Error Handling
- Handle exceptions gracefully
- Provide informative error messages
- Log errors appropriately using the logging system

### 5. Logging
- Use the centralized logging configuration (`logger_config.py`)
- Log important events: start, completion, errors, warnings
- Keep console output clean and user-friendly
- Detailed logs go to log files, not console

## Documentation Rules

### CHANGE_HISTORY.md

**When to Update:**
- Every time a feature is added, modified, or removed
- Every time a bug is fixed
- Every time configuration changes
- Every time dependencies are updated

**Format:**
```markdown
## YYYY-MM-DD

- Brief description of change 1
- Brief description of change 2
```

**Guidelines:**
- Use past tense verbs (Added, Fixed, Updated, Removed)
- Keep descriptions concise but informative
- Group related changes under the same date
- Include examples when helpful (e.g., filename formats)
- Most recent changes go at the top

### README.md

**Structure:**
1. Project title and brief description
2. Link to change history
3. Features list
4. Requirements
5. Installation instructions
6. Configuration guide
7. Usage examples
8. Project structure
9. How it works
10. Notes and tips
11. License

**Guidelines:**
- Keep examples up-to-date with actual behavior
- Use consistent formatting throughout
- Include both simple and advanced usage examples
- Update file structure when adding/removing files
- Test all commands before committing

### General Documentation Principles

1. **Language**: All documentation must be in English
2. **Consistency**: Use consistent terminology and formatting
3. **Clarity**: Write for users who may not be familiar with the codebase
4. **Conciseness**: Be clear and to the point
5. **Accuracy**: Ensure documentation matches actual behavior
6. **Updates**: Update documentation immediately when code changes

## Commit Message Guidelines

Use clear, descriptive commit messages:
- Start with a verb in past tense (Added, Fixed, Updated, Removed)
- Keep the first line under 72 characters
- Add details in the body if needed
- Reference issue numbers if applicable

Example:
```
Added version tag to tar filename

Tar files now include the image version tag for better identification.
Format: {repo}_{image}_{tag}_{digest}.tar
```

## Testing Before Commit

Before committing changes:
1. Test the main functionality manually
2. Verify all examples in documentation work correctly
3. Check that configuration changes are documented
4. Ensure CHANGE_HISTORY.md is updated
5. Verify no sensitive information is committed

## Directory Structure

```
python_uv_docker_images/
├── *.py                    # Python source files
├── config.yml              # Configuration file
├── pyproject.toml          # Project metadata and dependencies
├── uv.lock                 # Dependency lock file
├── README.md               # Main documentation
├── CHANGE_HISTORY.md       # Change log
├── DEVELOPMENT_GUIDELINES.md  # This file
├── images/                 # Output directory for tar files
├── tmp/                    # Temporary files (gitignored)
└── logs/                   # Log files (gitignored)
```

## Review Checklist

Before submitting changes:
- [ ] Code follows project style guidelines
- [ ] All functions have appropriate docstrings
- [ ] Configuration changes are documented
- [ ] CHANGE_HISTORY.md is updated
- [ ] README.md examples are accurate
- [ ] No debug code or comments left in production code
- [ ] Error handling is appropriate
- [ ] Logging is implemented correctly
- [ ] Documentation is in English
- [ ] Changes are tested and working
