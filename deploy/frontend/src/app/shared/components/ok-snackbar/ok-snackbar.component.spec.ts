import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OkSnackbarComponent } from './ok-snackbar.component';

describe('OkSnackbarComponent', () => {
  let component: OkSnackbarComponent;
  let fixture: ComponentFixture<OkSnackbarComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ OkSnackbarComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OkSnackbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
