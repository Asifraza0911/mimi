import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ChatService, ChatRequest, ChatResponse } from './chat.service';
import { environment } from '../../environments/environment';

describe('ChatService', () => {
  let service: ChatService;
  let httpMock: HttpTestingController;
  const apiUrl = `${environment.apiUrl}/chat`;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ChatService]
    });
    service = TestBed.inject(ChatService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should send a message with correct request format', () => {
    const userId = 'test-user-123';
    const message = 'Hello Mimi!';
    const mockResponse: ChatResponse = {
      reply: 'H-hey! What do you want?',
      affection_level: 15,
      mood: 'neutral'
    };

    service.sendMessage(userId, message).subscribe(response => {
      expect(response).toEqual(mockResponse);
      expect(response.reply).toBe('H-hey! What do you want?');
      expect(response.affection_level).toBe(15);
      expect(response.mood).toBe('neutral');
    });

    const req = httpMock.expectOne(apiUrl);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      user_id: userId,
      message: message,
      platform: 'web'
    } as ChatRequest);

    req.flush(mockResponse);
  });

  it('should set platform to "web"', () => {
    const userId = 'test-user-456';
    const message = 'Test message';

    service.sendMessage(userId, message).subscribe();

    const req = httpMock.expectOne(apiUrl);
    expect(req.request.body.platform).toBe('web');
    
    req.flush({
      reply: 'Test reply',
      affection_level: 20,
      mood: 'happy'
    });
  });

  it('should handle HTTP errors gracefully', () => {
    const userId = 'test-user-789';
    const message = 'Error test';
    const errorMessage = 'Server error';

    service.sendMessage(userId, message).subscribe({
      next: () => fail('should have failed with an error'),
      error: (error) => {
        expect(error).toBeTruthy();
        expect(error.message).toContain('Server error');
      }
    });

    const req = httpMock.expectOne(apiUrl);
    req.flush(errorMessage, { status: 500, statusText: 'Internal Server Error' });
  });

  it('should handle network errors', () => {
    const userId = 'test-user-999';
    const message = 'Network error test';

    service.sendMessage(userId, message).subscribe({
      next: () => fail('should have failed with an error'),
      error: (error) => {
        expect(error).toBeTruthy();
        expect(error.message).toContain('Network error');
      }
    });

    const req = httpMock.expectOne(apiUrl);
    req.error(new ProgressEvent('error'));
  });

  it('should extract error message from backend reply field', () => {
    const userId = 'test-user-error';
    const message = 'Backend error test';
    const backendErrorResponse = {
      reply: 'I-I\'m not feeling well right now...',
      affection_level: 10,
      mood: 'sad'
    };

    service.sendMessage(userId, message).subscribe({
      next: () => fail('should have failed with an error'),
      error: (error) => {
        expect(error).toBeTruthy();
        expect(error.message).toBe(backendErrorResponse.reply);
      }
    });

    const req = httpMock.expectOne(apiUrl);
    req.flush(backendErrorResponse, { status: 500, statusText: 'Internal Server Error' });
  });

  it('should return Observable<ChatResponse>', (done) => {
    const userId = 'test-user-observable';
    const message = 'Observable test';
    const mockResponse: ChatResponse = {
      reply: 'Test response',
      affection_level: 25,
      mood: 'flustered'
    };

    const result = service.sendMessage(userId, message);
    
    expect(result).toBeTruthy();
    result.subscribe(response => {
      expect(response).toEqual(mockResponse);
      done();
    });

    const req = httpMock.expectOne(apiUrl);
    req.flush(mockResponse);
  });
});
