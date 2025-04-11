# Multi-PDF Processing Feature Implementation Roadmap

## Overview
Add support for processing multiple PDF documents for a single device, combining information from multiple sources into a single comprehensive JSON output.

## Implementation Checklist

### 1. Frontend Changes (upload-modal.tsx)
- [x] Modify file input to accept multiple files
  - [x] Update input element with `multiple` attribute
  - [x] Update handleFileChange to handle FileList
  - [x] Add array state for multiple files

- [x] Update UI to show multiple selected files
  - [x] Add file list component showing all selected PDFs
  - [x] Show file names and sizes
  - [x] Add individual file removal capability
  - [x] Update progress indicator for batch processing

- [x] Update form data handling
  - [x] Modify handleUpload to send multiple files
  - [x] Update progress tracking for multiple files
  - [x] Maintain manufacturer selection logic

### 2. Backend API Changes (pdf_ingestion/api.py)

#### API Endpoint Updates
- [x] Modify /process endpoint
  ```python
  @router.post("/process", response_model=ProcessResponse)
  async def process_pdf(
      files: List[UploadFile] = File(...),
      manufacturer: str = Body(...)
  ) -> ProcessResponse:
  ```

#### Processing Logic Updates
- [x] Add sequential PDF processing function
  ```python
  async def process_multiple_pdfs(files: List[UploadFile], manufacturer: str):
      # Process first file with original prompt
      # Process subsequent files with context
      # Return final merged result
  ```

- [x] Implement file handling for multiple PDFs
  - [x] Save all PDFs to temp directory
  - [x] Process sequentially
  - [x] Clean up temp files after processing

### 3. Prompt Engineering

#### Original PDF_PROMPT
- [x] Review and update if needed
- [x] Ensure it remains optimal for first document
- [x] Add any missing field specifications

#### New Context-Aware Prompt
- [x] Implement FOLLOW_UP_PROMPT
  ```python
  FOLLOW_UP_PROMPT = """You are a specialized PDF parsing agent for HVAC device documentation. We have already extracted information from previous documents, provided below. Your task is to enhance this information with any new details found in the current document.

  EXISTING INFORMATION:
  {existing_json}

  Your response must be a valid JSON object with EXACTLY this structure:
  [JSON structure specification]

  Critical Rules:
  1. Device Section:
     - Preserve ALL existing device information
     - ONLY add new information to empty fields
     - If a field has existing data, keep it unless new data is clearly more complete
     - Never remove or blank out existing fields

  2. BACnet Objects:
     - Keep ALL existing BACnet objects
     - Add ANY new BACnet objects found
     - Use exact bacnetAddr format (e.g., "AI1", "BO3")
     - Include units ONLY if specifically mentioned
     - Copy descriptions word-for-word from documentation

  3. Modbus Registers:
     - Keep ALL existing registers
     - Add ANY new registers found
     - Never modify existing register information
     - Add new registers with complete information only

  4. Output Format:
     - Return ONLY the JSON structure
     - No additional text or explanations
     - Maintain exact field names and structure
     - Keep all arrays even if empty ([])
  """
  ```

### 4. Storage System Updates
- [x] Update file storage logic
  - [x] Save all PDFs to raw_docs directory
  - [x] Maintain unique filenames
  - [x] Update file path handling

- [x] Update JSON storage
  - [x] Save final merged JSON as productInfo.json
  - [x] Handle existing file updates
  - [x] Maintain proper directory structure

### 5. Error Handling
- [x] Add validation for multiple file uploads
  - [x] Check file types
  - [x] Verify file contents
  - [x] Handle partial processing failures

- [x] Implement error reporting
  - [x] Track per-file processing status
  - [x] Provide detailed error messages
  - [x] Handle cleanup on failure

### 6. Testing

#### Unit Tests
- [ ] Test file upload handling
- [ ] Test PDF processing sequence
- [ ] Test JSON merging logic
- [ ] Test error handling

#### Integration Tests
- [ ] Test complete workflow
- [ ] Test with various PDF combinations
- [ ] Test with different manufacturers
- [ ] Test error scenarios

#### Manual Testing Checklist
- [ ] Upload multiple PDFs
- [ ] Verify all PDFs saved correctly
- [ ] Check JSON output structure
- [ ] Verify data preservation rules
- [ ] Test error handling
- [ ] Verify progress indication
- [ ] Check cleanup operations

### 7. Documentation

#### Code Documentation
- [ ] Update function documentation
- [ ] Add processing flow documentation
- [ ] Document error handling

#### User Documentation
- [ ] Update UI help text
- [ ] Document multiple file support
- [ ] Add usage examples
- [ ] Document limitations

## Success Criteria
1. Multiple PDFs can be uploaded in a single operation
2. All PDFs are properly stored in raw_docs
3. Information is correctly combined into a single JSON
4. Existing data is preserved and enhanced
5. Error handling works correctly
6. User interface clearly shows progress and results
