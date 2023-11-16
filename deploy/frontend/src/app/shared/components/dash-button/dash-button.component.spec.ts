import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DashButtonComponent } from './dash-button.component';

describe('DashButtonComponent', () => {
  let component: DashButtonComponent;
  let fixture: ComponentFixture<DashButtonComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DashButtonComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
