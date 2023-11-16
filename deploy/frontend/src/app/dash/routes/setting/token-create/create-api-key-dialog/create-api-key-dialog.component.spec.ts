import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateApiKeyDialogComponent } from './create-api-key-dialog.component';

describe('CreateApiKeyDialogComponent', () => {
  let component: CreateApiKeyDialogComponent;
  let fixture: ComponentFixture<CreateApiKeyDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateApiKeyDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateApiKeyDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
