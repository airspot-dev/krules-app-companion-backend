import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ColumnDateFilterComponent } from './column-date-filter.component';

describe('ColumnDateFilterComponent', () => {
  let component: ColumnDateFilterComponent;
  let fixture: ComponentFixture<ColumnDateFilterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ColumnDateFilterComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ColumnDateFilterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
