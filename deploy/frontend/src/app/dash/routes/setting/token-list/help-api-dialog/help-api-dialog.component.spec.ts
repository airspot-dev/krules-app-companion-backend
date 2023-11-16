import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HelpApiDialogComponent } from './help-api-dialog.component';

describe('HelpApiDialogComponent', () => {
  let component: HelpApiDialogComponent;
  let fixture: ComponentFixture<HelpApiDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HelpApiDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HelpApiDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
