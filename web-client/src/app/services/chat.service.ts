import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { environment } from '../../environments/environment';

/**
 * Request model for chat API
 */
export interface ChatRequest {
  user_id: string;
  message: string;
  platform: 'web' | 'discord';
}

/**
 * Response model from chat API
 */
export interface ChatResponse {
  reply: string;
  affection_level: number;
  mood: string;
}

/**
 * Chat service for communicating with the AI Waifu backend.
 * 
 * This service handles all HTTP communication with the FastAPI backend,
 * sending user messages and receiving AI responses with emotional state.
 */
@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private readonly apiUrl = `${environment.apiUrl}/chat`;

  constructor(private http: HttpClient) {}

  /**
   * Send a message to the AI and receive a response.
   * 
   * @param userId - Unique identifier for the user
   * @param message - The message text to send
   * @returns Observable<ChatResponse> with reply, affection_level, and mood
   */
  sendMessage(userId: string, message: string): Observable<ChatResponse> {
    const request: ChatRequest = {
      user_id: userId,
      message: message,
      platform: 'web'
    };

    return this.http.post<ChatResponse>(this.apiUrl, request).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Handle HTTP errors gracefully.
   * 
   * @param error - The HTTP error response
   * @returns Observable that throws a user-friendly error message
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred while communicating with the AI.';

    if (error.error instanceof ErrorEvent) {
      // Client-side or network error
      errorMessage = `Network error: ${error.error.message}`;
    } else if (error.status === 0) {
      // Network error (no response from server)
      errorMessage = 'Network error: Unable to connect to the server';
    } else {
      // Backend returned an unsuccessful response code
      errorMessage = `Server error: ${error.status} - ${error.message}`;
      
      // If the backend returned a reply field with an error message, use that
      if (error.error?.reply) {
        errorMessage = error.error.reply;
      }
    }

    console.error('ChatService error:', errorMessage, error);
    return throwError(() => new Error(errorMessage));
  }
}
