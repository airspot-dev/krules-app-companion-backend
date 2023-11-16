import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LayoutRuleCreateComponent } from './layout-rule-create.component';

describe('LayoutRuleCreateComponent', () => {
  let component: LayoutRuleCreateComponent;
  let fixture: ComponentFixture<LayoutRuleCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ LayoutRuleCreateComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LayoutRuleCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
