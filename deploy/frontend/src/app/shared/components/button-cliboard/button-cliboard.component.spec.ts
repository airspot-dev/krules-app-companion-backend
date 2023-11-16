import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ButtonCliboardComponent } from './button-cliboard.component';

describe('ButtonCliboardComponent', () => {
  let component: ButtonCliboardComponent;
  let fixture: ComponentFixture<ButtonCliboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ButtonCliboardComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ButtonCliboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
