import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EventSourcingEditComponent } from './event-sourcing-edit.component';

describe('EventSourcingEditComponent', () => {
  let component: EventSourcingEditComponent;
  let fixture: ComponentFixture<EventSourcingEditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EventSourcingEditComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EventSourcingEditComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
