# Xeto Integration Roadmap

## Overview
This roadmap outlines the integration of Xeto library generation and compilation capabilities into the PDF ingestion application. The integration will allow users to convert extracted JSON data into Xeto libraries, edit them in a Monaco editor interface, and compile them using Haxall tools.

## Prerequisites
- [x] Node.js installed in backend container
- [x] @haxall/haxall package installed
- [x] Monaco editor component available (reuse from existing implementation)

## Phase 1: Backend Foundation

### 1.1 Backend Container Setup
- [ ] Add Node.js installation to Dockerfile.backend
- [ ] Install @haxall/haxall package
- [ ] Configure package.json with type: "module"
- [ ] Create required directory structure for Xeto

### 1.2 Xeto Service Implementation
- [x] Create services/xeto_service.py
  - [x] Implement synchronous subprocess wrapper
  - [x] Add Xeto initialization functionality
  - [x] Add Xeto compilation functionality
  - [x] Add error handling and result parsing

### 1.3 JSON to Xeto Conversion
- [x] Create services/json_converter.py
  - [x] Port json_to_xeto.py functionality
  - [x] Add template handling
  - [x] Implement error handling
  - [x] Add validation checks

### 1.4 API Endpoints
- [x] Add new endpoints to api.py:
  ```python
  POST /api/apps/pdf-ingestion/convert-to-xeto
  POST /api/apps/pdf-ingestion/compile-xeto
  POST /api/apps/pdf-ingestion/save-xeto
  ```

## Phase 2: Frontend Components

### 2.1 Xeto Editor Modal
- [x] Create components/xeto-editor-modal.tsx
  - [x] Implement modal container
  - [x] Add Monaco editor integration
  - [x] Create tab system for lib.xeto and specs.xeto
  - [x] Add compilation status display
  - [x] Add error message display

### 2.2 UI Integration
- [x] Add "Convert to Xeto" button to JSON view
- [x] Connect button to editor modal
- [x] Add action buttons:
  - [x] Attempt Compile
  - [x] Save to Storage
  - [x] Cancel/Close

### 2.3 State Management
- [x] Add Xeto-related state management
- [x] Implement file content handling
- [x] Add compilation status tracking
- [x] Handle error states

## Phase 3: Integration

### 3.1 API Integration
- [x] Connect frontend to convert-to-xeto endpoint
- [x] Implement compilation request handling
- [x] Add save functionality
- [x] Add error handling

### 3.2 File System Integration
- [x] Implement storage structure:
  ```
  document_storage/
    └── manufacturer/
        └── model/
            ├── raw_docs/           # Original PDFs
            ├── productInfo.json    # Extracted JSON
            └── xeto/              # New Xeto artifacts
                ├── lib.xeto
                └── specs.xeto
  ```
- [x] Add file overwrite handling
- [x] Implement cleanup procedures

### 3.3 End-to-End Testing
- [ ] Test JSON to Xeto conversion
  - [ ] Create test JSON data
  - [ ] Verify conversion accuracy
  - [ ] Test edge cases
- [ ] Test Xeto compilation
  - [ ] Test valid Xeto files
  - [ ] Test invalid Xeto files
  - [ ] Verify compilation output
- [ ] Test file storage
  - [ ] Test file creation
  - [ ] Test file overwrite
  - [ ] Test file cleanup
- [ ] Test error scenarios
  - [ ] Test invalid JSON
  - [ ] Test compilation errors
  - [ ] Test file system errors

## Phase 4: Refinement

### 4.1 Error Handling
- [x] Improve error messages
- [x] Add error recovery procedures
- [x] Implement graceful fallbacks

### 4.2 User Experience
- [x] Add loading states
- [x] Improve feedback messages
- [x] Add confirmation dialogs

### 4.3 Performance
- [x] Optimize file operations
- [ ] Add caching where appropriate
- [x] Improve response times

## Testing Checkpoints

### Backend Tests
- [ ] Test Xeto service operations
- [ ] Test JSON conversion
- [ ] Test API endpoints
- [ ] Test file system operations

### Frontend Tests
- [ ] Test modal functionality
- [ ] Test editor operations
- [ ] Test compilation flow
- [ ] Test error handling

### Integration Tests
- [ ] Test end-to-end workflow
- [ ] Test error scenarios
- [ ] Test edge cases
- [ ] Test performance

## Future Enhancements (Post-MVP)
- Syntax highlighting for Xeto files
- Real-time validation
- Version history
- File download capability
- Auto-fix suggestions for common errors
- Diff viewer for changes
- Batch operations support

## File Structure Changes
```
pdf_ingestion/
├── api.py
├── services/
│   ├── xeto_service.py      # New
│   └── json_converter.py    # New
├── utils/
│   └── subprocess_utils.py  # New
└── templates/
    └── xeto/               # New
        ├── lib.xeto.template
        └── specs.xeto.template
```

## API Specifications

### Convert to Xeto
```typescript
POST /api/apps/pdf-ingestion/convert-to-xeto
Request:
{
  jsonPath: string,
  manufacturer: string,
  model: string
}
Response:
{
  success: boolean,
  libContent: string,
  specsContent: string,
  error?: string
}
```

### Compile Xeto
```typescript
POST /api/apps/pdf-ingestion/compile-xeto
Request:
{
  libContent: string,
  specsContent: string,
  manufacturer: string,
  model: string
}
Response:
{
  success: boolean,
  output?: string,
  error?: string
}
```

### Save Xeto
```typescript
POST /api/apps/pdf-ingestion/save-xeto
Request:
{
  libContent: string,
  specsContent: string,
  manufacturer: string,
  model: string
}
Response:
{
  success: boolean,
  paths: {
    lib: string,
    specs: string
  },
  error?: string
}
```

## Success Criteria
- [x] Users can convert JSON to Xeto files
- [x] Users can edit Xeto files in the Monaco editor
- [x] Users can compile Xeto libraries
- [x] Users can save compiled libraries
- [x] All error cases are handled gracefully
- [x] File storage structure is maintained correctly

## Next Steps
1. Create comprehensive test suite for end-to-end testing
2. Document the Xeto integration features
3. Create user guide for the Xeto editor functionality
4. Consider implementing caching for frequently accessed files
5. Monitor system performance and optimize as needed
