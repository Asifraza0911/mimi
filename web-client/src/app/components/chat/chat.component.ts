import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked, Inject, PLATFORM_ID } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService, ChatResponse } from '../../services/chat.service';
import { AffectionMeterComponent } from '../affection-meter/affection-meter.component';

/**
 * Message interface for chat history
 */
interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

/**
 * Chat component for interacting with Mimi, the AI Waifu.
 * 
 * This component provides the main chat interface where users can:
 * - Send messages to Mimi
 * - View conversation history
 * - See Mimi's current mood and affection level
 * - Experience auto-scrolling to latest messages
 */
@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, AffectionMeterComponent],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messageContainer') private messageContainer!: ElementRef;

  // User identification
  userId: string = '';
  
  // Chat state
  messages: Message[] = [];
  currentMessage: string = '';
  isLoading: boolean = false;
  errorMessage: string = '';
  
  // AI state
  currentMood: string = 'neutral';
  affectionLevel: number = 10;
  
  // Auto-scroll control
  private shouldScrollToBottom: boolean = false;
  
  // Platform detection
  private isBrowser: boolean;

  constructor(
    private chatService: ChatService,
    @Inject(PLATFORM_ID) platformId: Object
  ) {
    this.isBrowser = isPlatformBrowser(platformId);
  }

  ngOnInit(): void {
    // Generate or retrieve user_id from localStorage (only in browser)
    this.userId = this.getUserId();
    
    // Add welcome message
    this.messages.push({
      role: 'assistant',
      content: 'Hmph! You finally decided to talk to me? W-well, it\'s not like I was waiting or anything...',
      timestamp: new Date()
    });
  }

  ngAfterViewChecked(): void {
    // Auto-scroll to bottom when new messages arrive
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  /**
   * Get or generate a unique user ID.
   * Uses a fixed Discord user ID to share memories across platforms.
   */
  private getUserId(): string {
    if (!this.isBrowser) {
      // Return a temporary ID for SSR
      return 'ssr-temp-user';
    }
    
    // Use fixed Discord user ID to share memories across web and Discord
    const discordUserId = '1076883627083837573';
    
    // Store in localStorage for consistency
    localStorage.setItem('waifu_user_id', discordUserId);
    
    return discordUserId;
  }

  /**
   * Send a message to Mimi.
   */
  sendMessage(): void {
    // Validate input
    if (!this.currentMessage.trim()) {
      return;
    }

    // Clear any previous errors
    this.errorMessage = '';

    // Add user message to history
    const userMessage: Message = {
      role: 'user',
      content: this.currentMessage,
      timestamp: new Date()
    };
    this.messages.push(userMessage);

    // Store message for API call
    const messageToSend = this.currentMessage;
    
    // Clear input field
    this.currentMessage = '';
    
    // Set loading state
    this.isLoading = true;
    this.shouldScrollToBottom = true;

    // Call API
    this.chatService.sendMessage(this.userId, messageToSend).subscribe({
      next: (response: ChatResponse) => {
        // Add AI response to history
        const aiMessage: Message = {
          role: 'assistant',
          content: response.reply,
          timestamp: new Date()
        };
        this.messages.push(aiMessage);

        // Update AI state
        this.currentMood = response.mood;
        this.affectionLevel = response.affection_level;

        // Trigger scroll
        this.shouldScrollToBottom = true;
        this.isLoading = false;
      },
      error: (error: Error) => {
        // Display error message
        this.errorMessage = error.message;
        this.isLoading = false;
        
        // Add error message to chat
        const errorMsg: Message = {
          role: 'assistant',
          content: 'H-hey! Something went wrong... but it\'s not my fault! Try again later, okay?',
          timestamp: new Date()
        };
        this.messages.push(errorMsg);
        this.shouldScrollToBottom = true;
      }
    });
  }

  /**
   * Handle Enter key press in textarea.
   * Send message on Enter, allow Shift+Enter for new lines.
   */
  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  /**
   * Scroll the message container to the bottom.
   */
  private scrollToBottom(): void {
    try {
      if (this.messageContainer) {
        const element = this.messageContainer.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }

  /**
   * Get mood emoji for display.
   */
  getMoodEmoji(): string {
    const moodEmojis: { [key: string]: string } = {
      'happy': '😊',
      'neutral': '😐',
      'sad': '😢',
      'jealous': '😠',
      'angry': '😡',
      'flustered': '😳'
    };
    return moodEmojis[this.currentMood] || '😐';
  }
}
