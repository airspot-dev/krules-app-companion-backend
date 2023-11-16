import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DataBackButtonComponent } from './data-back-button.component';

describe('DataBackButtonComponent', () => {
  let component: DataBackButtonComponent;
  let fixture: ComponentFixture<DataBackButtonComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DataBackButtonComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DataBackButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
