import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Affection Meter Component
 * 
 * A reusable component that visualizes the user's relationship level with Mimi.
 * Displays a progress bar with color coding based on relationship stages.
 * 
 * Usage:
 * <app-affection-meter [affectionLevel]="75"></app-affection-meter>
 */
@Component({
  selector: 'app-affection-meter',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './affection-meter.component.html',
  styleUrls: ['./affection-meter.component.css']
})
export class AffectionMeterComponent {
  /**
   * Affection level (0-100)
   * Represents the strength of the relationship with Mimi
   */
  @Input() affectionLevel: number = 0;

  /**
   * Get the color class based on affection level
   * Color coding represents relationship stages:
   * - Gray (0-20): Stranger
   * - Blue (21-50): Friend
   * - Purple (51-80): Close
   * - Pink (81-100): Attached
   */
  getAffectionColor(): string {
    if (this.affectionLevel >= 81) return 'bg-pink-500';
    if (this.affectionLevel >= 51) return 'bg-purple-500';
    if (this.affectionLevel >= 21) return 'bg-blue-500';
    return 'bg-gray-400';
  }

  /**
   * Get the relationship stage description
   */
  getStageDescription(): string {
    if (this.affectionLevel >= 81) return 'Attached';
    if (this.affectionLevel >= 51) return 'Close';
    if (this.affectionLevel >= 21) return 'Friend';
    return 'Stranger';
  }

  /**
   * Get the heart icon based on affection level
   */
  getHeartIcon(): string {
    if (this.affectionLevel >= 81) return '💖'; // Sparkling heart
    if (this.affectionLevel >= 51) return '💜'; // Purple heart
    if (this.affectionLevel >= 21) return '💙'; // Blue heart
    return '🤍'; // White heart
  }
}
