# Editor Components Documentation

## Components Overview

### 📝 DocumentEditor
Main editor component that renders dynamic sections with text and tables.

**Features:**
- ✅ Dynamic section rendering based on type ('text' | 'table')
- ✅ Citation support with clickable links
- ✅ Default content when no sections provided
- ✅ Full TypeScript support

**Props:**
```typescript
interface DocumentEditorProps {
  sections?: Section[];
  citations?: Citation[];
}
```

### 📊 SpecificationTable
Renders pharmaceutical specification data in a structured table format.

**Features:**
- ✅ Hardcoded specification data for drug substances
- ✅ Support for multi-line acceptance criteria
- ✅ Professional pharmaceutical table styling
- ✅ Responsive table layout

### 🔗 TextWithCitations
Renders text content with interactive citation links.

**Features:**
- ✅ Automatic citation link detection `[1]`, `[2]`, etc.
- ✅ Clickable citation numbers with tooltips
- ✅ Hover effects and styling
- ✅ Reference lookup from citations array

**Props:**
```typescript
interface TextWithCitationsProps {
  content: string;
  citations?: Citation[];
}
```

## Data Structures

### Section Interface
```typescript
interface Section {
  id: string;
  title: string;
  content: string;
  type: 'text' | 'table';
}
```

### Citation Interface
```typescript
interface Citation {
  id: string;
  text: string;
  reference: string;
}
```

### SpecRow Interface (SpecificationTable)
```typescript
interface SpecRow {
  test: string;
  method: string;
  acceptanceCriteria: string;
}
```

## Sample Data

The `sampleData.ts` file provides example data:
- **sampleCitations**: Array of citation objects with references
- **sampleSections**: Mixed content sections (text and table types)

## Usage Example

```typescript
import { DocumentEditor } from './components/Editor';
import { sampleCitations, sampleSections } from './components/Editor/sampleData';

<DocumentEditor 
  sections={sampleSections} 
  citations={sampleCitations} 
/>
```

## Styling

Citations are styled with:
- Red color (`#ef4444`) matching the app theme
- Underline text decoration
- Hover effects with darker red (`#dc2626`)
- Smooth transitions

## Integration

The DocumentEditor replaces the previous MainContent component and integrates seamlessly with:
- Layout components (Header, Sidebar, RightPanel)
- Existing CSS styling system
- Hot module replacement development workflow
