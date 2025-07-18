# Agent Instructions: Suggest Edit Feature Implementation

## 🎯 OBJECTIVE
Implement a "Suggest Edit" feature that allows users to refine text with preset options and RAG integration. The feature should work with selected text OR entire sections.

## 🚀 CORE REQUIREMENTS

### 1. TEXT SELECTION BEHAVIOR
- **ALWAYS ENABLED**: "Suggest edits" button is always clickable
- **WITH SELECTION**: If user has selected text, process only the selected text
- **WITHOUT SELECTION**: If no text is selected, automatically process the entire current section
- **VISUAL FEEDBACK**: Show users what content will be processed (selected text or section boundary)

### 2. BUTTON FUNCTIONALITY
- Button remains enabled at all times
- Tooltip changes based on context:
  - With selection: "Refine selected text"
  - Without selection: "Refine current section"
- No disabled states - always ready to use

### 3. SECTION DETECTION LOGIC
- Identify which section the user is currently viewing/focused on
- Use scroll position, cursor location, or last clicked section as indicators
- Have a fallback to the first section if detection fails
- Highlight the target section briefly when auto-selected

## 🎨 MODAL STRUCTURE

### Content Preview Section
- Show exactly what will be processed
- Display "Selected Text" or "Current Section" as header
- Include character and word count
- Use syntax highlighting for better readability

### Quick Actions Grid
Create a 3x2 grid of preset buttons:
- **Row 1**: Shorten, Clarify, Improve Flow
- **Row 2**: Make Concise, Expand Detail, Simplify

### Custom Instructions Area
- Large textarea for user input
- Placeholder text guiding users on what they can request
- Real-time character count

### Advanced Options
Checkboxes for:
- Use RAG for additional research
- Maintain original tone
- Preserve technical accuracy

### Action Buttons
- Primary "Apply" button (initially disabled)
- Secondary "Cancel" button

## 🧠 PRESET BEHAVIOR

### Non-RAG Presets (No external research needed)
- **Shorten**: Reduce content length while keeping key points
- **Clarify**: Improve readability and clarity
- **Improve Flow**: Better transitions and logical progression
- **Make Concise**: Remove redundancy and wordiness
- **Simplify**: Use simpler language and structure

### RAG-Required Presets
- **Expand Detail**: Add more comprehensive information (auto-enables RAG checkbox)

### Preset Selection Logic
- Only one preset can be selected at a time
- Selecting a preset enables the Apply button
- "Expand Detail" automatically checks the RAG option
- Visual indication of selected preset (highlighted state)

## 🔍 RAG INTEGRATION RULES

### Auto-Enable RAG When:
- User selects "Expand Detail" preset
- Custom instructions contain research keywords: "research", "find more", "add details", "investigate", "expand upon"

### Manual RAG Option:
- User can manually enable RAG for any preset
- Show tooltip explaining what RAG does: "Search for additional information to enhance content"

### RAG Processing Indicators:
- Show different loading states for RAG vs non-RAG operations
- RAG operations should show "Researching..." then "Processing..."
- Non-RAG operations show simple "Processing..."

## 📋 IMPLEMENTATION WORKFLOW

### Step 1: Button Click Detection
- Detect if "Suggest edits" button is clicked
- Check for active text selection
- If no selection, identify current section
- Store the target content and metadata

### Step 2: Modal Initialization
- Create modal overlay
- Populate content preview with target text
- Set up preset button grid
- Initialize all event listeners
- Show modal with smooth animation

### Step 3: User Interaction Handling
- Monitor preset button selections
- Track custom instruction input
- Handle RAG checkbox changes
- Enable/disable Apply button based on user actions

### Step 4: Content Processing
- Validate user selections and inputs
- Determine if RAG is needed
- Send request to processing API
- Show appropriate loading states
- Handle success and error responses

### Step 5: Content Replacement
- Replace original content with processed version
- Maintain document formatting and structure
- Show success feedback to user
- Close modal and clean up

## 🎛️ USER EXPERIENCE GUIDELINES

### Visual Feedback Requirements
- Highlight target content (selection or section) when modal opens
- Use different colors for selected text vs auto-selected sections
- Animate button states and modal transitions
- Provide clear loading indicators

### Responsive Design
- Modal should work on desktop, tablet, and mobile
- Preset grid should stack appropriately on smaller screens
- Ensure touch-friendly button sizes
- Handle keyboard navigation properly

### Error Handling
- Show clear error messages for failed operations
- Provide retry options for network issues
- Handle edge cases gracefully (empty content, API failures)
- Never lose user's custom instructions on errors

## 🔧 SECTION DETECTION STRATEGY

### Primary Detection Methods
- Track user's last click or cursor position within document
- Use scroll position to determine visible section
- Monitor focus events on section elements

### Fallback Logic
- If detection fails, use first section in document
- Provide visual feedback showing which section was selected
- Allow user to see and confirm the auto-selected content in modal

### Section Highlighting
- Briefly highlight the auto-selected section (1-2 seconds)
- Use subtle background color or border
- Animate the highlight to draw attention

## 📊 CONTENT VALIDATION

### Input Validation
- Ensure target content exists and isn't empty
- Validate custom instructions for harmful content
- Check content length limits for processing

### Output Validation
- Verify processed content maintains document structure
- Ensure character encoding is preserved
- Validate that essential information isn't lost

## 🎯 SUCCESS CRITERIA

### Functional Requirements
- Modal opens reliably for both selected text and sections
- All presets work correctly with appropriate RAG usage
- Content replacement preserves document integrity
- Error handling prevents data loss

### User Experience Goals
- Intuitive workflow that doesn't require training
- Fast response times for non-RAG operations
- Clear feedback at every step
- Seamless integration with existing document interface

## 🚨 CRITICAL IMPLEMENTATION NOTES

### Always Remember
- Button is NEVER disabled - always functional
- Auto-select sections when no text is selected
- RAG is smart - only use when necessary
- Preserve user's work - never lose custom instructions
- Provide clear visual feedback for all actions

### Performance Considerations
- Lazy load modal components
- Cache section detection results
- Optimize RAG queries to prevent redundant searches
- Use debouncing for real-time input validation

### Accessibility Requirements
- Full keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management in modal

## 📝 API INTEGRATION POINTS

### Suggest Edit Endpoint
- Send target content, preset selection, custom instructions
- Include RAG flag and advanced options
- Handle both success and error responses
- Support progress updates for long operations

### Content Replacement
- Maintain document version control
- Support undo/redo functionality
- Preserve formatting and structure
- Handle concurrent edit conflicts
