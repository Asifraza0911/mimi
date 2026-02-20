import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ChatComponent } from './chat.component';
import { ChatService } from '../../services/chat.service';
import { of, throwError } from 'rxjs';

describe('ChatComponent', () => {
  let component: ChatComponent;
  let fixture: ComponentFixture<ChatComponent>;
  let chatService: jasmine.SpyObj<ChatService>;

  beforeEach(async () => {
    const chatServiceSpy = jasmine.createSpyObj('ChatService', ['sendMessage']);

    await TestBed.configureTestingModule({
      imports: [ChatComponent, HttpClientTestingModule],
      providers: [
        { provide: ChatService, useValue: chatServiceSpy }
      ]
    }).compileComponents();

    chatService = TestBed.inject(ChatService) as jasmine.SpyObj<ChatService>;
    fixture = TestBed.createComponent(ChatComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should generate or retrieve user ID on init', () => {
    expect(component.userId).toBeTruthy();
    expect(component.userId.length).toBeGreaterThan(0);
  });

  it('should have a welcome message on init', () => {
    expect(component.messages.length).toBe(1);
    expect(component.messages[0].role).toBe('assistant');
  });

  it('should not send empty messages', () => {
    component.currentMessage = '   ';
    component.sendMessage();
    
    expect(chatService.sendMessage).not.toHaveBeenCalled();
  });

  it('should send message and update chat history', (done) => {
    const mockResponse = {
      reply: 'Test reply',
      affection_level: 15,
      mood: 'happy'
    };
    
    chatService.sendMessage.and.returnValue(of(mockResponse));
    
    component.currentMessage = 'Hello';
    const initialMessageCount = component.messages.length;
    
    component.sendMessage();
    
    // With synchronous observable (of()), the response is processed immediately
    // So we check the final state directly
    setTimeout(() => {
      expect(component.messages.length).toBe(initialMessageCount + 2);
      expect(component.messages[initialMessageCount].content).toBe('Hello');
      expect(component.messages[initialMessageCount].role).toBe('user');
      expect(component.messages[initialMessageCount + 1].content).toBe('Test reply');
      expect(component.messages[initialMessageCount + 1].role).toBe('assistant');
      expect(component.affectionLevel).toBe(15);
      expect(component.currentMood).toBe('happy');
      done();
    }, 0);
  });

  it('should handle API errors gracefully', (done) => {
    const errorMessage = 'Network error';
    chatService.sendMessage.and.returnValue(
      throwError(() => new Error(errorMessage))
    );
    
    component.currentMessage = 'Hello';
    const initialMessageCount = component.messages.length;
    
    component.sendMessage();
    
    setTimeout(() => {
      expect(component.errorMessage).toBe(errorMessage);
      expect(component.isLoading).toBe(false);
      expect(component.messages.length).toBe(initialMessageCount + 2); // User message + error message
      done();
    }, 100);
  });

  it('should clear input after sending message', () => {
    chatService.sendMessage.and.returnValue(of({
      reply: 'Test',
      affection_level: 10,
      mood: 'neutral'
    }));
    
    component.currentMessage = 'Hello';
    component.sendMessage();
    
    expect(component.currentMessage).toBe('');
  });

  it('should return correct mood emoji', () => {
    component.currentMood = 'happy';
    expect(component.getMoodEmoji()).toBe('😊');
    
    component.currentMood = 'sad';
    expect(component.getMoodEmoji()).toBe('😢');
    
    component.currentMood = 'angry';
    expect(component.getMoodEmoji()).toBe('😡');
  });

  it('should send message on Enter key press', () => {
    spyOn(component, 'sendMessage');
    
    const event = new KeyboardEvent('keypress', { key: 'Enter', shiftKey: false });
    spyOn(event, 'preventDefault');
    
    component.onKeyPress(event);
    
    expect(event.preventDefault).toHaveBeenCalled();
    expect(component.sendMessage).toHaveBeenCalled();
  });

  it('should not send message on Shift+Enter', () => {
    spyOn(component, 'sendMessage');
    
    const event = new KeyboardEvent('keypress', { key: 'Enter', shiftKey: true });
    
    component.onKeyPress(event);
    
    expect(component.sendMessage).not.toHaveBeenCalled();
  });
});
