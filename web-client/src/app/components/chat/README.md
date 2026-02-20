# Chat Component

## Overview

The Chat Component is the main UI for user interaction with Mimi, the AI Waifu. It provides a complete chat interface with message history, mood display, and affection tracking.

## Features

### Core Functionality
- **Message History**: Displays conversation between user and Mimi with timestamps
- **Send Messages**: Input field with Enter-to-send functionality (Shift+Enter for new lines)
- **Real-time Updates**: Shows Mimi's current mood and affection level
- **Auto-scroll**: Automatically scrolls to show latest messages
- **User Identification**: Generates and persists user_id in localStorage

### UI Components

#### Header
- Application title
- Current mood emoji (😊 😐 😢 😠 😡 😳)
- Affection level (0-100) with color coding:
  - Gray (0-19): Stranger
  - Blue (20-49): Friend
  - Purple (50-79): Close
  - Pink (80-100): Attached

#### Message Container
- Scrollable message history
- User messages (right-aligned, purple)
- AI messages (left-aligned, white with pink border)
- Loading indicator (animated dots)
- Timestamps for each message

#### Input Area
- Multi-line textarea
- Send button (disabled when empty or loading)
- Keyboard shortcuts:
  - Enter: Send message
  - Shift+Enter: New line

### Error Handling
- Network errors displayed in red banner
- Fallback error messages from AI
- Dismissible error notifications

## Technical Details

### Dependencies
- `@angular/core`: Component framework
- `@angular/common`: Common directives (NgFor, NgIf, NgClass)
- `@angular/forms`: Two-way data binding (FormsModule)
- `ChatService`: API communication service

### SSR Support
- Platform detection using `PLATFORM_ID`
- Conditional localStorage access (browser-only)
- Temporary user ID for server-side rendering

### Styling
- TailwindCSS for responsive design
- Custom scrollbar styling
- Smooth animations for messages
- Mobile-responsive layout

## Usage

### In App Component
```typescript
import { ChatComponent } from './components/chat/chat.component';

@Component({
  imports: [ChatComponent],
  // ...
})
```

### In Template
```html
<app-chat></app-chat>
```

## API Integration

The component uses `ChatService` to communicate with the backend:

```typescript
interface ChatRequest {
  user_id: string;
  message: string;
  platform: 'web' | 'discord';
}

interface ChatResponse {
  reply: string;
  affection_level: number;
  mood: string;
}
```

## Testing

Unit tests are provided in `chat.component.spec.ts`:
- Component creation
- User ID generation
- Message sending
- Error handling
- Keyboard shortcuts
- Mood and affection display

Run tests:
```bash
npm test
```

## Requirements Satisfied

- **Requirement 7.3**: Chat interface with message history ✓
- **Requirement 7.5**: Display reply, mood, and affection_level ✓
- User ID generation/persistence ✓
- Auto-scroll functionality ✓
- Send message functionality ✓

## Future Enhancements

Potential improvements:
- Message persistence (save to localStorage)
- Typing indicators
- Message reactions
- Voice input
- Image/emoji support
- Dark mode
- Customizable themes
