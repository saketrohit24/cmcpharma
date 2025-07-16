# Layout Components Structure

## Components Created

### 📁 Layout Components
- **`src/components/Layout/Header.tsx`** - Main header with tabs and navigation
- **`src/components/Layout/Sidebar.tsx`** - File structure navigation with collapsible folders
- **`src/components/Layout/RightPanel.tsx`** - Action buttons and chat integration
- **`src/components/Layout/index.ts`** - Clean exports for Layout components

### 💬 Chat Components
- **`src/components/Chat/ChatBox.tsx`** - Interactive chat interface
- **`src/components/Chat/index.ts`** - Clean exports for Chat components

## Key Features

### Header Component
- ✅ Dynamic tab management with state
- ✅ Add new tabs functionality
- ✅ Active tab highlighting
- ✅ Document info display
- ✅ Back button with Lucide icon

### Sidebar Component
- ✅ Hierarchical file structure
- ✅ Collapsible folders with Lucide icons
- ✅ Dynamic expand/collapse state
- ✅ Nested file rendering with proper indentation
- ✅ File and folder type differentiation

### RightPanel Component
- ✅ Action buttons with icons
- ✅ Conditional chat display
- ✅ Template generation button
- ✅ Info box when chat is hidden

### ChatBox Component
- ✅ Message input and submission
- ✅ Message history display
- ✅ Placeholder when empty
- ✅ Send button with icon

## Usage

```typescript
import { Header, Sidebar, RightPanel } from './components/Layout';
import { ChatBox } from './components/Chat';

// Components are fully self-contained with their own state management
```

## TypeScript Interfaces

- **Tab**: Manages tab data structure
- **FileItem**: Handles file/folder hierarchy
- All components are fully typed with React.FC
