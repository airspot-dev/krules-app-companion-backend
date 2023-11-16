import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LayoutRuleListComponent } from './layout-rule-list.component';

describe('LayoutRuleListComponent', () => {
  let component: LayoutRuleListComponent;
  let fixture: ComponentFixture<LayoutRuleListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LayoutRuleListComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LayoutRuleListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
