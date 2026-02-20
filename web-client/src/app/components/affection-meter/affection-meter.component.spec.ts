import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AffectionMeterComponent } from './affection-meter.component';

describe('AffectionMeterComponent', () => {
  let component: AffectionMeterComponent;
  let fixture: ComponentFixture<AffectionMeterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AffectionMeterComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(AffectionMeterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Color Coding', () => {
    it('should return gray color for stranger level (0-20)', () => {
      component.affectionLevel = 10;
      expect(component.getAffectionColor()).toBe('bg-gray-400');
    });

    it('should return blue color for friend level (21-50)', () => {
      component.affectionLevel = 35;
      expect(component.getAffectionColor()).toBe('bg-blue-500');
    });

    it('should return purple color for close level (51-80)', () => {
      component.affectionLevel = 65;
      expect(component.getAffectionColor()).toBe('bg-purple-500');
    });

    it('should return pink color for attached level (81-100)', () => {
      component.affectionLevel = 90;
      expect(component.getAffectionColor()).toBe('bg-pink-500');
    });
  });

  describe('Stage Description', () => {
    it('should return "Stranger" for level 0-20', () => {
      component.affectionLevel = 15;
      expect(component.getStageDescription()).toBe('Stranger');
    });

    it('should return "Friend" for level 21-50', () => {
      component.affectionLevel = 40;
      expect(component.getStageDescription()).toBe('Friend');
    });

    it('should return "Close" for level 51-80', () => {
      component.affectionLevel = 70;
      expect(component.getStageDescription()).toBe('Close');
    });

    it('should return "Attached" for level 81-100', () => {
      component.affectionLevel = 95;
      expect(component.getStageDescription()).toBe('Attached');
    });
  });

  describe('Heart Icon', () => {
    it('should return white heart for stranger level', () => {
      component.affectionLevel = 10;
      expect(component.getHeartIcon()).toBe('🤍');
    });

    it('should return blue heart for friend level', () => {
      component.affectionLevel = 30;
      expect(component.getHeartIcon()).toBe('💙');
    });

    it('should return purple heart for close level', () => {
      component.affectionLevel = 60;
      expect(component.getHeartIcon()).toBe('💜');
    });

    it('should return sparkling heart for attached level', () => {
      component.affectionLevel = 85;
      expect(component.getHeartIcon()).toBe('💖');
    });
  });

  describe('Boundary Values', () => {
    it('should handle affection level 0', () => {
      component.affectionLevel = 0;
      expect(component.getAffectionColor()).toBe('bg-gray-400');
      expect(component.getStageDescription()).toBe('Stranger');
    });

    it('should handle affection level 100', () => {
      component.affectionLevel = 100;
      expect(component.getAffectionColor()).toBe('bg-pink-500');
      expect(component.getStageDescription()).toBe('Attached');
    });

    it('should handle boundary at 21 (Friend threshold)', () => {
      component.affectionLevel = 21;
      expect(component.getAffectionColor()).toBe('bg-blue-500');
      expect(component.getStageDescription()).toBe('Friend');
    });

    it('should handle boundary at 51 (Close threshold)', () => {
      component.affectionLevel = 51;
      expect(component.getAffectionColor()).toBe('bg-purple-500');
      expect(component.getStageDescription()).toBe('Close');
    });

    it('should handle boundary at 81 (Attached threshold)', () => {
      component.affectionLevel = 81;
      expect(component.getAffectionColor()).toBe('bg-pink-500');
      expect(component.getStageDescription()).toBe('Attached');
    });
  });
});
