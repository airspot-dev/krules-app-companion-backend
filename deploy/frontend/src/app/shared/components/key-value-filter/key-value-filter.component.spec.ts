import { ComponentFixture, TestBed } from '@angular/core/testing';

import { KeyValueFilterComponent } from './key-value-filter.component';

describe('KeyValueFilterComponent', () => {
  let component: KeyValueFilterComponent;
  let fixture: ComponentFixture<KeyValueFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ KeyValueFilterComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(KeyValueFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
