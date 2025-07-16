# Citation Components Documentation

## Components Overview

### 🔗 CitationPopover
Interactive popover component that displays citation details when clicked.

**Features:**
- ✅ **Click to open/close** popover with citation details
- ✅ **Overlay backdrop** for easy dismissal
- ✅ **Professional styling** with shadow and border
- ✅ **Source file information** with page numbers
- ✅ **"View Source" button** for navigation (TODO implementation)
- ✅ **Lucide React icons** (FileText, ExternalLink)

**Props:**
```typescript
interface CitationPopoverProps {
  citation: Citation;
  number: number; // Display number [1], [2], etc.
}
```

### 📝 TextWithCitations (Enhanced)
Renders text content with interactive citation popovers.

**Features:**
- ✅ **Advanced citation detection** using regex
- ✅ **Interactive popover citations** instead of simple links
- ✅ **Default citations** when none provided
- ✅ **Professional pharmaceutical references**
- ✅ **Seamless text rendering** with citation integration

**Props:**
```typescript
interface TextWithCitationsProps {
  content: string;
  citations: Citation[];
}
```

## Data Structures

### Citation Interface (Enhanced)
```typescript
interface Citation {
  id: number;          // Numeric ID for ordering
  text: string;        // Citation description/title
  source: string;      // Source filename or document
  page: number;        // Page number in source
  sourceFileId?: string; // Optional file ID for navigation
}
```

## Key Improvements Over Previous Version

### 🆚 **Enhanced vs Original TextWithCitations:**

| Feature | Original | Enhanced |
|---------|----------|----------|
| Citation Display | Simple underlined links | Interactive popovers |
| Citation Info | Tooltip with title only | Full details with source & page |
| User Interaction | Hover only | Click to open/close |
| Visual Design | Basic styling | Professional popover with shadow |
| Source Navigation | None | "View Source" button |
| Data Structure | Simple id/text/reference | Complete with source/page info |

## Sample Data

### Default Citations:
```typescript
const defaultCitations = [
  {
    id: 1,
    text: "Manufacturing process validated according to ICH Q7",
    source: "process_validation.pdf",
    page: 24
  },
  {
    id: 2,
    text: "ICH Q6A: Specifications: Test Procedures and Acceptance Criteria",
    source: "ICH_Q6A_Guideline.pdf",
    page: 1
  }
];
```

## Usage Example

```typescript
import { TextWithCitations } from './components/Citations';

const content = "The manufacturing process [1] follows ICH guidelines [2].";
const citations = [/* your citation data */];

<TextWithCitations content={content} citations={citations} />
```

## Styling

### Citation Markers:
- Blue color (`#3b82f6`) for visibility
- Bold, 12px font size
- Hover effects with darker blue
- No text decoration for clean look

### Popovers:
- White background with subtle border
- Professional shadow (`shadow-lg`)
- Fixed width (256px) for consistency
- Z-index 20 for proper layering
- Responsive positioning (bottom-full, centered)

## Integration Notes

- ✅ **Replaces** the original Editor/TextWithCitations
- ✅ **Maintains compatibility** with DocumentEditor
- ✅ **Enhanced user experience** with interactive citations
- ✅ **Professional appearance** suitable for regulatory documents
- ✅ **Extensible** for future source file navigation features

## TODO Implementation

- [ ] **Source file navigation** - Jump to specific page in PDF/documents
- [ ] **Citation management** - Add/edit/delete citations
- [ ] **Citation formatting** - Different styles (APA, MLA, etc.)
- [ ] **Export functionality** - Generate citation bibliography
