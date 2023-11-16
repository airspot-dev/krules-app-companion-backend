import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AutomationListComponent } from './automation-list.component';

describe('AutomationListComponent', () => {
  let component: AutomationListComponent;
  let fixture: ComponentFixture<AutomationListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AutomationListComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AutomationListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
