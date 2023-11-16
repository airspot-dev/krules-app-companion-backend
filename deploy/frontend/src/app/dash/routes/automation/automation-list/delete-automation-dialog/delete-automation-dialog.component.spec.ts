import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteAutomationDialogComponent } from './delete-automation-dialog.component';

describe('DeleteAutomationDialogComponent', () => {
  let component: DeleteAutomationDialogComponent;
  let fixture: ComponentFixture<DeleteAutomationDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DeleteAutomationDialogComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(DeleteAutomationDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
