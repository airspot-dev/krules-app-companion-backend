import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteApiKeyDialogComponent } from './delete-api-key-dialog.component';

describe('DeleteApiKeyDialogComponent', () => {
  let component: DeleteApiKeyDialogComponent;
  let fixture: ComponentFixture<DeleteApiKeyDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeleteApiKeyDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DeleteApiKeyDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
