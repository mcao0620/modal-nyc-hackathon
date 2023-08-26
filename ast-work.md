
# Unified AST Retrieval - MVP Plan

## Features Needed for MVP
- Handle common Python syntax
    - Imports, functions, classes, control flow etc
- Unify major AST node types
    - Map Python AST and Tree-sitter equivalents
- Normalize into consistent JSON format
    - Extract key attributes like name, docstrings, etc
- Indexing and storage
    - Store ASTs for lookup by file/function name 
- Query interface
    - Simple API to retrieve ASTs by file path / function name 


# Tasks
- Complete unified visitor to extract all major Python syntax
- Normalize remaining AST node types not handled
- Validate ASTs against sample codebase
- Fix any remaining bugs or gaps
- Build indexing and storage
    - Simple file system storage to start
    - Lookup by file name/path
- Implement query API
    - Functions to find AST by name/location
    - Return JSON AST

# Documentation
- Usage docs for query interface
